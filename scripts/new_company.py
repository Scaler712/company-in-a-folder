#!/usr/bin/env python3
"""Create a new company folder from company-template/.

Usage:
    python3 scripts/new_company.py /absolute/path/to/my-company [--no-skills]
    python3 scripts/new_company.py /absolute/path/to/demo --demo

The folder gets AGENTS.md and CLAUDE.md as exact copies of READ-FIRST.md, so
Codex and Claude Code load the rules on their own. It also gets the guard in
`.claude/` (hooks, settings.json, guard-allow.txt), with `--demo` too. With
--demo the filled example in demo-company/ is copied instead of the empty
template. An approvals log is never copied: each folder earns its own.

The folder must be OUTSIDE this repository. Your company facts belong in a
private place, never in a clone you might publish. Standard library only.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = KIT_ROOT / "company-template"
DEMO = KIT_ROOT / "demo-company"
AGENT_FILES = ("AGENTS.md", "CLAUDE.md")
SKILLS = KIT_ROOT / "skills"
# The guard the template ships in .claude/. Demo folders get the same files.
GUARD_PARTS = ("hooks", "settings.json", "guard-allow.txt")
# Never copied into a new folder: approvals belong to one folder only.
NEVER_COPY = ("approvals.log",)


def is_inside(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _drop_never_copied(folder: Path) -> None:
    """Remove files a new company folder must never inherit."""
    for name in NEVER_COPY:
        for path in folder.rglob(name):
            if path.is_file():
                path.unlink()


def _copy_guard(source_claude: Path, target_claude: Path) -> None:
    """Put hooks/, settings.json and guard-allow.txt in place if missing."""
    if not source_claude.is_dir():
        return
    for name in GUARD_PARTS:
        src = source_claude / name
        dest = target_claude / name
        if not src.exists() or dest.exists():
            continue
        target_claude.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dest)
        else:
            shutil.copyfile(src, dest)


def create_company(
    target: Path,
    with_skills: bool = True,
    kit_root: Path = KIT_ROOT,
    demo: bool = False,
) -> list[Path]:
    """Copy the template (and skills) to target. Returns the files written.

    With demo=True the filled example in demo-company/ is the source instead of
    company-template/. Raises ValueError with a plain message when the target is
    not allowed or the source folder is missing.
    """
    kit_root = kit_root.resolve()
    template = kit_root / ("demo-company" if demo else "company-template")
    skills = kit_root / "skills"
    target = target.expanduser().resolve()

    if not template.is_dir():
        if demo:
            raise ValueError(
                f"demo company not found: {template}. The filled example lives in "
                "demo-company/ at the root of the kit. Drop --demo to use the empty template."
            )
        raise ValueError(f"template not found: {template}")
    if is_inside(target, kit_root):
        raise ValueError(
            f"refusing to create the company folder inside the kit ({kit_root}). "
            "Pick a private path outside this repository."
        )
    if is_inside(kit_root, target):
        raise ValueError("refusing: the target contains the kit. Pick a new, empty folder.")
    if target.exists() and any(target.iterdir()):
        raise ValueError(f"refusing: {target} already exists and is not empty.")

    target.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, target, dirs_exist_ok=True)
    _drop_never_copied(target)

    # The guard ships with company-template/.claude/. A demo folder that has
    # none of it gets the same hooks, settings and allow file.
    _copy_guard(kit_root / "company-template" / ".claude", target / ".claude")

    rules = target / "READ-FIRST.md"
    if rules.is_file():
        for name in AGENT_FILES:
            shutil.copyfile(rules, target / name)

    # The tool maps the jobs point at (for example tools/autoady.md).
    tools = kit_root / "tools"
    if tools.is_dir():
        shutil.copytree(tools, target / "tools", dirs_exist_ok=True)

    if with_skills:
        # dirs_exist_ok on the skills copy only, so the hooks stay in place.
        dest = target / ".claude" / "skills"
        dest.mkdir(parents=True, exist_ok=True)
        for skill_dir in sorted(p for p in skills.iterdir() if (p / "SKILL.md").is_file()):
            shutil.copytree(skill_dir, dest / skill_dir.name, dirs_exist_ok=True)

    return sorted(p for p in target.rglob("*") if p.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a company folder from the AI OS template.")
    parser.add_argument("target", help="absolute path for the new company folder, outside this repository")
    parser.add_argument("--no-skills", action="store_true", help="do not copy skills into .claude/skills/")
    parser.add_argument("--demo", action="store_true", help="copy the filled example in demo-company/ instead of the empty template")
    args = parser.parse_args(argv)

    try:
        files = create_company(Path(args.target), with_skills=not args.no_skills, demo=args.demo)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    target = Path(args.target).expanduser().resolve()
    print(f"company folder created: {target}")
    print(f"files written: {len(files)}")
    print("")
    print("next:")
    print(f"  1. cd {target}")
    print("  2. open that folder in your AI tool (Claude Code, Codex, or another)")
    print('  3. say "start"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
