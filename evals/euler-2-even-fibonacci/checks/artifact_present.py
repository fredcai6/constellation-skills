#!/usr/bin/env python
"""PROCESS check (gating): the workflow produced a non-empty solution deliverable.

This check BITES STRICTLY. It walks the agent's ``workspace/`` -- EXCLUDING the
corpus copy under ``.claude/`` and the engine's ``.agent-work/`` -- for a non-empty
Python solution file, and FAILs (non-zero) if none exists. There is NO completion-
sentinel fallback (issue #115 tc1): the sentinel is written as the workflow's LAST
step and could be present with no real solution behind it, so accepting it as a
stand-in was the "sentinel written without a real solution" hole. A run must now
produce a real ``solution.py`` to pass, not merely stamp the sentinel. The runner's
``--dry-run`` synthesizes a real ``solution.py`` (so this bites on it); ``--dry-run
-fail`` (only a ``BROKEN.txt`` marker) FAILs.

Usage: ``python artifact_present.py <run-dir>``  ->  exit 0 pass / non-zero fail.
"""
from __future__ import annotations

import sys
from pathlib import Path

EXCLUDED_PARTS = {".claude", ".git", ".agent-work"}


def _is_test_file(rel: Path) -> bool:
    name = rel.name.lower()
    if name.startswith("test_") or name.endswith("_test.py"):
        return True
    return any(part.lower() == "tests" for part in rel.parts[:-1])


def find_solution(workspace: Path) -> Path | None:
    for p in sorted(workspace.rglob("*.py")):
        if not p.is_file():
            continue
        rel = p.relative_to(workspace)
        if EXCLUDED_PARTS & set(rel.parts):
            continue
        if _is_test_file(rel):
            continue
        if p.stat().st_size > 0:
            return p
    return None


def main(run_dir_arg: str) -> int:
    workspace = Path(run_dir_arg) / "workspace"
    if not workspace.is_dir():
        print("FAIL artifact_present: no workspace/ under <run-dir>")
        return 1
    sol = find_solution(workspace)
    if sol is not None:
        print(f"PASS artifact_present: non-empty solution file {sol.relative_to(workspace)}")
        return 0
    print("FAIL artifact_present: no non-empty solution .py in workspace")
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("FAIL artifact_present: missing <run-dir> argument")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
