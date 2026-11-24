#!/usr/bin/env python3
"""Company guard for Claude Code. Standard library only, Python 3.9+.

Claude Code calls this script on two events. The hook contract
(https://docs.claude.com/en/docs/claude-code/hooks):

  * the event arrives as one JSON object on stdin, with the fields cwd and
    hook_event_name plus the fields for that event: PreToolUse carries
    tool_name and tool_input, UserPromptSubmit carries prompt;
  * on PreToolUse, exit code 0 means the hook has no objection and the tool
    call goes on through the normal permission flow, and exit code 2 blocks
    the call with the hook's stderr shown to the model as the reason;
  * on UserPromptSubmit, exit code 2 would reject the prompt, so this hook
    always exits 0 there. Its stdout is added to the model's context, so it
    prints at most one short line.

Two modes:

  * PreToolUse (no flag, or --pre-tool-use): decide one tool call.
  * UserPromptSubmit (--prompt): read the owner's typed prompt and record
    every explicit "yes C-<n>" in the approvals log inside .claude/.

Decision order on a tool call:

  1. SELF PROTECTION. The agent may read the guard's own files and never
     write, move or delete them. No card waives this.
  2. NEVER LIST. Blocked even with an approved card: a shell delete that
     touches anything outside output/, an obvious bulk send, and any
     outbound call whose input names more than MAX_RECIPIENTS people.
  3. READ ONLY AND LOCAL. Always allowed: reading, searching, listing, web
     fetch and web search, writing inside the company folder, and shell
     commands that are plainly local.
  4. OUTBOUND. Needs a card in log/cards.md whose tool field matches the
     call AND an unspent "yes C-<n>" for that card in the approvals log.
     Allowing the call spends that yes: the guard appends a "used" line, so
     the next outbound call needs a new typed yes.
  5. UNKNOWN TOOL. Blocked, with a line telling the owner how to allow it.

A "yes" written into log/cards.md approves nothing. Only the approvals log
counts, and only the prompt hook writes yes lines into it.

Fail closed: if the event cannot be parsed, or the cards file cannot be
read, or the approvals log cannot be read or written, outbound calls are
blocked. Read only work still goes through.

Run the built in cases with:

    python3 .claude/hooks/guard.py --self-test
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
import shlex
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# --------------------------------------------------------------------------
# Lists the owner can edit. Keep them lowercase.
# --------------------------------------------------------------------------

# Action words in an MCP tool name that mean the call changes something
# somewhere else. Checked before the read words.
WRITE_VERBS = {
    "send", "sends", "reply", "replies", "respond", "create", "created",
    "add", "insert", "update", "edit", "modify", "patch", "set", "write",
    "delete", "remove", "archive", "post", "publish", "schedule", "book",
    "pay", "charge", "refund", "invite", "share", "upload", "attach",
    "comment", "merge", "approve", "assign", "move", "transfer", "import",
    "export", "subscribe", "unsubscribe", "enroll", "enqueue", "trigger",
    "execute", "run", "start", "stop", "cancel", "complete", "close",
    "draft", "forward", "message", "dm", "call", "sign", "submit",
}

# Action words that mean the call only looks at something.
READ_VERBS = {
    "get", "list", "search", "read", "fetch", "find", "lookup", "query",
    "show", "view", "describe", "count", "check", "status", "info",
    "summary", "preview", "resolve", "me", "whoami", "schema", "download",
}

# First word of a shell command that is plainly local.
SAFE_SHELL = {
    "ls", "cat", "head", "tail", "wc", "grep", "egrep", "rg", "fgrep",
    "sort", "uniq", "cut", "tr", "sed", "awk", "jq", "echo", "printf",
    "pwd", "cd", "date", "basename", "dirname", "diff", "stat", "file",
    "which", "test", "true", "false", "sleep", "whoami", "hostname",
    "python", "python3", "node", "git", "unzip", "tar", "md5", "shasum",
    "wc_l", "column", "fold", "nl", "seq", "realpath", "readlink",
}

# Local commands that write. Their targets must sit inside the company folder.
LOCAL_WRITE_SHELL = {"cp", "mv", "touch", "mkdir", "tee", "install"}

# Commands that delete. Allowed only when every target is inside output/.
DELETE_SHELL = {"rm", "rmdir", "unlink", "shred", "trash", "truncate"}

# Commands that always count as a delete we never do from a bot.
ALWAYS_NEVER_SHELL = {("git", "clean"), ("git", "reset"), ("git", "rm")}

# Commands that send data out of this machine.
OUTBOUND_SHELL = {
    "curl", "wget", "http", "httpie", "mail", "mailx", "sendmail", "msmtp",
    "mutt", "ssh", "scp", "sftp", "rsync", "gh", "glab", "aws", "gcloud",
    "az", "twilio", "stripe", "osascript", "open",
}

# Claude Code tools that only look at things.
READ_ONLY_TOOLS = {
    "read", "grep", "glob", "ls", "notebookread", "webfetch", "websearch",
    "todowrite", "todoread", "exitplanmode", "bashoutput", "killshell",
    "killbash", "task", "skill", "slashcommand", "agentoutput", "listmcp",
    "think", "plan",
}

# Claude Code tools that write files. Paths must sit inside the folder.
WRITE_TOOLS = {"write", "edit", "multiedit", "notebookedit", "applypatch"}

# Extra tool names the owner trusts as read only, on top of guard-allow.txt.
EXTRA_ALLOWED_TOOLS = set()

# Input keys that name people a message would reach.
RECIPIENT_KEYS = {
    "to", "cc", "bcc", "recipient", "recipients", "recipient_ids", "emails",
    "email_addresses", "addresses", "contacts", "contact_ids", "members",
    "participants", "attendees", "phone_numbers", "numbers", "user_ids",
    "usernames", "channels", "channel_ids", "list_ids", "audience",
}

# Words that mean a bulk send, wherever they turn up in an outbound call.
BULK_WORDS = {
    "bulk", "batch_send", "broadcast", "campaign", "blast", "massmail",
    "mass_send", "sendmany", "send_all", "send_many", "everyone",
    "all_contacts", "all_subscribers", "mailing_list", "newsletter",
    "sequence_start", "drip",
}

MAX_RECIPIENTS = 3
ALLOW_FILE_REL = Path(".claude") / "guard-allow.txt"
CARDS_REL = Path("log") / "cards.md"
APPROVALS_REL = Path(".claude") / "approvals.log"

# Files only the owner edits by hand. The agent may read them and never
# write, move or delete them. No card waives this.
PROTECTED_FILES = (
    Path(".claude") / "approvals.log",
    Path(".claude") / "settings.json",
    Path(".claude") / "settings.local.json",
    Path(".claude") / "guard-allow.txt",
)
PROTECTED_DIRS = (Path(".claude") / "hooks",)

# Shell command heads that change a file they name.
PROTECT_WRITE_HEADS = {
    "cp", "mv", "touch", "mkdir", "tee", "install", "ln", "rm", "rmdir",
    "unlink", "shred", "trash", "truncate", "dd", "chmod", "chown",
    "sponge", "patch",
}

PROTECTED_HINT = (
    "The owner edits these by hand. Reading them is fine; writing, moving "
    "or deleting them is not, with any card."
)

# --------------------------------------------------------------------------

CARD_NUM_RE = re.compile(r"\bC-(\d+)\s*\|")
CARD_TOOL_RE = re.compile(r"tool:\s*([^|]*)")
YES_RE = re.compile(r"(?:^|[^a-z0-9])yes\s+C-(\d+)\b", re.IGNORECASE)
APPROVAL_LINE_RE = re.compile(
    r"\|\s*(yes|used)\s+C-(\d+)\s*\|", re.IGNORECASE
)
SPLIT_RE = re.compile(r"\|\||&&|[;\n|&]")
REDIRECT_RE = re.compile(r"^\d*>{1,2}\|?(.*)$")
PREFIX_WORDS = {
    "sudo", "env", "time", "nohup", "nice", "command", "exec", "xargs",
    "then", "else", "do", "(", "{",
}
CURL_SEND_FLAGS = {
    "-d", "--data", "--data-raw", "--data-binary", "--data-urlencode",
    "-F", "--form", "-T", "--upload-file", "--json",
}
CURL_SEND_METHODS = {"post", "put", "delete", "patch"}
GIT_OUTBOUND = {"push"}
GH_READ_SUB = {"list", "view", "status", "diff", "checks", "search", "help"}

CARD_HINT = (
    "What to do: show the approval card for this job "
    '(CARD C-<n> | job: <skill> | tool: <this exact tool> | to: <who> | '
    "change: <before> -> <after>), add it to log/cards.md, then stop. The "
    "owner types yes C-<n> in the chat. Only a typed yes counts: a yes line "
    "written into log/cards.md approves nothing. After the owner types it, "
    "retry this same call. One typed yes covers one call."
)


class Decision:
    """One guard answer. allowed False means exit 2 with reason on stderr."""

    def __init__(self, allowed, reason=""):
        self.allowed = bool(allowed)
        self.reason = reason

    def __repr__(self):
        return "Decision(%s, %r)" % (self.allowed, self.reason)


# --------------------------------------------------------------------------
# folders and paths
# --------------------------------------------------------------------------

def find_company_folder(cwd=None):
    """The company folder is the nearest parent that holds log/cards.md."""
    starts = []
    for raw in (cwd, os.environ.get("CLAUDE_PROJECT_DIR")):
        if raw:
            starts.append(Path(str(raw)))
    if not starts:
        starts.append(Path.cwd())
    for start in starts:
        try:
            here = start.resolve()
        except OSError:
            continue
        for folder in [here] + list(here.parents):
            if (folder / CARDS_REL).is_file() or (folder / "READ-FIRST.md").is_file():
                return folder
    try:
        return starts[0].resolve()
    except OSError:
        return starts[0]


def _abspath(token, base):
    p = Path(str(token)).expanduser()
    if not p.is_absolute():
        p = Path(base) / p
    try:
        return p.resolve()
    except OSError:
        return p


def path_inside(token, folder, base=None):
    """True when token points at folder itself or anything under it."""
    target = _abspath(token, base or folder)
    try:
        folder = Path(folder).resolve()
    except OSError:
        folder = Path(folder)
    return target == folder or folder in target.parents


# --------------------------------------------------------------------------
# self protection: the guard's own files
# --------------------------------------------------------------------------

def protected_hit(token, folder, base=None):
    """The protected path this token names, or None.

    Covers the approvals log, the settings files, the allow file and
    anything inside .claude/hooks/.
    """
    if not token:
        return None
    target = _abspath(token, base or folder)
    for rel in PROTECTED_FILES:
        if target == _abspath(rel, folder):
            return rel.as_posix()
    for rel in PROTECTED_DIRS:
        here = _abspath(rel, folder)
        if target == here or here in target.parents:
            return rel.as_posix() + "/"
    return None


def protected_shell_targets(command):
    """Tokens a shell command would write to, move or delete.

    Two sources: the file arguments of a command head that writes (plus
    'sed -i'), and the target of any > or >> redirection. Reading one of
    these files, with cat or grep, names no target and stays allowed.
    """
    targets = []
    for segment in split_segments(command):
        tokens = tokenize(segment)
        if not tokens:
            continue
        head = Path(tokens[0]).name.lower()
        writes = head in PROTECT_WRITE_HEADS
        if head in ("sed", "perl", "ruby"):
            writes = any(t.startswith("-i") for t in tokens[1:])
        if writes:
            targets.extend(file_args(tokens))
        for i, tok in enumerate(tokens):
            m = REDIRECT_RE.match(tok)
            if not m:
                continue
            rest = m.group(1)
            if rest:
                targets.append(rest)
            elif i + 1 < len(tokens):
                targets.append(tokens[i + 1])
    return targets


# --------------------------------------------------------------------------
# cards
# --------------------------------------------------------------------------

def read_cards_text(folder):
    """Return the cards file text, or None when it cannot be read."""
    try:
        return (Path(folder) / CARDS_REL).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def cards_in_file(text):
    """Every card in the file, as (number, tool field) pairs, lowest first.

    A 'yes' line in this file means nothing to the guard. Approvals live in
    the approvals log inside .claude/, which only the prompt hook writes.
    """
    if not text:
        return []
    tools = {}
    for line in text.splitlines():
        if "tool:" not in line:
            continue
        num = CARD_NUM_RE.search(line)
        if not num:
            continue
        field = CARD_TOOL_RE.search(line)
        tools[num.group(1)] = field.group(1).strip() if field else ""
    return [(num, tools[num]) for num in sorted(tools, key=int)]


# --------------------------------------------------------------------------
# approvals log: the owner's typed yes, and the one action that spends it
# --------------------------------------------------------------------------

def approvals_path(folder):
    return Path(folder) / APPROVALS_REL


def read_approvals(folder):
    """Return {number: unspent yes count}, or None when the log is unusable.

    A missing log is normal and reads as empty. Anything else that stops the
    guard from reading the file returns None, and outbound calls are blocked.
    """
    path = approvals_path(folder)
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        text = ""
    except (OSError, UnicodeDecodeError):
        return None
    counts = {}
    for line in text.splitlines():
        m = APPROVAL_LINE_RE.search(line)
        if not m:
            continue
        kind, num = m.group(1).lower(), m.group(2)
        counts[num] = counts.get(num, 0) + (1 if kind == "yes" else -1)
    return counts


def append_approval(folder, body):
    """Append one '<ISO time> | <body>' line. False when it cannot be done."""
    path = approvals_path(folder)
    line = "%s | %s\n" % (datetime.now().isoformat(timespec="seconds"), body)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(path), "a", encoding="utf-8") as fh:
            fh.write(line)
        return True
    except OSError:
        return False


def typed_yes_numbers(prompt):
    """Card numbers the owner explicitly approved in one typed prompt.

    Same strictness as the card rule: only 'yes C-<n>'. 'ok', 'looks good',
    'yes to everything' and a bare 'yes' are not an approval. Several
    explicit numbers in one prompt each count once.
    """
    out = []
    for m in YES_RE.finditer(str(prompt or "")):
        num = m.group(1)
        if num not in out:
            out.append(num)
    return out


def normalize(text):
    """Lowercase, split camel case, turn anything else into single spaces."""
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", str(text))
    text = re.sub(r"[^A-Za-z0-9]+", " ", text).lower()
    return " ".join(text.split())


def card_tool_matches(card_tool, call_name):
    """Matching rule, documented in .claude/hooks/README.md:

    normalize both sides (lowercase, camel case split, every other
    character becomes a space), then match when either normalized string
    contains the other, or when every word of the card's tool field (each
    at least three characters) also appears in the call name. An empty
    card tool field, or 'by hand', never matches a tool call.
    """
    card = normalize(card_tool)
    call = normalize(call_name)
    if len(card) < 3 or len(call) < 1:
        return False
    if card in ("by hand", "none", "manual"):
        return False
    if card in call or call in card:
        return True
    words = card.split()
    call_words = set(call.split())
    if words and all(len(w) >= 3 for w in words):
        return all(w in call_words for w in words)
    return False


# --------------------------------------------------------------------------
# input scanning
# --------------------------------------------------------------------------

def _walk(value, keypath=""):
    if isinstance(value, dict):
        for k, v in value.items():
            for item in _walk(v, str(k).lower()):
                yield item
    elif isinstance(value, (list, tuple)):
        for v in value:
            for item in _walk(v, keypath):
                yield item
    else:
        yield keypath, value


def count_recipients(tool_input):
    """How many people this call names. Splits comma separated strings."""
    found = set()
    for key, value in _walk(tool_input):
        if key not in RECIPIENT_KEYS:
            continue
        if isinstance(value, (int, float)):
            found.add(str(value))
            continue
        if not isinstance(value, str):
            continue
        for part in re.split(r"[,;]", value):
            part = part.strip()
            if part:
                found.add(part.lower())
    return len(found)


def blob_of(tool_name, tool_input):
    try:
        dumped = json.dumps(tool_input, default=str)
    except (TypeError, ValueError):
        dumped = str(tool_input)
    return normalize(tool_name + " " + dumped)


def bulk_hit(tool_name, tool_input):
    blob = blob_of(tool_name, tool_input)
    words = set(blob.split())
    for term in BULK_WORDS:
        plain = normalize(term)
        if plain in words or (" " in plain and plain in blob):
            return term
    return None


# --------------------------------------------------------------------------
# shell reading
# --------------------------------------------------------------------------

def split_segments(command):
    parts = []
    for chunk in SPLIT_RE.split(str(command)):
        chunk = chunk.strip()
        if chunk:
            parts.append(chunk)
    return parts


def tokenize(segment):
    try:
        tokens = shlex.split(segment, comments=True)
    except ValueError:
        tokens = segment.split()
    while tokens and tokens[0].strip("()[]{}") in PREFIX_WORDS:
        tokens = tokens[1:]
    while tokens and "=" in tokens[0] and not tokens[0].startswith("-"):
        tokens = tokens[1:]
    return tokens


def file_args(tokens):
    out = []
    for t in tokens[1:]:
        if t.startswith("-"):
            continue
        out.append(t)
    return out


def classify_shell(command, folder, base):
    """Return a Decision, or ('outbound', label) for a sending command."""
    segments = split_segments(command)
    if not segments:
        return Decision(True, "empty command")
    for token in protected_shell_targets(command):
        hit = protected_hit(token, folder, base)
        if hit:
            return Decision(
                False,
                "never list: this command would change '%s', which belongs "
                "to the guard. %s" % (hit, PROTECTED_HINT),
            )
    output_dir = Path(folder) / "output"
    for segment in segments:
        tokens = tokenize(segment)
        if not tokens:
            continue
        head = Path(tokens[0]).name.lower()
        sub = tokens[1].lower() if len(tokens) > 1 else ""

        if (head, sub) in ALWAYS_NEVER_SHELL:
            return Decision(
                False,
                "never list: '%s %s' can delete work outside output/. "
                "The owner does this by hand." % (head, sub),
            )
        if head == "find" and ("-delete" in tokens or "-exec" in tokens):
            return Decision(
                False,
                "never list: a find that deletes or runs a command is not "
                "allowed. The owner does this by hand.",
            )
        if head in DELETE_SHELL:
            targets = file_args(tokens)
            if not targets:
                return Decision(
                    False,
                    "never list: '%s' with no clear target is blocked." % head,
                )
            for t in targets:
                if not path_inside(t, output_dir, base):
                    return Decision(
                        False,
                        "never list: deleting '%s' is outside output/. Only "
                        "files under output/ may be deleted, and the owner "
                        "does the rest by hand." % t,
                    )
            continue
        if head in OUTBOUND_SHELL:
            verdict = shell_sends(head, tokens, folder, base)
            if verdict is not None:
                return verdict
            continue
        if head == "git":
            if sub in GIT_OUTBOUND:
                return ("outbound", "git " + sub)
            continue
        if head in LOCAL_WRITE_SHELL:
            for t in file_args(tokens):
                if not path_inside(t, folder, base):
                    return Decision(
                        False,
                        "'%s' would write to '%s', outside the company "
                        "folder. Keep work inside the folder, or show a "
                        "card for it." % (head, t),
                    )
            continue
        if head in SAFE_SHELL or head in EXTRA_ALLOWED_TOOLS:
            continue
        return Decision(
            False,
            "the guard does not know the command '%s', so it is blocked. "
            "If it is local and read only, the owner can add it to the "
            "SAFE_SHELL list at the top of .claude/hooks/guard.py." % head,
        )
    return Decision(True, "local shell command")


def shell_sends(head, tokens, folder, base):
    """None means this use is a read. Otherwise a Decision or outbound pair."""
    lowered = [t.lower() for t in tokens]
    if head in ("curl", "http", "httpie", "wget"):
        # Flags keep their case on purpose: curl uses -F and -T and -X for
        # sending, while -f and -x mean something else.
        for i, t in enumerate(tokens):
            low = t.lower()
            if t in CURL_SEND_FLAGS or low in ("--data", "--data-raw",
                                               "--data-binary", "--form",
                                               "--json", "--upload-file",
                                               "--data-urlencode"):
                return ("outbound", head)
            if t in ("-X", "--request", "--method") and i + 1 < len(tokens):
                if tokens[i + 1].lower() in CURL_SEND_METHODS:
                    return ("outbound", head)
            if low.startswith("--request=") or low.startswith("--method="):
                if low.split("=", 1)[1] in CURL_SEND_METHODS:
                    return ("outbound", head)
            if low.startswith("--post-"):
                return ("outbound", head)
        return None
    if head in ("mail", "mailx", "sendmail", "msmtp", "mutt"):
        return ("outbound", head)
    if head in ("ssh", "sftp", "twilio", "stripe", "osascript", "open"):
        return ("outbound", head)
    if head in ("scp", "rsync"):
        for t in tokens[1:]:
            if t.startswith("-"):
                continue
            if re.match(r"^[A-Za-z0-9._\-]+@?[A-Za-z0-9._\-]*:", t):
                return ("outbound", head)
        for t in file_args(tokens):
            if not path_inside(t, folder, base):
                return Decision(
                    False,
                    "'%s' would copy to '%s', outside the company folder. "
                    "Show a card for it." % (head, t),
                )
        return None
    if head in ("gh", "glab"):
        sub = lowered[2] if len(lowered) > 2 else ""
        if len(lowered) > 1 and lowered[1] == "api":
            return ("outbound", head + " api")
        if sub and sub in GH_READ_SUB:
            return None
        return ("outbound", head)
    if head in ("aws", "gcloud", "az"):
        return ("outbound", head)
    return ("outbound", head)


# --------------------------------------------------------------------------
# tool reading
# --------------------------------------------------------------------------

def load_allow_patterns(folder):
    patterns = []
    try:
        text = (Path(folder) / ALLOW_FILE_REL).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return patterns
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            patterns.append(line)
    return patterns


def allow_listed(tool_name, patterns):
    low = tool_name.lower()
    for pat in patterns:
        if fnmatch.fnmatch(low, pat.lower()) or pat.lower() == low:
            return True
    return False


def mcp_action(tool_name):
    """'write', 'read' or 'unknown' for an MCP tool name."""
    words = normalize(tool_name.split("mcp", 1)[-1]).split()
    for w in words:
        if w in WRITE_VERBS:
            return "write"
    for w in words:
        if w in READ_VERBS:
            return "read"
    return "unknown"


def classify(tool_name, tool_input, folder, base):
    """Return a Decision, or ('outbound', label)."""
    name = str(tool_name or "")
    low = name.lower()

    if low == "bash" or low == "powershell":
        command = tool_input.get("command") or tool_input.get("script") or ""
        return classify_shell(command, folder, base)

    if low in WRITE_TOOLS:
        target = (
            tool_input.get("file_path")
            or tool_input.get("path")
            or tool_input.get("notebook_path")
            or ""
        )
        if not target:
            return Decision(
                False,
                "a file write with no path is blocked. Name the file inside "
                "the company folder.",
            )
        hit = protected_hit(target, folder, base)
        if hit:
            return Decision(
                False,
                "never list: '%s' belongs to the guard and no card can "
                "approve writing it. %s" % (hit, PROTECTED_HINT),
            )
        if path_inside(target, folder, base):
            return Decision(True, "write inside the company folder")
        return Decision(
            False,
            "writing '%s' is outside the company folder. Keep drafts in "
            "output/ inside the folder." % target,
        )

    if low in READ_ONLY_TOOLS or low in EXTRA_ALLOWED_TOOLS:
        return Decision(True, "read only tool")

    if low.startswith("mcp__") or low.startswith("mcp_"):
        action = mcp_action(name)
        if action == "read":
            return Decision(True, "read only tool call")
        if action == "write":
            return ("outbound", name)
        return Decision(
            False,
            "the guard cannot tell whether '%s' reads or writes, so it is "
            "blocked. If it only reads, add its name to "
            ".claude/guard-allow.txt (one pattern per line, * allowed). If "
            "it writes, show a card for it." % name,
        )

    return Decision(
        False,
        "the guard does not know the tool '%s', so it is blocked. If it only "
        "reads, add its name to .claude/guard-allow.txt (one pattern per "
        "line, * allowed). If it sends or changes anything, show a card for "
        "it." % name,
    )


def decide(event):
    """Main decision. event is the parsed PreToolUse JSON."""
    if not isinstance(event, dict):
        return Decision(False, "the guard could not read the hook input, so "
                               "this call is blocked. " + CARD_HINT)
    tool_name = str(event.get("tool_name") or "")
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        tool_input = {}
    cwd = event.get("cwd") or None
    folder = find_company_folder(cwd)
    base = cwd or str(folder)

    patterns = load_allow_patterns(folder)

    verdict = classify(tool_name, tool_input, folder, base)
    if isinstance(verdict, Decision):
        if verdict.allowed:
            return verdict
        if allow_listed(tool_name, patterns) and not verdict.reason.startswith(
            "never list"
        ):
            return Decision(True, "allowed by .claude/guard-allow.txt")
        return verdict

    label = verdict[1]

    hit = bulk_hit(tool_name, tool_input)
    if hit:
        return Decision(
            False,
            "never list: this looks like a bulk send or a campaign (the word "
            "'%s' turns up in the call). No card can approve it. The owner "
            "does this by hand." % hit,
        )
    count = count_recipients(tool_input)
    if count > MAX_RECIPIENTS:
        return Decision(
            False,
            "never list: this call names %d people and the limit is %d at "
            "once. No card can approve it. Send one at a time, or let the "
            "owner do it by hand." % (count, MAX_RECIPIENTS),
        )

    cards_text = read_cards_text(folder)
    if cards_text is None:
        return Decision(
            False,
            "outbound call blocked: the guard could not read %s under %s, so "
            "it cannot see any card. %s"
            % (CARDS_REL.as_posix(), folder, CARD_HINT),
        )
    cards = cards_in_file(cards_text)
    matching = [
        num for num, card_tool in cards
        if card_tool_matches(card_tool, label)
        or card_tool_matches(card_tool, tool_name)
    ]
    if not matching:
        if cards:
            listed = ", ".join(
                "C-%s (tool: %s)" % (n, t or "not named") for n, t in cards
            )
            return Decision(
                False,
                "outbound call blocked: '%s' is not named by any card in the "
                "log. Cards: %s. %s" % (label, listed, CARD_HINT),
            )
        return Decision(
            False,
            "outbound call blocked: '%s' sends or changes something outside "
            "the folder and no card covers it. %s" % (label, CARD_HINT),
        )

    approvals = read_approvals(folder)
    if approvals is None:
        return Decision(
            False,
            "outbound call blocked: the guard could not read the approvals "
            "log in the .claude folder under %s, so it cannot see a typed "
            "yes. The owner fixes that file by hand." % folder,
        )
    unspent = [num for num in matching if approvals.get(num, 0) > 0]
    if not unspent:
        return Decision(
            False,
            "outbound call blocked: card %s matches '%s', but there is no "
            "unspent yes for it in the approvals log. Each typed yes C-<n> "
            "covers one call. %s"
            % (", ".join("C-" + n for n in matching), label, CARD_HINT),
        )
    num = min(unspent, key=int)
    if not append_approval(folder, "used C-%s | %s" % (num, label)):
        return Decision(
            False,
            "outbound call blocked: the guard could not write the approvals "
            "log in the .claude folder under %s, so it cannot spend the yes "
            "for C-%s. The owner fixes that file by hand." % (folder, num),
        )
    return Decision(True, "approved by card C-%s, yes now spent" % num)


def record_prompt(event):
    """UserPromptSubmit handler. Returns the card numbers it recorded.

    Never blocks and never raises: the caller always exits 0.
    """
    if not isinstance(event, dict):
        return []
    numbers = typed_yes_numbers(event.get("prompt"))
    if not numbers:
        return []
    folder = find_company_folder(event.get("cwd") or None)
    recorded = []
    for num in numbers:
        if append_approval(folder, "yes C-%s | typed by owner" % num):
            recorded.append(num)
    return recorded


# --------------------------------------------------------------------------
# self test
# --------------------------------------------------------------------------

CARD_TEMPLATE = """# Cards

