#!/usr/bin/env python
"""PROCESS check (gating): the workflow produced a non-empty solution deliverable.

This check BITES. It walks the agent's ``workspace/`` -- EXCLUDING the corpus copy
under ``.claude/`` and the engine's ``.agent-work/`` -- for a non-empty Python
solution file, and, as the run's minimal deliverable-of-record, the completion
sentinel ``eval-complete.txt`` the workflow writes ONLY as its final step. It FAILs
(non-zero) if neither exists non-empty. The runner's ``--dry-run-fail`` broken
workspace has neither (only a ``BROKEN.txt`` marker), so this check FAILs it.

Contract note (scripts/run_skill_eval.py): ``--dry-run`` synthesizes the sentinel as
the "stub artifact" but no solution file, so the sentinel is the accepted stand-in at
the agent-free FLOOR; a live run's real ``solution.py`` is validated by the primary
branch below. The residual "sentinel written without a real solution" hole is exactly
what the g5 live broken-variant CEILING covers -- not this floor.

Usage: ``python artifact_present.py <run-dir>``  ->  exit 0 pass / non-zero fail.
"""
from __future__ import annotations

import sys
from pathlib import Path

EXCLUDED_PARTS = {".claude", ".git", ".agent-work"}
SENTINEL = "eval-complete.txt"


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
    sentinel = workspace / SENTINEL
    if sentinel.is_file() and sentinel.stat().st_size > 0:
        print(
            f"PASS artifact_present: completion sentinel {SENTINEL} present "
            f"(final-step deliverable-of-record / dry-run stub)"
        )
        return 0
    print("FAIL artifact_present: no non-empty solution .py and no completion sentinel in workspace")
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("FAIL artifact_present: missing <run-dir> argument")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
