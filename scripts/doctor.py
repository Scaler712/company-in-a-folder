#!/usr/bin/env python3
"""Health check one company folder. Read only, no network, standard library only.

Usage:
    python3 scripts/doctor.py /path/to/my-company [--today YYYY-MM-DD] [--json]

It prints a score out of 100, the findings grouped by urgency, and exactly one
recommended next step. It never writes, edits or sends anything.

Scoring (100 points in total):

  10  agent-files            AGENTS.md and CLAUDE.md exist and are byte
                             identical to READ-FIRST.md.
  30  placeholders           one finding per file in core/, scored by how many
                             "[fill in" markers are left. Weights:
                             clients.md 12, business.md 6, pricing-and-limits.md 5,
                             people.md 3, priorities.md 2, open-questions.md 2.
                             A file with 0 markers left scores its full weight,
                             5 or more markers scores 0, in between is linear.
  10  turn-down              the "Who we turn down" section of core/clients.md
                             has at least 2 filled lines.
   5  priorities-count       core/priorities.md lists at most 3 numbered items.
   8  priorities-fresh       its "Last updated" date is no more than 14 days
                             before today.
  10  email-samples          communication/emails-i-sent.md has at least 5
                             voice samples.
  10  skills-installed       at least 2 .claude/skills/<job>/SKILL.md files.
   5  held-cards             no card in log/cards.md is older than 3 days with
                             no answer and no readback.
   5  decisions-due          no entry in decisions.md is past its check date
                             with an empty "actual" line.
   5  secrets                no key-shaped string, password line or card-number
                             shaped digit run in any text file. Any hit caps
                             the whole score at 50.
   2  git-remote             the folder is not inside a git repository that has
                             a remote. A remote is a warning, not a failure:
                             make sure that remote is private.

Heuristics, chosen after reading the template and READ-FIRST.md:

  Cards. A card block starts at a line like "C-7 | 2027-03-02 10:15 | job: ..."
  or "CARD C-7 | ...", with a real number (the fenced example in the template
  uses C-<n> and is ignored). The block runs to the next card header. The first
  YYYY-MM-DD in the header is the card date. The card counts as answered when an
  "answer:" or "done:" line carries a real value (yes, no, changed, or a
  readback), or when the block holds a standalone "yes C-7", "no C-7" or
  "done C-7" line. Empty values, values still in <angle brackets>, "not done"
  and "no answer" all count as unanswered. Unanswered plus a date more than 3
  days before today is a held card.

  Decisions. An entry starts at "## D-3 | 2027-02-20 | ...". Its check date is
  the first YYYY-MM-DD after "check on:". It is overdue when that date is on or
  before today and the "actual" line has no real value.

  Email samples. Primary count: "## " headings in
  communication/emails-i-sent.md whose body holds at least one real line, so
  "[paste]" and "[fill in" bodies do not count. If the file has no headings at
  all, blank-line separated blocks of at least 40 characters are counted
  instead, skipping the intro block. The report says which of the two it used.

Exit codes: 0 when the check ran, whatever the score. 2 on a usage error or
when the path is not a company folder.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

CORE_WEIGHTS = {
    "clients.md": 12.0,
    "business.md": 6.0,
    "pricing-and-limits.md": 5.0,
    "people.md": 3.0,
    "priorities.md": 2.0,
    "open-questions.md": 2.0,
}
PLACEHOLDER = "[fill in"
PLACEHOLDER_FULL_LOSS = 5  # this many markers left scores no points
STALE_DAYS = 14
HELD_CARD_DAYS = 3
MIN_EMAIL_SAMPLES = 5
MIN_SKILLS = 2
SECRETS_SCORE_CAP = 50

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules"}
DATE_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
NUMBERED_RE = re.compile(r"^\s{0,3}(\d+)\.\s+\S")
CARD_HEAD_RE = re.compile(r"^\s*(?:CARD\s+)?C-(\d+)\s*\|")
DECISION_HEAD_RE = re.compile(r"^\s*#{0,3}\s*D-(\d+)\s*\|")
FIELD_RE = re.compile(r"^\s*([A-Za-z][A-Za-z ()]*?)\s*:\s*(.*)$")

# Built at runtime so this file does not carry a key-shaped string itself.
KEY_RE = re.compile(r"\b" + "s" + r"k-[A-Za-z0-9_\-]{16,}")
SECRET_WORD_RE = re.compile(
    r"(?i)\b(?:pass(?:word|phrase)|api[_-]?key|secret[_-]?key|access[_-]?token)"
    r"\s*[:=]\s*[^\s\[<][^\s]{7,}"
)
DIGIT_RUN_RE = re.compile(r"(?<![\d\-])(?:\d[ \-]?){13,19}(?!\d)")
URL_RE = re.compile(r"https?://\S+")

ORDER = ["fail", "warn", "pass"]
GROUP_TITLES = {"fail": "Fix first", "warn": "Then", "pass": "Fine"}


class NotACompanyFolder(ValueError):
    """The path is missing READ-FIRST.md or core/."""


def read_text(path: Path) -> str:
    """Return the file text, or an empty string when it cannot be read."""
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return ""


def iter_text_files(root: Path):
    """Yield every readable text file under root, skipping tool folders."""
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        yield path


def tidy(number: float):
    """Round to one decimal, and to a plain int when it is whole."""
    number = round(float(number), 1)
    return int(number) if number == int(number) else number


def finding(fid: str, status: str, points: float, max_points: float, detail: str) -> dict:
    return {
        "id": fid,
        "status": status,
        "points": tidy(points),
        "max": tidy(max_points),
        "detail": detail,
    }


def count_placeholders(text: str) -> int:
    return text.count(PLACEHOLDER)


def first_date(text: str) -> date | None:
    match = DATE_RE.search(text)
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def is_real_value(value: str) -> bool:
    """True when a field value is filled in rather than left as a placeholder."""
    value = value.strip()
    if not value:
        return False
    if value.startswith("<") or value.startswith("["):
        return False
    lowered = value.lower()
    if lowered in {"none", "n/a", "tbd", "not done", "no answer"}:
        return False
    return not lowered.startswith(("not done", "no answer"))


def section(text: str, title: str) -> list[str]:
    """Return the lines under a '## <title>' heading, up to the next heading."""
    lines = text.splitlines()
    out: list[str] = []
    inside = False
    for line in lines:
        if line.startswith("#"):
            if inside:
                break
            inside = line.strip("# ").strip().lower() == title.lower()
            continue
        if inside:
            out.append(line)
    return out


def check_agent_files(root: Path) -> dict:
    rules = (root / "READ-FIRST.md").read_bytes()
    missing = [name for name in ("AGENTS.md", "CLAUDE.md") if not (root / name).is_file()]
    if missing:
        return finding(
            "agent-files", "fail", 0, 10,
            "missing " + " and ".join(missing) + ", so most AI tools load no rules at all",
        )
    differs = [
        name for name in ("AGENTS.md", "CLAUDE.md")
        if (root / name).read_bytes() != rules
    ]
    if differs:
        return finding(
            "agent-files", "fail", 0, 10,
            " and ".join(differs) + " differ from READ-FIRST.md, so tools read different rules",
        )
    return finding("agent-files", "pass", 10, 10, "AGENTS.md and CLAUDE.md match READ-FIRST.md")


def check_placeholders(root: Path) -> list[dict]:
    out = []
    for name, weight in sorted(CORE_WEIGHTS.items(), key=lambda kv: (-kv[1], kv[0])):
        path = root / "core" / name
        rel = f"core/{name}"
        if not path.is_file():
            out.append(finding(f"placeholders:{rel}", "fail", 0, weight, f"{rel} is missing"))
            continue
        left = count_placeholders(read_text(path))
        if left == 0:
            out.append(finding(f"placeholders:{rel}", "pass", weight, weight, f"{rel} has no placeholders left"))
            continue
        ratio = max(0.0, 1.0 - left / float(PLACEHOLDER_FULL_LOSS))
        status = "warn" if left <= 2 else "fail"
        plural = "" if left == 1 else "s"
        out.append(finding(
            f"placeholders:{rel}", status, weight * ratio, weight,
            f"{rel} still has {left} '{PLACEHOLDER}' marker{plural}",
        ))
    return out


def check_turn_down(root: Path) -> dict:
    path = root / "core" / "clients.md"
    if not path.is_file():
        return finding("turn-down", "fail", 0, 10, "core/clients.md is missing")
    lines = section(read_text(path), "Who we turn down")
    filled = [
        line.strip() for line in lines
        if line.strip().startswith(("-", "*")) and PLACEHOLDER not in line and len(line.strip()) > 10
    ]
    if len(filled) >= 2:
        return finding("turn-down", "pass", 10, 10, f"{len(filled)} turn-down lines a bot can quote")
    return finding(
        "turn-down", "fail", 0, 10,
        f"'Who we turn down' in core/clients.md has {len(filled)} filled line(s), it needs at least 2",
    )


def check_priorities(root: Path, today: date) -> list[dict]:
    path = root / "core" / "priorities.md"
    if not path.is_file():
        return [
            finding("priorities-count", "fail", 0, 5, "core/priorities.md is missing"),
            finding("priorities-fresh", "fail", 0, 8, "core/priorities.md is missing"),
        ]
    text = read_text(path)
    numbered = [line for line in text.splitlines() if NUMBERED_RE.match(line)]
    if len(numbered) <= 3:
        count = finding("priorities-count", "pass", 5, 5, f"{len(numbered)} numbered priorities, 3 is the cap")
    else:
        count = finding(
            "priorities-count", "fail", 0, 5,
            f"{len(numbered)} numbered priorities in core/priorities.md, the cap is 3",
        )

    updated = None
    for line in text.splitlines():
        if line.lower().lstrip("*- ").startswith("last updated"):
            updated = first_date(line)
            break
    if updated is None:
        fresh = finding("priorities-fresh", "fail", 0, 8, "core/priorities.md has no 'Last updated' date")
    else:
        age = (today - updated).days
        if age <= STALE_DAYS:
            fresh = finding("priorities-fresh", "pass", 8, 8, f"priorities updated {age} day(s) ago")
        else:
            fresh = finding(
                "priorities-fresh", "fail", 0, 8,
                f"priorities last updated {age} days ago, every bot is working on old priorities",
            )
    return [count, fresh]


def count_email_samples(text: str) -> tuple[int, str]:
    """Return (samples, how they were counted). Tolerant of two layouts."""
    lines = text.splitlines()
    heads = [i for i, line in enumerate(lines) if line.startswith("## ")]
    if heads:
        samples = 0
        bounds = heads + [len(lines)]
        for start, end in zip(heads, bounds[1:]):
            body = [
                line.strip() for line in lines[start + 1:end]
                if line.strip() and line.strip() != "[paste]" and PLACEHOLDER not in line
            ]
            if body:
                samples += 1
        return samples, "'## ' sections with pasted text under them"
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    return max(0, len([b for b in blocks[1:] if len(b) >= 40])), "blank-line separated blocks of 40+ characters"


def check_emails(root: Path) -> dict:
    path = root / "communication" / "emails-i-sent.md"
    if not path.is_file():
        return finding("email-samples", "fail", 0, 10, "communication/emails-i-sent.md is missing")
    samples, how = count_email_samples(read_text(path))
    detail = f"counted {samples} email sample(s) in communication/emails-i-sent.md ({how})"
    if samples >= MIN_EMAIL_SAMPLES:
        return finding("email-samples", "pass", 10, 10, detail)
    status = "warn" if samples >= 2 else "fail"
    return finding("email-samples", status, 0, 10, detail + f", at least {MIN_EMAIL_SAMPLES} are needed")


def check_skills(root: Path) -> dict:
    installed = sorted(p.parent.name for p in (root / ".claude" / "skills").glob("*/SKILL.md"))
    if len(installed) >= MIN_SKILLS:
        return finding("skills-installed", "pass", 10, 10, f"{len(installed)} skills installed under .claude/skills/")
    return finding(
        "skills-installed", "fail", 0, 10,
        f"{len(installed)} skill(s) under .claude/skills/, at least {MIN_SKILLS} are needed",
    )


def parse_cards(text: str) -> list[dict]:
    """Split log/cards.md into card blocks. See the module docstring."""
    lines = text.splitlines()
    heads = [(i, m) for i, m in ((i, CARD_HEAD_RE.match(line)) for i, line in enumerate(lines)) if m]
    starts = [i for i, _ in heads]
    cards = []
    bounds = starts + [len(lines)]
    for (start, head), end in zip(heads, bounds[1:]):
        block = lines[start:end]
        number = head.group(1)
        answered = False
        for line in block:
            match = FIELD_RE.match(line)
            if match and match.group(1).strip().lower() in {"answer", "done"}:
                if is_real_value(match.group(2)):
                    answered = True
            stripped = line.strip().lower()
            if re.match(r"^(yes|no|done)\s+c-" + number + r"\b", stripped):
                answered = True
        cards.append({"number": number, "date": first_date(block[0]), "answered": answered})
    return cards


def check_cards(root: Path, today: date) -> dict:
    path = root / "log" / "cards.md"
    if not path.is_file():
        return finding("held-cards", "warn", 0, 5, "log/cards.md is missing, no card history to read")
    cards = parse_cards(read_text(path))
    held = [
        c for c in cards
        if not c["answered"] and c["date"] is not None and (today - c["date"]).days > HELD_CARD_DAYS
    ]
    if not held:
        return finding("held-cards", "pass", 5, 5, f"{len(cards)} card(s) logged, none held over {HELD_CARD_DAYS} days")
    names = ", ".join("C-" + c["number"] for c in held)
    return finding(
        "held-cards", "fail", 0, 5,
        f"{len(held)} card(s) shown over {HELD_CARD_DAYS} days ago with no yes, no or done line: {names}",
    )


def parse_decisions(text: str) -> list[dict]:
    lines = text.splitlines()
    heads = [(i, m) for i, m in ((i, DECISION_HEAD_RE.match(line)) for i, line in enumerate(lines)) if m]
    starts = [i for i, _ in heads]
    out = []
    bounds = starts + [len(lines)]
    for (start, head), end in zip(heads, bounds[1:]):
        block = lines[start:end]
        number = head.group(1)
        check_on = None
        actual = ""
        for line in block:
            lowered = line.strip().lower()
            if lowered.startswith("check on"):
                check_on = first_date(line)
            elif lowered.startswith("actual"):
                actual = line.split(":", 1)[1] if ":" in line else ""
        out.append({"number": number, "check_on": check_on, "actual": is_real_value(actual)})
    return out


def check_decisions(root: Path, today: date) -> dict:
    path = root / "decisions.md"
    if not path.is_file():
        return finding("decisions-due", "warn", 0, 5, "decisions.md is missing")
    entries = parse_decisions(read_text(path))
    due = [e for e in entries if e["check_on"] is not None and e["check_on"] <= today and not e["actual"]]
    if not due:
        return finding("decisions-due", "pass", 5, 5, f"{len(entries)} decision(s) logged, none past its check date")
    names = ", ".join("D-" + e["number"] for e in due)
    return finding(
        "decisions-due", "fail", 0, 5,
        f"{len(due)} decision(s) past the check date with no actual result: {names}",
    )


def luhn_ok(digits: str) -> bool:
    """True when the digits pass the checksum real card numbers carry.

    Long ids in links and reference numbers are not card numbers. The
    checksum keeps those from being reported.
    """
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def scan_secrets(root: Path) -> list[str]:
    """Return 'path:line: kind' hits. The matched text is never included."""
    hits = []
    for path in iter_text_files(root):
        rel = path.relative_to(root)
        for lineno, line in enumerate(read_text(path).splitlines(), 1):
            kinds = []
            if KEY_RE.search(line):
                kinds.append("key-shaped string")
            if SECRET_WORD_RE.search(line):
                kinds.append("password or key line")
            for run in DIGIT_RUN_RE.findall(URL_RE.sub(" ", line)):
                digits = re.sub(r"[ \-]", "", run)
                if 13 <= len(digits) <= 19 and luhn_ok(digits):
                    kinds.append("card-number-shaped digits")
                    break
            for kind in kinds:
                hits.append(f"{rel}:{lineno}: {kind}")
    return hits


def check_secrets(root: Path) -> tuple[dict, list[str]]:
    hits = scan_secrets(root)
    if not hits:
        return finding("secrets", "pass", 5, 5, "no key-shaped string, password line or card number found"), hits
    shown = "; ".join(hits[:5])
    more = "" if len(hits) <= 5 else f" and {len(hits) - 5} more"
    return finding(
        "secrets", "fail", 0, 5,
        f"{len(hits)} possible secret(s), score capped at {SECRETS_SCORE_CAP}. "
        f"Move them to a credential store, then delete the line: {shown}{more}",
    ), hits


def find_git_remote(root: Path) -> tuple[Path | None, bool]:
    """Walk up for a git repo and say whether its config names a remote."""
    for folder in [root] + list(root.parents):
        gitdir = folder / ".git"
        if not gitdir.exists():
            continue
        config = gitdir / "config" if gitdir.is_dir() else None
        if config is None or not config.is_file():
            return folder, False
        has_remote = any(
            line.strip().startswith("[remote ") for line in read_text(config).splitlines()
        )
        return folder, has_remote
    return None, False


def check_git(root: Path) -> dict:
    folder, has_remote = find_git_remote(root)
    if folder is None:
        return finding("git-remote", "pass", 2, 2, "not inside a git repository")
    if not has_remote:
        return finding("git-remote", "pass", 2, 2, f"inside the git repository at {folder}, no remote configured")
    return finding(
        "git-remote", "warn", 0, 2,
        f"the git repository at {folder} has a remote. Make sure that remote is private: "
        "this folder holds your company facts",
    )


NEXT_STEP_TEXT = {
    "secrets": "Open the files named under 'secrets' and move every key, password and card number into your "
               "tools' own credential store, then delete the line.",
    "agent-files": "Copy the rules file to the names AI tools look for: cp READ-FIRST.md AGENTS.md && "
                   "cp READ-FIRST.md CLAUDE.md",
    "placeholders:core/clients.md": "Fill in core/clients.md. Dictate it: who you sell to, your best 3 clients "
                                    "and why, and who you turn down with a one-line reason each.",
    "turn-down": "Write at least 2 lines under 'Who we turn down' in core/clients.md, each one who plus the "
                 "reason, in words a bot can quote back.",
    "priorities-fresh": "Spend 5 minutes on core/priorities.md: at most 3 priorities for this month and today's "
                        "date on the 'Last updated' line.",
    "priorities-count": "Cut core/priorities.md back to at most 3 priorities and move the rest under 'Not now'.",
    "placeholders:core/business.md": "Fill in core/business.md so every bot starts from the same facts.",
    "placeholders:core/pricing-and-limits.md": "Fill in core/pricing-and-limits.md so no bot ever invents a price.",
    "email-samples": "Paste at least 5 real emails you wrote into communication/emails-i-sent.md, names removed, "
                     "your wording untouched.",
    "skills-installed": "Copy the skills you need into .claude/skills/<job>/SKILL.md, or rerun "
                        "scripts/new_company.py so it does it for you.",
    "held-cards": "Answer the held cards in log/cards.md with 'yes C-<n>' or 'no', or mark them held on purpose.",
    "decisions-due": "Fill the 'actual' line on the decisions that are past their check date, then keep, change "
                     "or drop each one.",
    "placeholders:core/people.md": "Fill in core/people.md, roles rather than names.",
    "placeholders:core/priorities.md": "Fill in core/priorities.md.",
    "placeholders:core/open-questions.md": "Clear core/open-questions.md: answer what you can, delete what no "
                                           "longer matters.",
    "git-remote": "Check that the git remote on this folder is a private repository, and move the folder out of "
                  "any public one.",
}
NEXT_STEP_ORDER = [
    "secrets",
    "agent-files",
    "placeholders:core/clients.md",
    "turn-down",
    "priorities-fresh",
    "placeholders:core/business.md",
    "placeholders:core/pricing-and-limits.md",
    "email-samples",
    "skills-installed",
    "held-cards",
    "decisions-due",
    "priorities-count",
    "placeholders:core/people.md",
    "placeholders:core/priorities.md",
    "placeholders:core/open-questions.md",
    "git-remote",
]


def pick_next_step(findings: list[dict]) -> str:
    by_id = {f["id"]: f for f in findings}
    for fid in NEXT_STEP_ORDER:
        item = by_id.get(fid)
        if item is not None and item["status"] != "pass":
            return NEXT_STEP_TEXT[fid]
    for item in findings:
        if item["status"] != "pass":
            return f"Look at {item['id']}: {item['detail']}"
    return "Nothing to fix. Run one real job today, such as process-a-lead, and stop at the card."


def run_doctor(root: Path, today: date) -> dict:
    """Score one company folder. Reads only. Raises NotACompanyFolder on a bad path."""
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise NotACompanyFolder(f"not a folder: {root}")
    if not (root / "READ-FIRST.md").is_file() or not (root / "core").is_dir():
        raise NotACompanyFolder(
            f"not a company folder: {root} has no READ-FIRST.md and core/. "
            "Create one with scripts/new_company.py, then point me at that folder."
        )

    findings: list[dict] = [check_agent_files(root)]
    findings += check_placeholders(root)
    findings.append(check_turn_down(root))
    findings += check_priorities(root, today)
    findings.append(check_emails(root))
    findings.append(check_skills(root))
    findings.append(check_cards(root, today))
    findings.append(check_decisions(root, today))
    secrets_finding, secrets_hits = check_secrets(root)
    findings.append(secrets_finding)
    findings.append(check_git(root))

    score = sum(f["points"] for f in findings)
    max_score = sum(f["max"] for f in findings)
    score = int(round(score))
    if secrets_hits:
        score = min(score, SECRETS_SCORE_CAP)
    return {
        "root": str(root),
        "today": today.isoformat(),
        "score": score,
        "max": int(round(max_score)),
        "findings": findings,
        "secret_hits": secrets_hits,
        "next_step": pick_next_step(findings),
    }


def format_report(result: dict) -> str:
    lines = [f"AI OS doctor: {result['score']}/{result['max']}", f"folder: {result['root']}"]
    for status in ORDER:
        group = [f for f in result["findings"] if f["status"] == status]
        if not group:
            continue
        lines.append("")
        lines.append(GROUP_TITLES[status])
        for item in group:
            lines.append(f"  - {item['detail']} ({item['points']}/{item['max']})")
    lines.append("")
    lines.append(f"Next step: {result['next_step']}")
    return "\n".join(lines)


def parse_today(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"--today must look like YYYY-MM-DD, got: {value}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Health check one company folder. Read only.")
    parser.add_argument("folder", help="path to the company folder to check")
    parser.add_argument("--today", default=None, help="treat this YYYY-MM-DD as today, for repeatable runs")
    parser.add_argument("--json", action="store_true", dest="as_json", help="print the result as JSON")
    args = parser.parse_args(argv)

    try:
        today = parse_today(args.today) if args.today else date.today()
        result = run_doctor(Path(args.folder), today)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.as_json:
        payload = {k: v for k, v in result.items() if k != "secret_hits"}
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(format_report(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
