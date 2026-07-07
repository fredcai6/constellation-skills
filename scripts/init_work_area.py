#!/usr/bin/env python
"""Scaffold a Constellation work area: .agent-work/<work-id>/ and its subdirs.

Optionally instantiate spine.json from a named spine template, resolving the
commander placeholders so the result is immediately runnable by the engine.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SUBDIRS = ["crew-handoffs", "evidence", "triage-candidates"]


def init_work_area(root: Path, work_id: str) -> Path:
    base = root / ".agent-work" / work_id
    for sub in [""] + SUBDIRS:
        (base / sub).mkdir(parents=True, exist_ok=True)
    return base


def resolve_spine(template_text: str, work_id: str, skill_dir: str | None, root: Path) -> str:
    """Resolve commander placeholders in a spine template's text.

    - ``<commander-skill-dir>`` -> ``skill_dir`` when given. When omitted,
      auto-detect the source-repo layout (bundled scripts at ``<root>/scripts``)
      and collapse the token form ``<commander-skill-dir>/scripts`` -> ``scripts``
      so the init command references the real top-level script path.
    - ``<commander-session-id>`` -> ``commander-<work-id>`` (the conventional default).
    - ``<work-id>`` -> the work_id argument (all occurrences).
    """
    text = template_text
    if skill_dir is not None:
        text = text.replace("<commander-skill-dir>", skill_dir)
    else:
        if (root / "scripts").is_dir():
            # Bundled scripts live at the repo top level; skill-dir == repo root.
            text = text.replace("<commander-skill-dir>/scripts", "scripts")
        # Any remaining bare token resolves to the repo root.
        text = text.replace("<commander-skill-dir>", ".")
    text = text.replace("<commander-session-id>", f"commander-{work_id}")
    text = text.replace("<work-id>", work_id)
    return text


def instantiate_spine(
    root: Path,
    work_id: str,
    template: Path,
    skill_dir: str | None = None,
    force: bool = False,
) -> Path | None:
    """Write .agent-work/<work-id>/spine.json from ``template`` with placeholders resolved.

    Returns the written path, or ``None`` when an existing spine.json is left
    intact because ``force`` was not passed.
    """
    base = init_work_area(root, work_id)
    dest = base / "spine.json"
    if dest.exists() and not force:
        print(f"spine.json already exists (in-progress run state); pass --force to overwrite: {dest}")
        return None
    resolved = resolve_spine(template.read_text(encoding="utf-8"), work_id, skill_dir, root)
    # Fail visibly if resolution produced invalid JSON rather than writing a broken spine.
    json.loads(resolved)
    dest.write_text(resolved, encoding="utf-8")
    return dest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("work_id")
    parser.add_argument("--root", default=".")
    parser.add_argument("--spine", help="path to a spine template to instantiate into spine.json")
    parser.add_argument("--skill-dir", dest="skill_dir", help="value for <commander-skill-dir> (auto-detected if omitted)")
    parser.add_argument("--force", action="store_true", help="overwrite an existing spine.json")
    args = parser.parse_args(argv)
    root = Path(args.root)
    base = init_work_area(root, args.work_id)
    print(f"work area ready: {base}")
    if args.spine:
        dest = instantiate_spine(root, args.work_id, Path(args.spine), args.skill_dir, args.force)
        if dest is not None:
            print(f"spine ready: {dest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
