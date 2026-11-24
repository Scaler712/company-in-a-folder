#!/usr/bin/env python3
"""Build SKILLS.md and evals/triggers.json from the skill files.

Reads departments.json (which department each skill sits in) and the
frontmatter of every skills/<name>/SKILL.md. Writes:

  SKILLS.md              one table per department: skill, what it does
  evals/triggers.json    the phrases each skill says it should fire on

Run with --check to fail (exit 1) when the files on disk are out of date,
when a skill is missing from departments.json, listed twice, or listed but
absent, when a skill has fewer than two trigger phrases, or when two skills
claim the same phrase.

Usage:
    python3 scripts/build_index.py [--check] [--root PATH]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent
QUOTE_RE = re.compile(r'"([^"\n]{3,80})"')


def read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    block = text[3:end] if end != -1 else ""
    out: dict = {}
    key = None
    for line in block.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key = m.group(1)
            out[key] = m.group(2).strip()
        elif key and line.startswith((" ", "\t")):
            out[key] = (out[key] + " " + line.strip()).strip()
    for k, v in out.items():
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            out[k] = v[1:-1]
        if v in (">", "|", ">-", "|-"):
            out[k] = ""
    return out


def first_sentence(description: str) -> str:
    text = description.strip()
    cut = text.find(" Use when")
    if cut != -1:
        text = text[:cut]
    m = re.search(r"(?<=[.!?])\s", text)
    if m:
        text = text[: m.start()]
    text = text.strip().rstrip(".").replace("|", "/")
    if len(text) > 150:
        cut = text.rfind(", ", 0, 150)
        if cut > 60:
            text = text[:cut]
    return text


def triggers(description: str) -> list[str]:
    cut = description.find("Use when")
    tail = description[cut:] if cut != -1 else ""
    seen: list[str] = []
    for phrase in QUOTE_RE.findall(tail):
        p = phrase.strip().lower().rstrip(".,")
        if p and p not in seen:
            seen.append(p)
    return seen


def collect(root: Path) -> tuple[dict, dict, list[str]]:
    problems: list[str] = []
    departments = json.loads((root / "departments.json").read_text(encoding="utf-8"))
    on_disk = sorted(p.parent.name for p in (root / "skills").glob("*/SKILL.md"))
    listed: list[str] = [s for names in departments.values() for s in names]
    for name in on_disk:
        if listed.count(name) == 0:
            problems.append(f"skill not in departments.json: {name}")
        elif listed.count(name) > 1:
            problems.append(f"skill listed more than once in departments.json: {name}")
    for name in listed:
        if name not in on_disk:
            problems.append(f"departments.json names a skill that does not exist: {name}")
    info: dict = {}
    for name in on_disk:
        fm = read_frontmatter(root / "skills" / name / "SKILL.md")
        desc = fm.get("description", "")
        info[name] = {"summary": first_sentence(desc), "triggers": triggers(desc)}
        if len(info[name]["triggers"]) < 2:
            problems.append(f"fewer than two quoted trigger phrases after 'Use when': {name}")
    owner: dict = {}
    for name, data in info.items():
        for phrase in data["triggers"]:
            if phrase in owner and owner[phrase] != name:
                problems.append(f"trigger phrase claimed by two skills: '{phrase}' ({owner[phrase]}, {name})")
            owner[phrase] = name
    return departments, info, problems


def render_skills_md(departments: dict, info: dict) -> str:
    total = sum(len(v) for v in departments.values())
    lines = [
        "# Skills",
        "",
        f"{total} jobs, grouped by the part of the business each one runs. "
        "Built from the skill files by `scripts/build_index.py`, so it cannot drift from them.",
        "",
    ]
    for dept, names in departments.items():
        lines += [f"## {dept}", "", "| Job | What it does |", "|---|---|"]
        for name in names:
            summary = info.get(name, {}).get("summary", "")
            lines.append(f"| `{name}` | {summary} |")
        lines.append("")
    return "\n".join(lines)


def render_triggers(departments: dict, info: dict) -> str:
    data = {
        "about": "Phrases each skill says it should fire on, taken from its description. "
        "Use them to test that your agent picks the right skill.",
        "skills": {name: info[name]["triggers"] for names in departments.values() for name in names if name in info},
    }
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build SKILLS.md and evals/triggers.json.")
    parser.add_argument("--check", action="store_true", help="fail if files are out of date or the index has problems")
    parser.add_argument("--root", type=Path, default=KIT_ROOT)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    departments, info, problems = collect(root)
    outputs = {
        root / "SKILLS.md": render_skills_md(departments, info),
        root / "evals" / "triggers.json": render_triggers(departments, info),
    }
    if args.check:
        for path, text in outputs.items():
            if not path.is_file() or path.read_text(encoding="utf-8") != text:
                problems.append(f"out of date, run scripts/build_index.py: {path.relative_to(root)}")
    else:
        for path, text in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
    for p in problems:
        print("  - " + p)
    print(f"skills: {len(info)}  departments: {len(departments)}  result: {'FAIL' if problems else 'PASS'}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
