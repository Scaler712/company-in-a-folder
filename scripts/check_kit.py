#!/usr/bin/env python3
"""Validate the company-in-a-folder repository. Standard library only.

Checks:
  1. skills      every SKILL.md has frontmatter; name matches its folder;
                 kit skills (skills/) have a description containing "Use when".
  2. paths       every file path a kit markdown file mentions in backticks or
                 in a markdown link exists (placeholders like <x> are skipped).
  3. denylist    no private names, email addresses, key-shaped strings or IP
                 addresses anywhere in the repository.
  4. style       no em dashes in kit-owned text (marketing-os/ is vendored).

Usage:
    python3 scripts/check_kit.py [--root PATH]
Exit code 0 on PASS, 1 on any FAIL.
"""
from __future__ import annotations

import argparse
import codecs
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
VENDORED = "marketing-os"
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}

# Denylist terms are stored rot13-encoded so this file does not trip its own scan.
_DENY_ROT13 = [
    "xevfgvna", "puevfgvna", "gvrfarf", "ersf", "nwp", "ynan", "znvxf",
    "bhgcebqhpr", "urval", "urezrmn", "urgmare", "nggvb", "gbqbvfg",
    "nelna", "pbqlap", "xabk", "evtn",
    "pragehf", "whzvf", "cnfpvb", "mneb", "fhatb", "ybamb", "tyvgpul", "qbgxva", "znpuvan", "fgryb", "xrrgba", "purqvq", "betb", "nccnevf",
]
DENY_TERMS = [codecs.decode(t, "rot13") for t in _DENY_ROT13]

# Allowed exceptions: git ref paths in archive URLs, e.g. archive/<r>/heads/main.zip
_REF_EXCEPTION = "/heads/"

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}")
KEY_RE = re.compile(r"\b" + "s" + r"k-[A-Za-z0-9_\-]{16,}")
IP_RE = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
EM_DASH = "\u2014"

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
BACKTICK_RE = re.compile(r"`([^`\s]+)`")
MDLINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
PATH_EXTS = (".md", ".py", ".json", ".txt", ".csv", ".yml", ".yaml")
PLACEHOLDER_MARKS = ("<", ">", "{", "}", "YYYY", "*", "[", "]")
# Files the owner creates after copying the template; mentioned but not shipped.
OWNER_CREATED = {"AGENTS.md", "CLAUDE.md"}


def iter_files(root: Path):
    for p in sorted(root.rglob("*")):
        if p.is_file() and not any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            yield p


