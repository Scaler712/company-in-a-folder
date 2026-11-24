"""Tests for scripts/new_company.py, scripts/doctor.py and scripts/check_kit.py.

Standard library only.
"""
from __future__ import annotations

import codecs
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "scripts"))

import check_kit  # noqa: E402
import build_index  # noqa: E402
import doctor  # noqa: E402
import new_company  # noqa: E402


def rot(s: str) -> str:
    return codecs.decode(s, "rot13")


class NewCompanyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_creates_folder_with_core_files_and_skills(self):
        target = self.tmp / "acme"
        files = new_company.create_company(target)
        self.assertTrue(files)
        for rel in [
            "READ-FIRST.md", "START-HERE.md", "corrections.md", "decisions.md",
            "core/business.md", "core/clients.md", "core/pricing-and-limits.md",
            "core/people.md", "core/priorities.md", "core/open-questions.md",
            "log/cards.md", "output/README.md",
            ".claude/skills/process-a-lead/SKILL.md",
        ]:
            self.assertTrue((target / rel).is_file(), rel)
        skills = sorted(p.name for p in (target / ".claude/skills").iterdir())
        self.assertEqual(skills, sorted(p.parent.name for p in (KIT / "skills").glob("*/SKILL.md")))

    def test_no_skills_flag(self):
        target = self.tmp / "acme"
        new_company.create_company(target, with_skills=False)
        # The guard ships with the template; only the skills are skipped.
        self.assertFalse((target / ".claude/skills").exists())
        self.assertTrue((target / ".claude/hooks/guard.py").is_file())
        self.assertTrue((target / "core/clients.md").is_file())

    def test_skills_do_not_wipe_the_guard(self):
        target = self.tmp / "acme-with-skills"
        new_company.create_company(target)
        self.assertTrue((target / ".claude/hooks/guard.py").is_file())
        self.assertTrue((target / ".claude/settings.json").is_file())
        self.assertTrue((target / ".claude/guard-allow.txt").is_file())
        self.assertTrue(any((target / ".claude/skills").iterdir()))

    def test_no_approvals_log_is_copied(self):
        target = self.tmp / "acme-clean"
        new_company.create_company(target)
        self.assertEqual(list(target.rglob("approvals.log")), [])

    def test_refuses_inside_repo(self):
        with self.assertRaises(ValueError) as ctx:
            new_company.create_company(KIT / "my-company-should-not-exist")
        self.assertIn("inside the kit", str(ctx.exception))
        self.assertFalse((KIT / "my-company-should-not-exist").exists())

    def test_refuses_parent_of_repo(self):
        with self.assertRaises(ValueError):
            new_company.create_company(KIT.parent)

    def test_refuses_non_empty_target(self):
        target = self.tmp / "busy"
        target.mkdir()
        (target / "keep.txt").write_text("mine")
        with self.assertRaises(ValueError):
            new_company.create_company(target)
        self.assertEqual((target / "keep.txt").read_text(), "mine")

    def test_cli_exit_codes(self):
        script = str(KIT / "scripts/new_company.py")
        ok = subprocess.run([sys.executable, script, str(self.tmp / "cli")], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("company folder created", ok.stdout)
        bad = subprocess.run([sys.executable, script, str(KIT / "nope")], capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertIn("refusing", bad.stderr)

    def test_writes_identical_agent_files(self):
        target = self.tmp / "acme"
        new_company.create_company(target, with_skills=False)
        rules = (target / "READ-FIRST.md").read_bytes()
        for name in ("AGENTS.md", "CLAUDE.md"):
            self.assertTrue((target / name).is_file(), name)
            self.assertEqual((target / name).read_bytes(), rules, name)

    def test_next_steps_say_open_the_folder(self):
        script = str(KIT / "scripts/new_company.py")
        ok = subprocess.run([sys.executable, script, str(self.tmp / "steps")], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertIn("open that folder in your AI tool", ok.stdout)
        self.assertNotIn("cp READ-FIRST.md", ok.stdout)

    def test_demo_copies_the_demo_company(self):
        kit = self.tmp / "kit"
        make_kit(kit)
        (kit / "demo-company/core").mkdir(parents=True)
        (kit / "demo-company/READ-FIRST.md").write_text("# Read this first\nFilled example.\n")
        (kit / "demo-company/core/clients.md").write_text("# Clients\nOffice landlords.\n")
        target = self.tmp / "demo-copy"
        new_company.create_company(target, kit_root=kit, demo=True)
        self.assertIn("Filled example", (target / "READ-FIRST.md").read_text())
        self.assertEqual((target / "AGENTS.md").read_bytes(), (target / "READ-FIRST.md").read_bytes())
        self.assertEqual((target / "CLAUDE.md").read_bytes(), (target / "READ-FIRST.md").read_bytes())
        self.assertTrue((target / ".claude/skills/demo-job/SKILL.md").is_file())
        self.assertNotIn("fill in", (target / "core/clients.md").read_text())

    def test_demo_folder_gets_the_guard(self):
        kit = self.tmp / "kit"
        make_kit(kit)
        guard = kit / "company-template/.claude/hooks"
        guard.mkdir(parents=True)
        (guard / "guard.py").write_text("# guard\n")
        (kit / "company-template/.claude/settings.json").write_text("{}\n")
        (kit / "company-template/.claude/guard-allow.txt").write_text("# none\n")
        (kit / "company-template/.claude/approvals.log").write_text("stale\n")
        (kit / "demo-company/core").mkdir(parents=True)
        (kit / "demo-company/READ-FIRST.md").write_text("# Read this first\n")
        target = self.tmp / "demo-guarded"
        new_company.create_company(target, kit_root=kit, demo=True)
        self.assertTrue((target / ".claude/hooks/guard.py").is_file())
        self.assertTrue((target / ".claude/settings.json").is_file())
        self.assertTrue((target / ".claude/guard-allow.txt").is_file())
        self.assertEqual(list(target.rglob("approvals.log")), [])

    def test_demo_keeps_its_own_guard(self):
        kit = self.tmp / "kit"
        make_kit(kit)
        guard = kit / "company-template/.claude/hooks"
        guard.mkdir(parents=True)
        (guard / "guard.py").write_text("# template guard\n")
        demo_hooks = kit / "demo-company/.claude/hooks"
        demo_hooks.mkdir(parents=True)
        (demo_hooks / "guard.py").write_text("# demo guard\n")
        (kit / "demo-company/READ-FIRST.md").write_text("# Read this first\n")
        target = self.tmp / "demo-own-guard"
        new_company.create_company(target, kit_root=kit, demo=True)
        self.assertIn("demo guard", (target / ".claude/hooks/guard.py").read_text())

    def test_demo_missing_gives_a_clear_error(self):
        kit = self.tmp / "kit"
        make_kit(kit)
        with self.assertRaises(ValueError) as ctx:
            new_company.create_company(self.tmp / "demo-copy", kit_root=kit, demo=True)
        self.assertIn("demo company not found", str(ctx.exception))
        self.assertIn("demo-company/", str(ctx.exception))
        self.assertFalse((self.tmp / "demo-copy").exists())

    def test_demo_still_refuses_bad_targets(self):
        kit = self.tmp / "kit"
        make_kit(kit)
        (kit / "demo-company/core").mkdir(parents=True)
        (kit / "demo-company/READ-FIRST.md").write_text("# Read this first\n")
        with self.assertRaises(ValueError) as ctx:
            new_company.create_company(kit / "inside", kit_root=kit, demo=True)
        self.assertIn("inside the kit", str(ctx.exception))
        busy = self.tmp / "busy-demo"
        busy.mkdir()
        (busy / "keep.txt").write_text("mine")
        with self.assertRaises(ValueError):
            new_company.create_company(busy, kit_root=kit, demo=True)


def make_kit(root: Path) -> None:
    """A minimal valid kit tree for check_kit tests."""
    (root / "skills/demo-job").mkdir(parents=True)
    (root / "skills/demo-job/SKILL.md").write_text(
        "---\nname: demo-job\ndescription: Does a demo. Use when testing.\n---\n"
        "# Demo\nRead `core/clients.md`.\n"
    )
    (root / "company-template/core").mkdir(parents=True)
    (root / "company-template/core/clients.md").write_text("# Clients\n")
    (root / "README.md").write_text("See `skills/demo-job/SKILL.md`.\n")


class CheckKitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        make_kit(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_check(self):
        out = io.StringIO()
        code = check_kit.run(self.tmp, out=out)
        return code, out.getvalue()

    def test_real_kit_passes(self):
        out = io.StringIO()
        self.assertEqual(check_kit.run(KIT, out=out), 0, out.getvalue())

    def test_minimal_kit_passes(self):
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_name_must_match_folder(self):
        p = self.tmp / "skills/demo-job/SKILL.md"
        p.write_text(p.read_text().replace("name: demo-job", "name: other-name"))
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("does not match folder", out)

    def test_description_needs_use_when(self):
        p = self.tmp / "skills/demo-job/SKILL.md"
        p.write_text(p.read_text().replace("Use when testing.", "For tests."))
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("Use when", out)

    def test_missing_frontmatter(self):
        (self.tmp / "skills/demo-job/SKILL.md").write_text("# no frontmatter\n")
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("frontmatter", out)

    def test_broken_path_fails_and_placeholders_skip(self):
        (self.tmp / "README.md").write_text(
            "See `core/missing.md` and `output/YYYY-MM-DD-x.md` and `contacts/<company>.md`.\n"
        )
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("core/missing.md", out)
        self.assertNotIn("YYYY", out)
        self.assertNotIn("<company>", out)

    def test_denylist_names_case_insensitive(self):
        for term in ["urval", "nggvb", "Ersf"]:
            word = rot(term)
            (self.tmp / "README.md").write_text(f"Thanks to {word.upper()} for this.\n")
            code, out = self.run_check()
            self.assertEqual(code, 1, word)
            self.assertIn("FAIL denylist", out)

    def test_denylist_is_word_based(self):
        (self.tmp / "README.md").write_text("An explanation of planar maps.\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_git_ref_url_allowed(self):
        (self.tmp / "README.md").write_text("https://example.org/archive/" + rot("ersf") + "/heads/main.zip\n")
        code, out = self.run_check()
        self.assertEqual(code, 0, out)

    def test_email_key_ip_detected(self):
        samples = {
            "email": "write to someone" + "@" + "example.com",
            "key": "s" + "k-" + "a1B2c3D4e5F6g7H8i9",
            "ip": ".".join(["10", "0", "0", "12"]),
        }
        for kind, text in samples.items():
            (self.tmp / "README.md").write_text(text + "\n")
            code, out = self.run_check()
            self.assertEqual(code, 1, kind)
            self.assertIn(f"{kind}:", out)

    def test_em_dash_fails_style(self):
        (self.tmp / "README.md").write_text("one \u2014 two\n")
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("FAIL style", out)

    def test_scan_covers_any_file_type(self):
        (self.tmp / "notes.txt").write_text(rot("nwp") + " group\n")
        code, out = self.run_check()
        self.assertEqual(code, 1)
        self.assertIn("notes.txt", out)


TODAY = date(2027, 3, 8)


def day(offset: int) -> str:
    """A date string offset days away from TODAY, for repeatable fixtures."""
    return (TODAY + timedelta(days=offset)).isoformat()


FILLED_CORE = {
    "business.md": (
        "# Business\n\nWe size and install heat pumps for small office buildings.\n"
        "We have run since 2014 and there are 22 of us.\n"
    ),
    "clients.md": (
        "# Clients\n\n## Who we sell to\n\n"
        "- Type of business: landlords of office buildings under 40 units\n"
        "- Size: 10 to 60 staff\n"
        "- Who decides: the owner or the facilities lead\n\n"
        "## Our best 3 clients and why\n\n"
        "1. A landlord with 6 buildings who wanted one survey per year.\n"
        "2. A school group that needed the plant room drawn before tender.\n"
        "3. A property manager who pays on time and asks few questions.\n\n"
        "## Signs of a good fit\n\n"
        "- They already have drawings of the plant room.\n"
        "- They talk about running cost, not purchase price.\n\n"
        "## Who we turn down\n\n"
        "- Home owners because our smallest job is 40 units.\n"
        "- Builders who want a price before drawings because we cannot size the plant.\n\n"
        "## Where to send people we turn down\n\n"
        "- A local installer group that does single homes.\n"
    ),
    "pricing-and-limits.md": (
        "# Pricing and limits\n\nA survey is 900 per building. Design is 4 percent of works.\n"
        "We never quote works we have not surveyed.\n"
    ),
    "people.md": "# People\n\nOwner signs every proposal. Two designers. One site lead.\n",
    "open-questions.md": "# Open questions\n\nNothing open today.\n",
}


def make_company(root: Path, today: date = TODAY) -> None:
    """A company folder that should score full marks."""
    (root / "core").mkdir(parents=True)
    (root / "log").mkdir()
    (root / "communication").mkdir()
    rules = "# Read this first\n\nUnknown stays unknown. Stop at the card.\n"
    (root / "READ-FIRST.md").write_text(rules)
    for name in ("AGENTS.md", "CLAUDE.md"):
        (root / name).write_text(rules)
    for name, text in FILLED_CORE.items():
        (root / "core" / name).write_text(text)
    (root / "core/priorities.md").write_text(
        "# Priorities\n\nLast updated: " + today.isoformat() + "\n\n"
        "1. Win two office retrofits by the end of the month.\n"
        "2. Cut a survey to one day on site.\n\n"
        "## Not now\n\n- New build work.\n"
    )
    (root / "communication/emails-i-sent.md").write_text(
        "# Emails I sent\n\nReal emails, names removed.\n\n"
        + "".join(
            f"## {n}. reply to a new lead\n\nThanks for getting in touch, I can look at this on Thursday.\n\n"
            for n in range(1, 6)
        )
    )
    (root / "log/cards.md").write_text(
        "# Cards\n\nOne block per card, in order.\n\n"
        "C-1 | " + day(-9) + " 09:00 | job: process-a-lead | tool: by hand | to: a lead | "
        "change: none -> reply drafted\n"
        'answer: yes C-1 at 09:20\n'
        "done: sent by hand, " + day(-9) + "\n"
    )
    (root / "decisions.md").write_text(
        "# Decisions\n\n"
        "## D-1 | " + day(-20) + " | proposed by: weekly-plan\n"
        "proposal: run the lead job every morning\n"
        "why: core/priorities.md\n"
        "expected result: every lead answered the same day\n"
        "check on: " + day(-13) + "\n"
        "owner answer: yes, " + day(-19) + "\n"
        "actual (filled on the check date): all 6 leads answered the same day\n"
        "keep, change or drop: keep\n"
    )
    for name in ("process-a-lead", "weekly-plan"):
        folder = root / ".claude/skills" / name
        folder.mkdir(parents=True)
        (folder / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: One job. Use when asked.\n---\n# {name}\n"
        )


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def filled(self) -> Path:
        root = self.tmp / "filled"
        make_company(root)
        return root

    def ids(self, result: dict) -> dict:
        return {f["id"]: f for f in result["findings"]}

    def test_fresh_template_scores_low_and_points_at_clients(self):
        target = self.tmp / "fresh"
        new_company.create_company(target)
        result = doctor.run_doctor(target, TODAY)
        self.assertLess(result["score"], 60)
        self.assertIn("core/clients.md", result["next_step"])
        self.assertEqual(self.ids(result)["agent-files"]["status"], "pass")
        self.assertEqual(self.ids(result)["placeholders:core/clients.md"]["status"], "fail")

    def test_filled_folder_scores_full_marks(self):
        result = doctor.run_doctor(self.filled(), TODAY)
        failed = [f["id"] for f in result["findings"] if f["status"] != "pass"]
        self.assertEqual(failed, [], doctor.format_report(result))
        self.assertEqual(result["score"], 100)
        self.assertIn("Nothing to fix", result["next_step"])

    def test_placeholder_counting_is_per_file(self):
        root = self.filled()
        marker = "[fill in: who signs]"
        (root / "core/people.md").write_text("# People\n\n" + marker + "\n" + marker + "\n")
        result = doctor.run_doctor(root, TODAY)
        people = self.ids(result)["placeholders:core/people.md"]
        self.assertIn("2 '[fill in' markers", people["detail"])
        self.assertLess(people["points"], people["max"])
        self.assertEqual(self.ids(result)["placeholders:core/clients.md"]["status"], "pass")
        self.assertEqual(doctor.count_placeholders("none here"), 0)

    def test_more_than_three_priorities_is_flagged(self):
        root = self.filled()
        (root / "core/priorities.md").write_text(
            "# Priorities\n\nLast updated: " + TODAY.isoformat() + "\n\n"
            "1. One.\n2. Two.\n3. Three.\n4. Four.\n"
        )
        result = doctor.run_doctor(root, TODAY)
        count = self.ids(result)["priorities-count"]
        self.assertEqual(count["status"], "fail")
        self.assertIn("the cap is 3", count["detail"])
        self.assertEqual(self.ids(result)["priorities-fresh"]["status"], "pass")

    def test_stale_priorities_date_is_flagged(self):
        root = self.filled()
        fresh = doctor.run_doctor(root, TODAY)
        self.assertEqual(self.ids(fresh)["priorities-fresh"]["status"], "pass")
        later = doctor.run_doctor(root, TODAY + timedelta(days=30))
        stale = self.ids(later)["priorities-fresh"]
        self.assertEqual(stale["status"], "fail")
        self.assertIn("30 days ago", stale["detail"])

    def test_held_card_flagged_and_answered_card_is_not(self):
        root = self.filled()
        base = (root / "log/cards.md").read_text()
        (root / "log/cards.md").write_text(
            base
            + "\nC-2 | " + day(-5) + " 10:00 | job: write-a-proposal | tool: by hand | to: a client | "
            "change: none -> proposal drafted\nanswer:\ndone: not done\n"
            + "\nC-3 | " + day(-6) + " 11:00 | job: prepare-a-call | tool: by hand | to: a client | "
            "change: none -> brief written\nanswer: no\ndone: not done\n"
        )
        result = doctor.run_doctor(root, TODAY)
        held = self.ids(result)["held-cards"]
        self.assertEqual(held["status"], "fail")
        self.assertIn("C-2", held["detail"])
        self.assertNotIn("C-3", held["detail"])
        self.assertNotIn("C-1", held["detail"])

    def test_decision_past_its_check_date_is_flagged(self):
        root = self.filled()
        (root / "decisions.md").write_text(
            "# Decisions\n\n## D-2 | " + day(-10) + " | proposed by: weekly-plan\n"
            "proposal: drop the Friday review\nwhy: nobody reads it\n"
            "expected result: two hours back\ncheck on: " + day(-3) + "\n"
            "owner answer: yes\nactual (filled on the check date): <what happened>\n"
            "keep, change or drop: <decision>\n"
        )
        result = doctor.run_doctor(root, TODAY)
        due = self.ids(result)["decisions-due"]
        self.assertEqual(due["status"], "fail")
        self.assertIn("D-2", due["detail"])

    def test_secret_is_reported_by_line_without_echoing_it(self):
        root = self.filled()
        secret = "s" + "k-" + "A1b2C3d4E5f6G7h8I9"
        (root / "notes.md").write_text("# Notes\n\nnothing\ntoken " + secret + "\n")
        result = doctor.run_doctor(root, TODAY)
        found = self.ids(result)["secrets"]
        self.assertEqual(found["status"], "fail")
        self.assertIn("notes.md:4", found["detail"])
        self.assertNotIn(secret, found["detail"])
        self.assertNotIn(secret, doctor.format_report(result))
        self.assertLessEqual(result["score"], 50)

    def test_long_id_in_a_link_is_not_a_card_number(self):
        root = self.filled()
        (root / "note.md").write_text(
            "See https://example.com/help/" + "2692697373" + "96981 for the rule.\n"
            "Order " + "1234567890" + "12345 is a reference, not a card.\n"
        )
        self.assertEqual(doctor.scan_secrets(root), [])

    def test_password_line_and_card_digits_are_found(self):
        root = self.filled()
        (root / "notes.md").write_text(
            "# Notes\n\npassword: " + "n0t-a-real-one-x\n"
            + "card " + "4" + "1" * 15 + "\n"
        )
        result = doctor.run_doctor(root, TODAY)
        detail = self.ids(result)["secrets"]["detail"]
        self.assertIn("password or key line", detail)
        self.assertIn("card-number-shaped digits", detail)

    def test_missing_agent_files_are_flagged(self):
        root = self.filled()
        (root / "CLAUDE.md").unlink()
        result = doctor.run_doctor(root, TODAY)
        self.assertEqual(self.ids(result)["agent-files"]["status"], "fail")
        self.assertIn("CLAUDE.md", self.ids(result)["agent-files"]["detail"])
        (root / "CLAUDE.md").write_text("# other rules\n")
        changed = doctor.run_doctor(root, TODAY)
        self.assertIn("differ from READ-FIRST.md", self.ids(changed)["agent-files"]["detail"])

    def test_turn_down_needs_two_lines(self):
        root = self.filled()
        text = (root / "core/clients.md").read_text()
        (root / "core/clients.md").write_text(
            text.replace("- Builders who want a price before drawings because we cannot size the plant.\n", "")
        )
        result = doctor.run_doctor(root, TODAY)
        turn = self.ids(result)["turn-down"]
        self.assertEqual(turn["status"], "fail")
        self.assertIn("at least 2", turn["detail"])

    def test_email_samples_are_counted_and_explained(self):
        root = self.filled()
        (root / "communication/emails-i-sent.md").write_text(
            "# Emails I sent\n\nPaste real emails here.\n\n"
            "## 1. reply to a new lead\n\n[paste]\n\n## 2. a polite no\n\nSorry, this one is not for us.\n"
        )
        result = doctor.run_doctor(root, TODAY)
        emails = self.ids(result)["email-samples"]
        self.assertNotEqual(emails["status"], "pass")
        self.assertIn("counted 1 email sample", emails["detail"])
        self.assertIn("sections with pasted text", emails["detail"])

    def test_skills_need_two_installed(self):
        root = self.filled()
        shutil.rmtree(root / ".claude/skills/weekly-plan")
        result = doctor.run_doctor(root, TODAY)
        self.assertEqual(self.ids(result)["skills-installed"]["status"], "fail")

    def test_git_remote_is_a_warning(self):
        root = self.filled()
        (root / ".git").mkdir()
        (root / ".git/config").write_text(
            '[core]\n\tbare = false\n[remote "origin"]\n\turl = ssh://example.org/one.git\n'
        )
        result = doctor.run_doctor(root, TODAY)
        git = self.ids(result)["git-remote"]
        self.assertEqual(git["status"], "warn")
        self.assertIn("private", git["detail"])

    def test_not_a_company_folder_exits_two(self):
        plain = self.tmp / "plain"
        plain.mkdir()
        with self.assertRaises(doctor.NotACompanyFolder):
            doctor.run_doctor(plain, TODAY)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = doctor.main([str(plain)])
        self.assertEqual(code, 2)
        self.assertIn("not a company folder", err.getvalue())

    def test_bad_today_exits_two(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            code = doctor.main([str(self.filled()), "--today", "08-03-2027"])
        self.assertEqual(code, 2)
        self.assertIn("YYYY-MM-DD", err.getvalue())

    def test_cli_human_and_json_output(self):
        root = self.filled()
        script = str(KIT / "scripts/doctor.py")
        human = subprocess.run(
            [sys.executable, script, str(root), "--today", TODAY.isoformat()],
            capture_output=True, text=True,
        )
        self.assertEqual(human.returncode, 0, human.stderr)
        self.assertIn("AI OS doctor: 100/100", human.stdout)
        self.assertIn("Next step:", human.stdout)
        as_json = subprocess.run(
            [sys.executable, script, str(root), "--today", TODAY.isoformat(), "--json"],
            capture_output=True, text=True,
        )
        self.assertEqual(as_json.returncode, 0, as_json.stderr)
        payload = json.loads(as_json.stdout)
        self.assertEqual(payload["score"], 100)
        self.assertIn("next_step", payload)
        self.assertTrue(payload["findings"])
        for item in payload["findings"]:
            self.assertEqual(sorted(item), ["detail", "id", "max", "points", "status"])

    def test_doctor_writes_nothing(self):
        root = self.filled()
        before = {p: p.stat().st_mtime_ns for p in sorted(root.rglob("*")) if p.is_file()}
        doctor.run_doctor(root, TODAY)
        after = {p: p.stat().st_mtime_ns for p in sorted(root.rglob("*")) if p.is_file()}
        self.assertEqual(before, after)


class BuildIndexTests(unittest.TestCase):
    def test_real_kit_index_is_current_and_clean(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = build_index.main(["--check"])
        self.assertEqual(code, 0, buf.getvalue())

    def test_missing_and_duplicate_skills_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("alpha", "beta"):
                d = root / "skills" / name
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(
                    "---\nname: " + name + "\ndescription: Does a thing. "
                    'Use when asked "do the ' + name + '" or "run ' + name + '".\n---\n'
                )
            (root / "departments.json").write_text(json.dumps({"One": ["alpha", "alpha", "gamma"]}))
            _, _, problems = build_index.collect(root)
            text = "\n".join(problems)
            self.assertIn("more than once", text)
            self.assertIn("not in departments.json: beta", text)
            self.assertIn("does not exist: gamma", text)

    def test_shared_trigger_phrase_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("alpha", "beta"):
                d = root / "skills" / name
                d.mkdir(parents=True)
                (d / "SKILL.md").write_text(
                    "---\nname: " + name + "\ndescription: Does a thing. "
                    'Use when asked "same words" or "only ' + name + '".\n---\n'
                )
            (root / "departments.json").write_text(json.dumps({"One": ["alpha", "beta"]}))
            _, _, problems = build_index.collect(root)
            self.assertTrue(any("claimed by two skills" in p for p in problems), problems)


if __name__ == "__main__":
    unittest.main()
