#!/usr/bin/env python
"""ADVISORY answer check -- NEVER gates the verdict (structural T3).

The runner executes, records, and prints this, but the verdict gate reads ONLY
``checks/*.py`` (process). ``checks/answer/*.py`` can NEVER move the verdict. This
exists to show answer-correctness is recorded but weak-never-sufficient: a corpus
that prints the right number while botching the workflow still FAILs on the process
checks; this line is diagnostic only.

It tries to run any solution file in the workspace and check its stdout for the
known answer, else scans workspace text/data files for it.

Usage: ``python answer_matches.py <run-dir>``  (exit code is informational only).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

KNOWN_ANSWER = "233168"  # Project Euler #1: sum of multiples of 3 or 5 below 1000
EXCLUDED_PARTS = {".claude", ".git", ".agent-work"}
SCAN_SUFFIXES = {".txt", ".md", ".json", ".out", ".log", ".csv"}


def _run_solutions(workspace: Path) -> bool:
    for p in sorted(workspace.rglob("*.py")):
        rel = p.relative_to(workspace)
        if EXCLUDED_PARTS & set(rel.parts):
            continue
        name = p.name.lower()
        if name.startswith("test_") or name.endswith("_test.py"):
            continue
        try:
            proc = subprocess.run(
                [sys.executable, str(p)],
                cwd=str(workspace),
                capture_output=True,
                text=True,
                timeout=30,
            )
        except Exception:
            continue
        if KNOWN_ANSWER in (proc.stdout or ""):
            return True
    return False


def _scan_files(workspace: Path) -> bool:
    for p in sorted(workspace.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(workspace)
        if EXCLUDED_PARTS & set(rel.parts):
            continue
        if p.suffix.lower() not in SCAN_SUFFIXES:
            continue
        try:
            if KNOWN_ANSWER in p.read_text(encoding="utf-8", errors="ignore"):
                return True
        except OSError:
            continue
    return False


def main(run_dir_arg: str) -> int:
    workspace = Path(run_dir_arg) / "workspace"
    found = workspace.is_dir() and (_run_solutions(workspace) or _scan_files(workspace))
    if found:
        print(f"ADVISORY answer_matches: known answer {KNOWN_ANSWER} observed (advisory, non-gating)")
        return 0
    print(f"ADVISORY answer_matches: known answer {KNOWN_ANSWER} not observed (advisory, non-gating)")
    return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ADVISORY answer_matches: missing <run-dir> argument (advisory, non-gating)")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