def read_text(p: Path):
    try:
        return p.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def parse_frontmatter(text: str):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*)$", line)
        if m:
            fields[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    return fields


def check_skills(root: Path) -> list[str]:
    problems = []
    kit_skills = sorted((root / "skills").glob("*/SKILL.md")) if (root / "skills").is_dir() else []
    if not kit_skills:
        problems.append("skills/: no SKILL.md files found")
    vendored = []
    vroot = root / VENDORED
    if vroot.is_dir():
        vendored = sorted(vroot.glob("skills/*/SKILL.md"))
        if (vroot / "SKILL.md").is_file():
            vendored.append(vroot / "SKILL.md")
    for path in kit_skills + vendored:
        rel = path.relative_to(root)
        fm = parse_frontmatter(read_text(path) or "")
        if fm is None:
            problems.append(f"{rel}: missing or broken frontmatter")
            continue
        name, desc = fm.get("name", ""), fm.get("description", "")
        folder = path.parent.name
        if name != folder:
            problems.append(f"{rel}: name '{name}' does not match folder '{folder}'")
        if not NAME_RE.match(name) or len(name) > 64:
            problems.append(f"{rel}: name must be lowercase-hyphen, max 64 chars")
        if not desc:
            problems.append(f"{rel}: empty description")
        elif len(desc) > 1024:
            problems.append(f"{rel}: description over 1024 chars")
        if path in kit_skills and "use when" not in desc.lower():
            problems.append(f"{rel}: description must say 'Use when ...'")
        if path in vendored and not desc.lower().startswith("use"):
            problems.append(f"{rel}: vendored description should say when to use it")
    return problems


def _looks_like_path(token: str) -> bool:
    if token.startswith(("http://", "https://", "mailto:", "#")):
        return False
    if any(m in token for m in PLACEHOLDER_MARKS):
        return False
    if token.startswith(("-", "$", ".claude/settings")):
        return False
    return token.endswith(PATH_EXTS) or (token.endswith("/") and "/" in token)


def _resolve(token: str, md_file: Path, root: Path) -> bool:
    token = token.split("#", 1)[0]
    if not token:
        return True
    if Path(token).name in OWNER_CREATED and "/" not in token.rstrip("/"):
        return True
    template = root / "company-template"
    candidates = [md_file.parent / token, template / token, root / token]
    if token.startswith(".claude/skills/"):
        candidates.append(root / "skills" / token[len(".claude/skills/"):])
    return any(c.exists() for c in candidates)


def check_paths(root: Path) -> list[str]:
    problems = []
    for p in iter_files(root):
        rel = p.relative_to(root)
        if rel.parts[0] == VENDORED or p.suffix != ".md":
            continue
        text = read_text(p) or ""
        tokens = set(BACKTICK_RE.findall(text)) | set(MDLINK_RE.findall(text))
        for tok in sorted(tokens):
            if _looks_like_path(tok) and not _resolve(tok, p, root):
                problems.append(f"{rel}: path not found: {tok}")
    return problems


def scan_text(text: str):
    """Return a list of (kind, match) hits in text."""
    hits = []
    lowered = text.lower()
    for term in DENY_TERMS:
        for m in re.finditer(r"\b" + re.escape(term) + r"\b", lowered):
            if lowered.startswith(_REF_EXCEPTION, m.end()):
                continue
            hits.append(("name", text[m.start():m.end()]))
    hits += [("email", m) for m in EMAIL_RE.findall(text)]
    hits += [("key", m) for m in KEY_RE.findall(text)]
    hits += [("ip", m) for m in IP_RE.findall(text)]
    return hits


def check_denylist(root: Path) -> list[str]:
    problems = []
    for p in iter_files(root):
        rel = p.relative_to(root)
        for kind, hit in scan_text(str(rel)):
            problems.append(f"{rel}: {kind} in file name: {hit}")
        text = read_text(p)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for kind, hit in scan_text(line):
                problems.append(f"{rel}:{lineno}: {kind}: {hit}")
    return problems


def check_style(root: Path) -> list[str]:
    problems = []
    for p in iter_files(root):
        rel = p.relative_to(root)
        if rel.parts[0] == VENDORED:
            continue
        text = read_text(p)
        if text and EM_DASH in text:
            for lineno, line in enumerate(text.splitlines(), 1):
                if EM_DASH in line:
                    problems.append(f"{rel}:{lineno}: em dash")
    return problems


CHECKS = [
    ("skills", check_skills),
    ("paths", check_paths),
    ("denylist", check_denylist),
    ("style", check_style),
]


def run(root: Path, out=sys.stdout) -> int:
    root = root.resolve()
    failed = 0
    for label, fn in CHECKS:
        problems = fn(root)
        if problems:
            failed += 1
            print(f"FAIL {label} ({len(problems)})", file=out)
            for line in problems:
                print(f"  - {line}", file=out)
        else:
            print(f"PASS {label}", file=out)
    print(f"result: {'FAIL' if failed else 'PASS'}", file=out)
    return 1 if failed else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Validate the company-in-a-folder repository.")
    parser.add_argument("--root", default=str(DEFAULT_ROOT), help="repository root to check")
    args = parser.parse_args(argv)
    return run(Path(args.root))


if __name__ == "__main__":
    sys.exit(main())