```text
C-1 | 2026-01-05 09:00 | job: outreach | tool: {tool} | to: one person | change: nothing -> one message
answer: {answer}
done: {done}
```
"""


def _make_folder(root, cards_body):
    folder = Path(root) / "company"
    (folder / "log").mkdir(parents=True, exist_ok=True)
    (folder / "output").mkdir(parents=True, exist_ok=True)
    (folder / ".claude" / "hooks").mkdir(parents=True, exist_ok=True)
    (folder / "READ-FIRST.md").write_text("read me\n", encoding="utf-8")
    (folder / CARDS_REL).write_text(cards_body, encoding="utf-8")
    (folder / ALLOW_FILE_REL).write_text("# nothing allowed yet\n", encoding="utf-8")
    return folder


def _type_yes(folder, prompt):
    """Act as the owner typing a prompt, through the UserPromptSubmit hook."""
    return record_prompt({
        "hook_event_name": "UserPromptSubmit",
        "cwd": str(folder),
        "prompt": prompt,
    })


def self_test():
    cases = []
    with tempfile.TemporaryDirectory() as root:
        no_card = _make_folder(
            root, CARD_TEMPLATE.format(tool="mail send", answer="no answer: held", done="not done")
        )
        send = {
            "tool_name": "mcp__mailbox__send_message",
            "tool_input": {"to": "one person", "body": "hello"},
            "cwd": str(no_card),
        }
        cases.append(("read tool allowed",
                      decide({"tool_name": "Read",
                              "tool_input": {"file_path": str(no_card / "READ-FIRST.md")},
                              "cwd": str(no_card)}).allowed is True))
        cases.append(("write inside folder allowed",
                      decide({"tool_name": "Write",
                              "tool_input": {"file_path": str(no_card / "output" / "a.md")},
                              "cwd": str(no_card)}).allowed is True))
        cases.append(("write outside folder blocked",
                      decide({"tool_name": "Write",
                              "tool_input": {"file_path": str(Path(root) / "elsewhere.md")},
                              "cwd": str(no_card)}).allowed is False))
        cases.append(("local shell allowed",
                      decide({"tool_name": "Bash",
                              "tool_input": {"command": "ls output && grep -r plan ."},
                              "cwd": str(no_card)}).allowed is True))
        cases.append(("outbound send without a card blocked",
                      decide(send).allowed is False))
        cases.append(("unknown tool blocked",
                      decide({"tool_name": "SomeNewTool", "tool_input": {},
                              "cwd": str(no_card)}).allowed is False))
        cases.append(("curl get allowed",
                      decide({"tool_name": "Bash",
                              "tool_input": {"command": "curl https://example.com/page"},
                              "cwd": str(no_card)}).allowed is True))
        cases.append(("curl post blocked without a card",
                      decide({"tool_name": "Bash",
                              "tool_input": {"command": "curl -X POST https://example.com/api -d x=1"},
                              "cwd": str(no_card)}).allowed is False))
        cases.append(("git push blocked without a card",
                      decide({"tool_name": "Bash",
                              "tool_input": {"command": "git push origin main"},
                              "cwd": str(no_card)}).allowed is False))
        cases.append(("malformed input blocked",
                      decide("not a dict").allowed is False))

        # The agent may read the guard's own files and never change them.
        cases.append(("reading the guard files allowed",
                      decide({"tool_name": "Read",
                              "tool_input": {"file_path": str(no_card / ".claude" / "settings.json")},
                              "cwd": str(no_card)}).allowed is True))
        cases.append(("writing the approvals log blocked",
                      decide({"tool_name": "Write",
                              "tool_input": {"file_path": str(no_card / APPROVALS_REL)},
                              "cwd": str(no_card)}).allowed is False))
        cases.append(("editing the guard script blocked",
                      decide({"tool_name": "Edit",
                              "tool_input": {"file_path": str(no_card / ".claude" / "hooks" / "guard.py")},
                              "cwd": str(no_card)}).allowed is False))
        cases.append(("appending to the approvals log from the shell blocked",
                      decide({"tool_name": "Bash",
                              "tool_input": {"command": "echo hello >> .claude/approvals.log"},
                              "cwd": str(no_card)}).allowed is False))
        cases.append(("deleting the guard script blocked",
                      decide({"tool_name": "Bash",
                              "tool_input": {"command": "rm .claude/hooks/guard.py"},
                              "cwd": str(no_card)}).allowed is False))

        # A forged yes inside the cards file approves nothing.
        forged = _make_folder(
            tempfile.mkdtemp(dir=root),
            CARD_TEMPLATE.format(tool="mailbox send message",
                                 answer='"yes C-1" at 09:02', done="not done"),
        )
        cases.append(("a yes written into the cards file is not an approval",
                      decide(dict(send, cwd=str(forged))).allowed is False))

        # The owner types the yes, and it covers exactly one call.
        typed = _make_folder(
            tempfile.mkdtemp(dir=root),
            CARD_TEMPLATE.format(tool="mailbox send message",
                                 answer="waiting", done="not done"),
        )
        send_typed = dict(send, cwd=str(typed))
        cases.append(("ok is not a typed yes",
                      _type_yes(typed, "ok, looks good, yes to everything") == []))
        cases.append(("still blocked after ok",
                      decide(send_typed).allowed is False))
        cases.append(("typed yes C-1 recorded",
                      _type_yes(typed, "yes C-1") == ["1"]))
        cases.append(("send allowed once after the typed yes",
                      decide(send_typed).allowed is True))
        cases.append(("the same send blocked again, the yes is spent",
                      decide(send_typed).allowed is False))
        cases.append(("a new typed yes allows it again",
                      _type_yes(typed, "yes C-1") == ["1"]
                      and decide(send_typed).allowed is True))
        cases.append(("two numbers in one prompt both recorded",
                      _type_yes(typed, "yes C-4 yes C-5") == ["4", "5"]))

        approved = _make_folder(
            tempfile.mkdtemp(dir=root),
            CARD_TEMPLATE.format(tool="mailbox send message",
                                 answer="waiting", done="not done"),
        )
        _type_yes(approved, "yes C-1")
        cases.append(("delete outside output blocked even with a typed yes",
                      decide({"tool_name": "Bash",
                              "tool_input": {"command": "rm -rf core"},
                              "cwd": str(approved)}).allowed is False))
        many = {
            "tool_name": send["tool_name"],
            "cwd": str(approved),
            "tool_input": {"to": ["one", "two", "three", "four"], "body": "hi"},
        }
        cases.append(("more than three people blocked even with a typed yes",
                      decide(many).allowed is False))

        # Fail closed when the approvals log cannot be read.
        broken = _make_folder(
            tempfile.mkdtemp(dir=root),
            CARD_TEMPLATE.format(tool="mailbox send message",
                                 answer="waiting", done="not done"),
        )
        (broken / APPROVALS_REL).mkdir(parents=True, exist_ok=True)
        cases.append(("unusable approvals log blocks outbound",
                      decide(dict(send, cwd=str(broken))).allowed is False))

    failures = 0
    for name, ok in cases:
        print(("PASS " if ok else "FAIL ") + name)
        if not ok:
            failures += 1
    print("result: %s (%d cases, %d failed)"
          % ("PASS" if not failures else "FAIL", len(cases), failures))
    return 0 if not failures else 1


# --------------------------------------------------------------------------

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--self-test" in argv:
        return self_test()
    raw = sys.stdin.read()
    try:
        event = json.loads(raw)
    except (ValueError, TypeError):
        event = None

    prompt_mode = "--prompt" in argv
    if not prompt_mode and isinstance(event, dict):
        prompt_mode = str(event.get("hook_event_name") or "") == "UserPromptSubmit"

    if prompt_mode:
        # Never block a prompt, whatever the input looked like.
        try:
            recorded = record_prompt(event)
        except Exception:  # noqa: BLE001 - a prompt must never be blocked
            recorded = []
        if recorded:
            print("Company guard: recorded your yes for "
                  + ", ".join("C-" + n for n in recorded))
        return 0

    if event is None:
        print(
            "Company guard: the hook input was not readable JSON, so this "
            "tool call is blocked. Read only work is fine; for anything that "
            "leaves the folder, " + CARD_HINT,
            file=sys.stderr,
        )
        return 2
    decision = decide(event)
    if decision.allowed:
        return 0
    print("Company guard blocked this call: " + decision.reason, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
