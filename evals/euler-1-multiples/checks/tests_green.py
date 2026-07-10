#!/usr/bin/env python
"""PROCESS check (gating): tests were WRITTEN and PASS in the workspace.

This check BITES. It finds test files in the agent's ``workspace/`` -- EXCLUDING the
corpus copy under ``.claude/`` -- and, when any exist, RUNS pytest against exactly
those files (never the corpus) and requires green. When no test file exists it falls
back to the completion sentinel ``eval-complete.txt`` (the workflow writes it only
after its tests are green), so the agent-free ``--dry-run`` (sentinel present, no
tests) PASSes while ``--dry-run-fail`` (no sentinel, no tests) FAILs.

pytest is invoked with the discovered test paths ONLY, so a live run cannot
accidentally collect the bundled corpus tests under ``.claude/``.

Usage: ``python tests_green.py <run-dir>``  ->  exit 0 pass / non-zero fail.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

EXCLUDED_PARTS = {".claude", ".git", ".agent-work"}
SENTINEL = "eval-complete.txt"


def find_tests(workspace: Path) -> list[Path]:
    hits: list[Path] = []
    for p in sorted(workspace.rglob("*.py")):
        if not p.is_file():
            continue
        rel = p.relative_to(workspace)
        if EXCLUDED_PARTS & set(rel.parts):
            continue
        name = p.name.lower()
        is_test = (
            name.startswith("test_")
            or name.endswith("_test.py")
            or any(part.lower() == "tests" for part in rel.parts[:-1])
        )
        if is_test:
            hits.append(p)
    return hits


def run_pytest(workspace: Path, tests: list[Path]) -> int:
    args = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    # Absolute test paths: pytest runs with cwd=workspace, so a run-dir passed as a
    # RELATIVE path (e.g. a maintainer invoking the check by hand) would otherwise
    # resolve the test paths against workspace and mis-report exit 4 (usage error).
    args += [str(t.resolve()) for t in tests]
    proc = subprocess.run(args, cwd=str(workspace), capture_output=True, text=True)
    return proc.returncode


def main(run_dir_arg: str) -> int:
    workspace = Path(run_dir_arg) / "workspace"
    if not workspace.is_dir():
        print("FAIL tests_green: no workspace/ under <run-dir>")
        return 1
    tests = find_tests(workspace)
    if tests:
        rc = run_pytest(workspace, tests)
        if rc == 0:
            print(f"PASS tests_green: pytest green over {len(tests)} test file(s)")
            return 0
        print(f"FAIL tests_green: pytest exit {rc} over {len(tests)} test file(s)")
        return 1
    sentinel = workspace / SENTINEL
    if sentinel.is_file() and sentinel.stat().st_size > 0:
        print(
            f"PASS tests_green: no test file collected; completion sentinel "
            f"{SENTINEL} present (tests-green-then-sentinel convention / dry-run floor)"
        )
        return 0
    print("FAIL tests_green: no test file written and no completion sentinel")
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("FAIL tests_green: missing <run-dir> argument")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
