#!/usr/bin/env python
"""Lint: every declared `context_refs` path must appear verbatim in its own
task's `imperative` prose.

`scripts/context_manifest.py` (the authority on the `context_refs` shape) is
committed and approved, and its module docstring explains the design: a
declaration entry is `{"root", "path", "required"}`, and the task's
`imperative` prose is deliberately kept alongside it rather than replaced,
because the prose carries rules a path list cannot express -- e.g. the
COMMANDER_SPINE `context` step's substitute-and-record rule, and "a missing
engine-config is a sanctioned degradation, do NOT create the overlay file."

This script is the mechanical guard that keeps the two from drifting apart:
for every task that declares `context_refs`, every declared `path` string
must occur verbatim inside that same task's `imperative` string, as a whole
path token -- a match is not accepted when it is merely a suffix of a longer,
different path in the prose (see `_appears_at_path_boundary`).

**Direction, stated honestly.** This catches exactly one failure shape: the
declaration naming a path its own prose never mentions -- a declaration that
has been retargeted, mistyped, or extended past the prose that justifies it.
It CANNOT catch the reverse -- a path quietly dropped from `context_refs`
while the prose still names it (the declaration silently *narrowing away*
from what the prose describes) -- because the imperative is free-form prose,
not a parseable list, and there is no reliable way to extract "the paths this
sentence claims to read" from it. The declaration is authoritative; the prose
is the human-readable explanation of it. This lint does not claim to
guarantee agreement in both directions: it only guarantees that no declared
path points somewhere its own prose is silent about.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

#: Kept as a local literal, not imported from `context_manifest.py`: this lint
#: is a read-only consumer of the same JSON shape, and the two scripts are
#: deliberately not coupled beyond that shared, documented key name.
DECLARATION_KEY = "context_refs"

#: Where the real, shipped checklist templates live -- used only by the
#: no-args discovery path; an explicit path list on the command line bypasses
#: this entirely.
DEFAULT_GLOB = "skills/*/templates/*.json"

#: A character that can appear inside a path token. Used to decide whether
#: the character immediately BEFORE a candidate match is itself part of a
#: longer path -- if it is, the match is a suffix of that longer path, not a
#: standalone occurrence of the declared path, and does not count.
_PATH_CHAR = re.compile(r"[A-Za-z0-9_./\\-]")

#: Trailing continuation characters. Deliberately excludes `.`: a `.`
#: immediately after a match is ambiguous on its own (it could continue the
#: path as an extension, e.g. `GLOSSARY.md` + `.bak`, or be ordinary
#: sentence-ending punctuation, e.g. `GLOSSARY.md` + `. Attest c1.`) --
#: `_bounded_after` resolves that ambiguity by looking one character further.
_TRAILING_CONTINUATION_CHAR = re.compile(r"[A-Za-z0-9_/\\-]")


def _bounded_after(prose: str, end: int) -> bool:
    """True when nothing immediately after `prose[:end]` continues the path
    token that ends there. End-of-string always qualifies. A `.` is special:
    it qualifies (does NOT continue the path) only when the character past it
    is not alphanumeric -- `.` then alnum is an extension glued onto the
    match (a real `.bak`/`.old`/`.tmp` sibling file); `.` then anything else,
    or nothing, is ordinary sentence punctuation."""
    if end >= len(prose):
        return True
    ch = prose[end]
    if ch == ".":
        nxt = prose[end + 1] if end + 1 < len(prose) else ""
        return not nxt.isalnum()
    return not _TRAILING_CONTINUATION_CHAR.match(ch)


def _appears_at_path_boundary(path: str, prose: str) -> bool:
    """True when `path` occurs in `prose` as a whole path token, not merely as
    a substring of a longer, different path. A match counts only when it is
    bounded at BOTH ends: the character immediately preceding it -- start-of-
    string, whitespace, a quote, a backtick, or `(` all qualify -- is not
    itself a path character, AND nothing immediately after it continues the
    path (see `_bounded_after` for the `.`-disambiguation). This catches a
    declared `agents/GLOSSARY.md` wrongly matching inside prose's
    `docs/agents/GLOSSARY.md` (leading side), and a declared
    `docs/agents/GLOSSARY.md` wrongly matching inside prose's
    `docs/agents/GLOSSARY.md.bak` (trailing side) -- the same defect class,
    a declared path resolving to a DIFFERENT file than the prose names, seen
    from either end."""
    start = 0
    while True:
        idx = prose.find(path, start)
        if idx == -1:
            return False
        leading_ok = idx == 0 or not _PATH_CHAR.match(prose[idx - 1])
        trailing_ok = _bounded_after(prose, idx + len(path))
        if leading_ok and trailing_ok:
            return True
        start = idx + 1


def _is_checklist(data: object) -> bool:
    """True for anything shaped like a checklist (`gated` or `survey`) this
    lint can meaningfully walk: an `items` list and a `tasks` mapping. Plenty
    of `skills/*/templates/*.json` files are NOT checklists at all (engine
    config, finding templates, issue-set templates) and must be skipped
    rather than mis-parsed."""
    return (
        isinstance(data, dict)
        and isinstance(data.get("items"), list)
        and isinstance(data.get("tasks"), dict)
    )


def offenders_in_task(task: dict) -> list[str]:
    """Declared paths in `task` that do not appear verbatim in its own
    `imperative` string. Empty means the task is clean, including the normal
    case of carrying no declaration at all."""
    declared = task.get(DECLARATION_KEY)
    if not declared:
        return []
    prose = task.get("imperative")
    if not isinstance(prose, str):
        prose = ""
    missing = []
    for entry in declared:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            missing.append(repr(entry))
            continue
        path = entry["path"]
        if not _appears_at_path_boundary(path, prose):
            missing.append(path)
    return missing


def check_checklist(data: dict, source: str = "<checklist>") -> list[str]:
    """One human-readable problem string per (task, offending path). Empty
    means every task's declaration agrees with its own prose."""
    problems: list[str] = []
    tasks = data.get("tasks")
    if not isinstance(tasks, dict):
        return problems
    for task_id, task in tasks.items():
        if not isinstance(task, dict):
            continue
        for path in offenders_in_task(task):
            problems.append(
                f"{source}: task {task_id!r} declares context_refs path {path!r} "
                f"that does not appear verbatim in its own imperative prose"
            )
    return problems


def discover_templates(root: Path) -> list[Path]:
    """Every real, committed checklist template under `root` -- never sorted
    by anything but path, and never a reason on its own to skip a file; a file
    that fails to parse is still reported, not silently dropped."""
    return sorted(root.glob(DEFAULT_GLOB))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "paths", nargs="*", type=Path,
        help="checklist JSON files to check (default: every skills/*/templates/*.json checklist)",
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="project root (default cwd)")
    args = parser.parse_args(argv)

    targets = args.paths if args.paths else discover_templates(args.root)
    if not targets:
        print(f"no checklist templates found under {args.root / 'skills'}", file=sys.stderr)
        return 1

    all_problems: list[str] = []
    checked = 0
    for path in targets:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            all_problems.append(f"{path}: could not read ({exc})")
            continue
        try:
            data = json.loads(text)
        except ValueError as exc:
            all_problems.append(f"{path}: unparseable JSON ({exc})")
            continue
        if not _is_checklist(data):
            continue
        checked += 1
        all_problems.extend(check_checklist(data, source=str(path)))

    if all_problems:
        print("context_refs declaration diverges from imperative prose:", file=sys.stderr)
        for problem in all_problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print(f"context declaration lint ok: {checked} checklist(s) checked, 0 offenders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
