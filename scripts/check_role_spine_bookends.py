#!/usr/bin/env python
"""Lint: every role spine template declares at least one bookend, and the
repo's declaration matches what is actually installed.

Mitigation for form B's silent-permissive failure (#567, lane K + lane L).
`checklist_engine.py::_is_bookend()` reads a missing `bookend` key as NOT a
bookend -- deliberately, so a plan authored before bookends existed keeps
working. That same permissive default means a role spine template that
*meant* to declare bookends but never got installed is silently unprotected:
`init_work_area.py` mints spines from the INSTALLED copy, not the repo copy,
so a repo edit to a template's bookend declarations does nothing until the
corpus is reinstalled. This script is a corpus check, not a runtime refusal
-- it never touches `_is_bookend()` or its default, and a plan with no
declaration still reads as not-a-bookend at runtime exactly as before.

Two triggers:
  1. UNDECLARED -- a role spine template (repo-relative
     skills/<name>/templates/*_SPINE.template.json) declares zero
     "bookend": true tasks.
  2. DRIFT -- a template that DOES declare bookends, where the installed
     copy's bookend task-id set differs from the repo's (including the
     installed copy being entirely absent, which reads as an empty set --
     the worst case of drift).

Scope: role spine templates only (matched by the *_SPINE.template.json glob
under skills/*/templates/). Not every template in the corpus -- that is a
larger, differently-shaped check `check_skill_freshness.py` already covers
for a PROJECT's local/baseline/upstream templates. That script has no notion
of "this repo's own skill source vs. the installed corpus" and no manifest
for it (it drives off a project's `.agent-work/templates/TEMPLATES_MANIFEST.json`,
which this repo -- the skill source itself -- has no reason to carry), so its
three-way machinery does not fit this shape; this script is intentionally a
small standalone rather than a forced reuse.

CLI: `check_role_spine_bookends.py --repo-root PATH --skills-root PATH`

Exit codes:
  0  every role spine template declares >=1 bookend and matches the installed copy
  1  at least one template is undeclared or drifted (report printed)
  2  REFUSED -- a template could not be read/parsed at all
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


class LintError(Exception):
    pass


def _bookend_ids(tasks: dict) -> set[str]:
    if not isinstance(tasks, dict):
        raise LintError("template's 'tasks' must be an object")
    return {tid for tid, task in tasks.items() if isinstance(task, dict) and task.get("bookend")}


def _load_tasks(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LintError(f"{path}: cannot read/parse -- {exc}") from exc
    return data.get("tasks", {})


def _installed_skill_name(repo_skill_dir: str) -> str:
    """skills/commander -> constellation-commander. A repo skill directory
    name is never itself prefixed (the installed corpus adds the prefix at
    install time), so this mapping is unconditional."""
    return f"constellation-{repo_skill_dir}"


def check(repo_root: Path, skills_root: Path) -> list[dict[str, str]]:
    """One row per role spine template found in the repo. `status` is one of
    'ok', 'undeclared', 'drift', 'installed-missing'."""
    rows: list[dict[str, str]] = []
    for template in sorted((repo_root / "skills").glob("*/templates/*_SPINE.template.json")):
        repo_skill_dir = template.relative_to(repo_root / "skills").parts[0]
        installed_skill = _installed_skill_name(repo_skill_dir)
        installed_path = skills_root / installed_skill / "templates" / template.name

        repo_bookends = _bookend_ids(_load_tasks(template))

        if not repo_bookends:
            rows.append({
                "template": str(template.relative_to(repo_root)),
                "status": "undeclared",
                "detail": "declares zero bookend tasks",
            })
            continue

        if not installed_path.is_file():
            rows.append({
                "template": str(template.relative_to(repo_root)),
                "status": "installed-missing",
                "detail": f"repo declares {sorted(repo_bookends)}, "
                          f"no installed copy at {installed_path}",
            })
            continue

        installed_bookends = _bookend_ids(_load_tasks(installed_path))
        if installed_bookends != repo_bookends:
            rows.append({
                "template": str(template.relative_to(repo_root)),
                "status": "drift",
                "detail": f"repo={sorted(repo_bookends)} installed={sorted(installed_bookends)}",
            })
            continue

        rows.append({
            "template": str(template.relative_to(repo_root)),
            "status": "ok",
            "detail": f"bookends {sorted(repo_bookends)} match installed",
        })
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument(
        "--skills-root", type=Path, required=True,
        help="Installed skills directory containing constellation-* skill folders",
    )
    args = parser.parse_args(argv)

    try:
        rows = check(args.repo_root.resolve(), args.skills_root)
    except LintError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not rows:
        print("no role spine templates found under skills/*/templates/*_SPINE.template.json")
        return 0

    offenders = [row for row in rows if row["status"] != "ok"]
    for row in rows:
        marker = " " if row["status"] == "ok" else "!"
        print(f"{marker} {row['status']:<18} {row['template']} -- {row['detail']}")

    if offenders:
        print(f"\n{len(offenders)} role spine template(s) undeclared or drifted from the installed corpus.")
        return 1
    print(f"\nall {len(rows)} role spine template(s) declare bookends and match the installed corpus")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
