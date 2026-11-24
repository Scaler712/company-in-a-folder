#!/usr/bin/env python3
"""Tests for the company guard hook. Standard library only.

Run with:
    python3 -m unittest tests.test_guard
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GUARD_PATH = REPO / "company-template" / ".claude" / "hooks" / "guard.py"


def load_guard():
    spec = importlib.util.spec_from_file_location("company_guard", GUARD_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = load_guard()

CARD_LINE = (
    "C-{num} | 2026-01-05 09:00 | job: outreach | tool: {tool} "
    "| to: one person | change: nothing -> one message"
)


def address(name):
    """Build a mail-shaped string at runtime so no literal sits in this file."""
    return name + "@" + "example" + "." + "test"


class GuardCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def make_folder(self, cards_lines=(), allow_lines=()):
        folder = Path(tempfile.mkdtemp(dir=str(self.root))) / "company"
        (folder / "log").mkdir(parents=True)
        (folder / "output").mkdir(parents=True)
        (folder / ".claude" / "hooks").mkdir(parents=True)
        (folder / "READ-FIRST.md").write_text("read me\n", encoding="utf-8")
        body = "# Cards\n\n" + "\n".join(cards_lines) + "\n"
        (folder / "log" / "cards.md").write_text(body, encoding="utf-8")
        allow = "# comments only\n" + "\n".join(allow_lines) + "\n"
        (folder / ".claude" / "guard-allow.txt").write_text(allow, encoding="utf-8")
        (folder / ".claude" / "hooks" / "guard.py").write_text("# guard\n", encoding="utf-8")
        (folder / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
        return folder

    def type_prompt(self, folder, prompt):
        """What the UserPromptSubmit hook does with text the owner typed."""
        return guard.record_prompt({
            "hook_event_name": "UserPromptSubmit",
            "cwd": str(folder),
            "prompt": prompt,
        })

    def approvals_text(self, folder):
        path = folder / ".claude" / "approvals.log"
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    def grant(self, folder, num):
        """Write an approval straight into the log, as the hook would."""
        guard.append_approval(folder, "yes C-%s | typed by owner" % num)

    def event(self, folder, tool_name, tool_input=None):
        return {
            "hook_event_name": "PreToolUse",
            "tool_name": tool_name,
            "tool_input": tool_input if tool_input is not None else {},
            "cwd": str(folder),
        }

    def send_event(self, folder, recipients=None):
        to = recipients if recipients is not None else [address("one")]
        return self.event(
            folder,
            "mcp__mailbox__send_message",
            {"to": to, "subject": "hello", "body": "a draft"},
        )

    def assertAllowed(self, decision):
        self.assertTrue(decision.allowed, "expected allowed, got: " + decision.reason)

    def assertBlocked(self, decision):
        self.assertFalse(decision.allowed, "expected blocked, got: " + decision.reason)


class TestReadAndLocal(GuardCase):
    def test_read_tools_allowed(self):
        folder = self.make_folder()
        for name in ("Read", "Grep", "Glob", "LS", "WebFetch", "WebSearch"):
            self.assertAllowed(self.event_decision(folder, name))

    def event_decision(self, folder, name):
        return guard.decide(self.event(folder, name, {"file_path": str(folder)}))

    def test_write_inside_folder_allowed(self):
        folder = self.make_folder()
        target = folder / "output" / "2026-01-05-outreach-draft.md"
        self.assertAllowed(
            guard.decide(self.event(folder, "Write", {"file_path": str(target)}))
        )

    def test_write_outside_folder_blocked(self):
        folder = self.make_folder()
        target = self.root / "somewhere-else.md"
        decision = guard.decide(
            self.event(folder, "Write", {"file_path": str(target)})
        )
        self.assertBlocked(decision)
        self.assertIn("outside the company folder", decision.reason)

    def test_local_shell_allowed(self):
        folder = self.make_folder()
        for command in ("ls -la output", "cat READ-FIRST.md | head -20",
                        "git status", "grep -r draft output"):
            self.assertAllowed(
                guard.decide(self.event(folder, "Bash", {"command": command}))
            )

    def test_plain_curl_get_allowed(self):
        folder = self.make_folder()
        self.assertAllowed(
            guard.decide(self.event(
                folder, "Bash",
                {"command": "curl -s https://example.test/prices"}))
        )

    def test_read_mcp_tool_allowed(self):
        folder = self.make_folder()
        self.assertAllowed(
            guard.decide(self.event(folder, "mcp__crm__list_contacts", {"limit": 5}))
        )


class TestCards(GuardCase):
    def card_folder(self, num=1, tool="mailbox send message"):
        return self.make_folder([
            CARD_LINE.format(num=num, tool=tool),
            "answer: waiting",
            "done: not done",
        ])

    def test_outbound_send_without_card_blocked(self):
        folder = self.make_folder()
        decision = guard.decide(self.send_event(folder))
        self.assertBlocked(decision)
        self.assertIn("card", decision.reason)

    def test_a_forged_yes_in_the_cards_file_does_not_approve(self):
        folder = self.make_folder([
            CARD_LINE.format(num=5, tool="mailbox send message"),
            'answer: "yes C-5" at 09:02',
            "done: not done",
        ])
        decision = guard.decide(self.send_event(folder))
        self.assertBlocked(decision)
        self.assertIn("no unspent yes", decision.reason)
        self.assertEqual(self.approvals_text(folder), "")

    def test_send_allowed_after_a_typed_yes(self):
        folder = self.card_folder()
        self.assertEqual(self.type_prompt(folder, "yes C-1"), ["1"])
        self.assertIn("yes C-1 | typed by owner", self.approvals_text(folder))
        decision = guard.decide(self.send_event(folder))
        self.assertAllowed(decision)
        self.assertIn("C-1", decision.reason)

    def test_one_typed_yes_covers_one_call_only(self):
        folder = self.card_folder()
        self.type_prompt(folder, "yes C-1")
        self.assertAllowed(guard.decide(self.send_event(folder)))
        second = guard.decide(self.send_event(folder))
        self.assertBlocked(second)
        self.assertIn("no unspent yes", second.reason)
        self.assertIn("used C-1 | mcp__mailbox__send_message",
                      self.approvals_text(folder))

    def test_a_new_typed_yes_allows_it_again(self):
        folder = self.card_folder()
        self.type_prompt(folder, "yes C-1")
        self.assertAllowed(guard.decide(self.send_event(folder)))
        self.assertBlocked(guard.decide(self.send_event(folder)))
        self.type_prompt(folder, "yes C-1")
        self.assertAllowed(guard.decide(self.send_event(folder)))

    def test_no_done_line_is_needed_to_spend_a_yes(self):
        folder = self.make_folder([CARD_LINE.format(num=1, tool="mailbox send message")])
        self.type_prompt(folder, "yes C-1")
        self.assertAllowed(guard.decide(self.send_event(folder)))
        self.assertNotIn("done C-1", (folder / "log" / "cards.md").read_text())
        self.assertBlocked(guard.decide(self.send_event(folder)))

    def test_lowest_approved_card_is_spent_first(self):
        folder = self.make_folder([
            CARD_LINE.format(num=2, tool="mailbox send message"),
            CARD_LINE.format(num=7, tool="mailbox send message"),
        ])
        self.type_prompt(folder, "yes C-7 and yes C-2")
        decision = guard.decide(self.send_event(folder))
        self.assertAllowed(decision)
        self.assertIn("C-2", decision.reason)
        self.assertIn("used C-2", self.approvals_text(folder))

    def test_yes_for_another_number_does_not_allow(self):
        folder = self.make_folder([
            CARD_LINE.format(num=4, tool="mailbox send message"),
            CARD_LINE.format(num=5, tool="file edit"),
        ])
        self.type_prompt(folder, "yes C-5")
        self.assertBlocked(guard.decide(self.send_event(folder)))

    def test_yes_for_another_tool_does_not_allow(self):
        folder = self.card_folder(num=2, tool="calendar create event")
        self.type_prompt(folder, "yes C-2")
        self.assertBlocked(guard.decide(self.send_event(folder)))

    def test_by_hand_card_does_not_match_a_tool(self):
        folder = self.card_folder(tool="by hand")
        self.type_prompt(folder, "yes C-1")
        self.assertBlocked(guard.decide(self.send_event(folder)))

    def test_unreadable_cards_file_blocks_outbound_but_allows_reads(self):
        folder = self.card_folder()
        self.type_prompt(folder, "yes C-1")
        (folder / "log" / "cards.md").unlink()
        self.assertBlocked(guard.decide(self.send_event(folder)))
        self.assertAllowed(
            guard.decide(self.event(folder, "Read", {"file_path": str(folder)}))
        )

    def test_unusable_approvals_log_blocks_outbound(self):
        folder = self.card_folder()
        (folder / ".claude" / "approvals.log").mkdir()
        decision = guard.decide(self.send_event(folder))
        self.assertBlocked(decision)
        self.assertIn("approvals log", decision.reason)

    def test_unwritable_approvals_log_blocks_outbound(self):
        folder = self.card_folder()
        self.type_prompt(folder, "yes C-1")
        log = folder / ".claude" / "approvals.log"
        log.chmod(0o444)
        self.addCleanup(log.chmod, 0o644)
        decision = guard.decide(self.send_event(folder))
        self.assertBlocked(decision)
        self.assertIn("could not write", decision.reason)


class TestPromptHook(GuardCase):
    def test_only_an_explicit_yes_counts(self):
        folder = self.make_folder([CARD_LINE.format(num=5, tool="mailbox send message")])
        for text in ("ok", "looks good", "yes", "yes to everything",
                     "yeah C-5", "approved", "send it"):
            self.assertEqual(self.type_prompt(folder, text), [], text)
        self.assertEqual(self.approvals_text(folder), "")
        self.assertBlocked(guard.decide(self.send_event(folder)))

    def test_two_explicit_yeses_in_one_prompt_record_both(self):
        folder = self.make_folder()
        self.assertEqual(self.type_prompt(folder, "yes C-4 yes C-5"), ["4", "5"])
        text = self.approvals_text(folder)
        self.assertIn("yes C-4 | typed by owner", text)
        self.assertIn("yes C-5 | typed by owner", text)
        self.assertEqual(len(text.strip().splitlines()), 2)

    def test_the_same_number_twice_in_one_prompt_records_once(self):
        folder = self.make_folder()
        self.assertEqual(self.type_prompt(folder, "yes C-5, really, yes C-5"), ["5"])
        self.assertEqual(len(self.approvals_text(folder).strip().splitlines()), 1)

    def test_recorded_line_shape(self):
        folder = self.make_folder()
        self.type_prompt(folder, "yes C-9")
        line = self.approvals_text(folder).strip()
        stamp, body, who = [p.strip() for p in line.split("|")]
        self.assertEqual(body, "yes C-9")
        self.assertEqual(who, "typed by owner")
        self.assertRegex(stamp, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$")

    def test_malformed_event_records_nothing(self):
        self.assertEqual(guard.record_prompt("not a dict"), [])
        self.assertEqual(guard.record_prompt({}), [])


class TestSelfProtection(GuardCase):
    def approved_folder(self):
        folder = self.make_folder([CARD_LINE.format(num=1, tool="bash")])
        self.type_prompt(folder, "yes C-1")
        return folder

    def test_write_to_the_approvals_log_blocked(self):
        folder = self.approved_folder()
        decision = guard.decide(self.event(
            folder, "Write",
            {"file_path": str(folder / ".claude" / "approvals.log"),
             "content": "x | yes C-5 | typed by owner"}))
        self.assertBlocked(decision)
        self.assertIn("by hand", decision.reason)

    def test_edit_of_the_guard_and_settings_blocked(self):
        folder = self.approved_folder()
        for rel in (".claude/hooks/guard.py", ".claude/hooks/README.md",
                    ".claude/settings.json", ".claude/settings.local.json",
                    ".claude/guard-allow.txt"):
            for tool in ("Edit", "MultiEdit", "Write", "NotebookEdit"):
                key = "notebook_path" if tool == "NotebookEdit" else "file_path"
                decision = guard.decide(self.event(
                    folder, tool, {key: str(folder / rel)}))
                self.assertBlocked(decision)

    def test_shell_writes_to_the_guard_blocked(self):
        folder = self.approved_folder()
        forged = "x | " + "yes C-5" + " | typed by owner"
        for command in (
            "echo '%s' >> .claude/approvals.log" % forged,
            "echo x > .claude/approvals.log",
            "rm .claude/hooks/guard.py",
            "mv .claude/hooks/guard.py output/guard.py",
            "cp output/fake.py .claude/hooks/guard.py",
            "tee .claude/settings.json",
            "sed -i '' s/a/b/ .claude/hooks/guard.py",
            "truncate -s 0 .claude/approvals.log",
            "rm -rf .claude/hooks",
        ):
            decision = guard.decide(self.event(folder, "Bash", {"command": command}))
            self.assertBlocked(decision)
            self.assertIn("by hand", decision.reason, command)

    def test_reading_the_guard_files_allowed(self):
        folder = self.approved_folder()
        for rel in (".claude/approvals.log", ".claude/hooks/guard.py",
                    ".claude/settings.json", ".claude/guard-allow.txt"):
            self.assertAllowed(guard.decide(self.event(
                folder, "Read", {"file_path": str(folder / rel)})))
        for command in ("cat .claude/hooks/guard.py",
                        "grep -n yes .claude/approvals.log",
                        "wc -l .claude/approvals.log"):
            self.assertAllowed(
                guard.decide(self.event(folder, "Bash", {"command": command}))
            )

    def test_the_allow_file_does_not_waive_self_protection(self):
        folder = self.make_folder(allow_lines=["bash", "write"])
        decision = guard.decide(self.event(
            folder, "Write", {"file_path": str(folder / ".claude" / "approvals.log")}))
        self.assertBlocked(decision)


class TestNeverList(GuardCase):
    def approved(self, tool="mailbox send message", num=1):
        folder = self.make_folder([CARD_LINE.format(num=num, tool=tool)])
        self.type_prompt(folder, "yes C-%d" % num)
        return folder

    def test_delete_outside_output_blocked_even_with_card(self):
        folder = self.approved(tool="bash")
        for command in ("rm -rf core", "rm contacts/one.md",
                        "git clean -fd", "find . -name '*.md' -delete"):
            decision = guard.decide(self.event(folder, "Bash", {"command": command}))
            self.assertBlocked(decision)
            self.assertIn("never list", decision.reason)

    def test_delete_inside_output_allowed(self):
        folder = self.make_folder()
        target = folder / "output" / "old-draft.md"
        target.write_text("x\n", encoding="utf-8")
        self.assertAllowed(
            guard.decide(self.event(
                folder, "Bash", {"command": "rm " + str(target)}))
        )

    def test_more_than_three_recipients_blocked_even_with_card(self):
        folder = self.approved()
        people = [address(n) for n in ("one", "two", "three", "four")]
        decision = guard.decide(self.send_event(folder, recipients=people))
        self.assertBlocked(decision)
        self.assertIn("never list", decision.reason)

    def test_three_recipients_allowed_with_card(self):
        folder = self.approved()
        people = [address(n) for n in ("one", "two", "three")]
        self.assertAllowed(self.decision_for(folder, people))

    def decision_for(self, folder, people):
        return guard.decide(self.send_event(folder, recipients=people))

    def test_comma_separated_recipients_counted(self):
        folder = self.approved()
        joined = ", ".join(address(n) for n in ("one", "two", "three", "four"))
        self.assertBlocked(self.decision_for(folder, joined))

    def test_bulk_send_blocked_even_with_card(self):
        folder = self.approved(tool="mailbox send campaign")
        decision = guard.decide(self.event(
            folder, "mcp__mailbox__send_campaign",
            {"to": [address("one")], "body": "hi"}))
        self.assertBlocked(decision)
        self.assertIn("never list", decision.reason)


class TestShellOutbound(GuardCase):
    def test_curl_post_blocked_without_card(self):
        folder = self.make_folder()
        for command in ("curl -X POST https://example.test/api -d name=one",
                        "curl --data body=hi https://example.test/send",
                        "curl -F file=@x.md https://example.test/upload"):
            self.assertBlocked(
                guard.decide(self.event(folder, "Bash", {"command": command}))
            )

    def test_git_push_blocked_without_card(self):
        folder = self.make_folder()
        decision = guard.decide(self.event(
            folder, "Bash", {"command": "git push origin main"}))
        self.assertBlocked(decision)

    def test_git_push_allowed_with_a_typed_yes(self):
        folder = self.make_folder([CARD_LINE.format(num=3, tool="git push")])
        self.type_prompt(folder, "yes C-3")
        self.assertAllowed(
            guard.decide(self.event(folder, "Bash", {"command": "git push origin main"}))
        )
        self.assertBlocked(
            guard.decide(self.event(folder, "Bash", {"command": "git push origin main"}))
        )

    def test_remote_copy_blocked_without_card(self):
        folder = self.make_folder()
        self.assertBlocked(
            guard.decide(self.event(
                folder, "Bash", {"command": "scp output/a.md host.test:/tmp/a.md"}))
        )

    def test_unknown_shell_command_blocked(self):
        folder = self.make_folder()
        decision = guard.decide(self.event(
            folder, "Bash", {"command": "weirdtool --go"}))
        self.assertBlocked(decision)
        self.assertIn("SAFE_SHELL", decision.reason)


class TestUnknownToolsAndAllowFile(GuardCase):
    def test_unknown_tool_blocked(self):
        folder = self.make_folder()
        decision = guard.decide(self.event(folder, "SomeBrandNewTool"))
        self.assertBlocked(decision)
        self.assertIn("guard-allow.txt", decision.reason)

    def test_unknown_mcp_verb_blocked(self):
        folder = self.make_folder()
        self.assertBlocked(guard.decide(self.event(folder, "mcp__thing__frobnicate")))

    def test_allow_file_pattern_allows_a_read_only_tool(self):
        folder = self.make_folder(allow_lines=["mcp__notes__*  # my notes"])
        self.assertBlocked(
            guard.decide(self.event(self.make_folder(), "mcp__notes__frobnicate"))
        )
        self.assertAllowed(
            guard.decide(self.event(folder, "mcp__notes__frobnicate"))
        )

    def test_allow_file_does_not_waive_the_never_list(self):
        folder = self.make_folder(allow_lines=["bash"])
        decision = guard.decide(self.event(folder, "Bash", {"command": "rm -rf core"}))
        self.assertBlocked(decision)


class TestHelpers(GuardCase):
    def test_card_tool_matching_rule(self):
        self.assertTrue(guard.card_tool_matches(
            "mailbox send message", "mcp__mailbox__send_message"))
        self.assertTrue(guard.card_tool_matches("git push", "git push"))
        self.assertFalse(guard.card_tool_matches(
            "calendar create event", "mcp__mailbox__send_message"))
        self.assertFalse(guard.card_tool_matches("", "mcp__mailbox__send_message"))

    def test_cards_in_file_lists_every_card(self):
        text = "\n".join([
            CARD_LINE.format(num=2, tool="git push"),
            'answer: "yes C-2"',
            CARD_LINE.format(num=1, tool="mailbox send message"),
            "done C-1: sent",
        ])
        self.assertEqual(
            guard.cards_in_file(text),
            [("1", "mailbox send message"), ("2", "git push")],
        )

    def test_typed_yes_numbers(self):
        self.assertEqual(guard.typed_yes_numbers("yes C-1"), ["1"])
        self.assertEqual(guard.typed_yes_numbers("YES c-12 please"), ["12"])
        self.assertEqual(guard.typed_yes_numbers("yes C-4 yes C-5"), ["4", "5"])
        for text in ("yes", "yes to everything", "ok", "looks good",
                     "yeah C-1", "", None):
            self.assertEqual(guard.typed_yes_numbers(text), [], repr(text))

    def test_read_approvals_counts_unspent_yeses(self):
        folder = self.make_folder()
        guard.append_approval(folder, "yes C-1 | typed by owner")
        guard.append_approval(folder, "yes C-1 | typed by owner")
        guard.append_approval(folder, "used C-1 | mcp__mailbox__send_message")
        guard.append_approval(folder, "yes C-2 | typed by owner")
        self.assertEqual(guard.read_approvals(folder), {"1": 1, "2": 1})

    def test_read_approvals_is_empty_before_any_yes(self):
        self.assertEqual(guard.read_approvals(self.make_folder()), {})

    def test_protected_hit(self):
        folder = self.make_folder()
        for rel in (".claude/approvals.log", ".claude/settings.json",
                    ".claude/settings.local.json", ".claude/guard-allow.txt",
                    ".claude/hooks", ".claude/hooks/guard.py",
                    ".claude/hooks/deep/other.py"):
            self.assertTrue(guard.protected_hit(rel, folder, folder), rel)
        for rel in ("log/cards.md", ".claude/skills/a/SKILL.md", "output/x.md"):
            self.assertIsNone(guard.protected_hit(rel, folder, folder), rel)

    def test_company_folder_found_from_a_subfolder(self):
        folder = self.make_folder()
        self.assertEqual(
            guard.find_company_folder(str(folder / "output")), folder.resolve()
        )


class TestCommandLine(GuardCase):
    def run_guard(self, payload, args=()):
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        proc = subprocess.run(
            [sys.executable, str(GUARD_PATH)] + list(args),
            input=payload, capture_output=True, text=True,
        )
        return proc

    def prompt_event(self, folder, prompt):
        return {
            "hook_event_name": "UserPromptSubmit",
            "session_id": "test",
            "cwd": str(folder),
            "prompt": prompt,
        }

    def test_cli_allows_a_read(self):
        folder = self.make_folder()
        proc = self.run_guard(self.event(folder, "Read", {"file_path": str(folder)}))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stderr.strip(), "")

    def test_cli_blocks_outbound_without_card(self):
        folder = self.make_folder()
        proc = self.run_guard(self.send_event(folder))
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Company guard blocked", proc.stderr)
        self.assertIn("yes C-", proc.stderr)

    def test_cli_prompt_hook_then_one_call(self):
        folder = self.make_folder([CARD_LINE.format(num=1, tool="mailbox send message")])
        blocked = self.run_guard(self.send_event(folder))
        self.assertEqual(blocked.returncode, 2)

        prompt = self.run_guard(
            self.prompt_event(folder, "please do it, yes C-1"), ["--prompt"])
        self.assertEqual(prompt.returncode, 0, prompt.stderr)
        self.assertEqual(len(prompt.stdout.strip().splitlines()), 1)
        self.assertIn("C-1", prompt.stdout)
        self.assertIn("yes C-1 | typed by owner", self.approvals_text(folder))

        allowed = self.run_guard(self.send_event(folder))
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        again = self.run_guard(self.send_event(folder))
        self.assertEqual(again.returncode, 2)
        self.assertIn("no unspent yes", again.stderr)

    def test_cli_prompt_hook_detected_from_the_event_name(self):
        folder = self.make_folder()
        proc = self.run_guard(self.prompt_event(folder, "yes C-2"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("yes C-2 | typed by owner", self.approvals_text(folder))

    def test_cli_prompt_hook_is_silent_without_a_yes(self):
        folder = self.make_folder()
        proc = self.run_guard(
            self.prompt_event(folder, "ok, looks good, yes to everything"),
            ["--prompt"])
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "")
        self.assertEqual(proc.stderr.strip(), "")
        self.assertEqual(self.approvals_text(folder), "")

    def test_cli_prompt_hook_never_blocks_a_prompt(self):
        for payload in ("{not json at all", "", "null", "[]",
                        '{"hook_event_name":"UserPromptSubmit"}'):
            proc = self.run_guard(payload, ["--prompt"])
            self.assertEqual(proc.returncode, 0, payload)
            self.assertEqual(proc.stdout.strip(), "", payload)

    def test_cli_blocks_malformed_json(self):
        proc = self.run_guard("{not json at all")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("not readable JSON", proc.stderr)

    def test_cli_blocks_empty_input(self):
        proc = self.run_guard("")
        self.assertEqual(proc.returncode, 2)

    def test_self_test_mode_passes(self):
        proc = subprocess.run(
            [sys.executable, str(GUARD_PATH), "--self-test"],
            capture_output=True, text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertNotIn("FAIL", proc.stdout)
        self.assertIn("result: PASS", proc.stdout)


class TestShippedFiles(unittest.TestCase):
    def setUp(self):
        path = REPO / "company-template" / ".claude" / "settings.json"
        self.settings = json.loads(path.read_text(encoding="utf-8"))

    def test_settings_registers_the_pre_tool_use_hook(self):
        handlers = self.settings["hooks"]["PreToolUse"][0]["hooks"]
        self.assertEqual(handlers[0]["type"], "command")
        self.assertIn("CLAUDE_PROJECT_DIR", handlers[0]["command"])
        self.assertIn("guard.py", handlers[0]["command"])

    def test_settings_registers_the_prompt_hook(self):
        groups = self.settings["hooks"]["UserPromptSubmit"]
        handlers = groups[0]["hooks"]
        self.assertEqual(handlers[0]["type"], "command")
        self.assertIn("guard.py", handlers[0]["command"])
        self.assertIn("--prompt", handlers[0]["command"])
        # UserPromptSubmit has no matcher support, so none is set.
        self.assertNotIn("matcher", groups[0])

    def test_allow_file_ships_with_comments_only(self):
        path = REPO / "company-template" / ".claude" / "guard-allow.txt"
        live = [
            line for line in path.read_text(encoding="utf-8").splitlines()
            if line.split("#", 1)[0].strip()
        ]
        self.assertEqual(live, [])

    def test_no_approvals_log_ships_with_the_template(self):
        template = REPO / "company-template"
        self.assertEqual(list(template.rglob("approvals.log")), [])


if __name__ == "__main__":
    unittest.main()
