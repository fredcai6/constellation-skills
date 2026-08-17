"""C3 — the table's cases are unchanged: same ids, same expectations.

The handoff calls a diff of the `CASES` list the cheapest proof, so this is that
diff, made mechanical: the `CASES = [` ... `]` block plus `_CASE_IDS`, taken from
HEAD's copy of the file and from the working tree, compared byte for byte.

It also compares the EVALUATED table -- ids and expected values, as the cases
actually resolve on this platform -- because a byte-identical block whose helper
functions changed would still be a changed specification.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = "tests/test_worktree_derivation.py"
START = "CASES = ["
END = "_CASE_IDS = [case[0] for case in CASES]"


def head_source() -> str:
    out = subprocess.run(["git", "show", f"HEAD:{TARGET}"], cwd=ROOT,
                         capture_output=True, text=True, check=True)
    return out.stdout


def block(source: str) -> str:
    start = source.index(START)
    end = source.index(END) + len(END)
    return source[start:end]


def evaluated(source: str, tag: str):
    """Evaluate the table in its own definitional context, nothing else.

    HEAD's copy of this file cannot simply be imported any more -- it resolves
    `checklist_engine.worktree_from_spine_path`, which is the very symbol this
    gate deleted, so `_require` fails its import by design. That is the deletion
    test passing, not an obstacle to route around: so evaluate only what decides
    what the cases ARE -- `_ROOT`, `_FOLDS_CASE`, `_path`, `_expected` and the
    `CASES` list itself -- and never the implementation bindings.
    """
    head_marker = "# An absolute root to build cases under."
    segment = "import os\n\n" + source[source.index(head_marker):
                                       source.index(END) + len(END)]
    namespace: dict = {}
    exec(compile(segment, f"<cases:{tag}>", "exec"), namespace)   # noqa: S102
    return [(c[0], c[1], c[2]) for c in namespace["CASES"]]


def main() -> int:
    working = (ROOT / TARGET).read_text(encoding="utf-8")
    head = head_source()

    same_text = block(head) == block(working)
    print(f"CASES block, HEAD vs working tree: byte-identical = {same_text} "
          f"({len(block(working))} characters)")

    head_cases = evaluated(head, "head")
    work_cases = evaluated(working, "working")
    print(f"cases evaluated: HEAD {len(head_cases)}, working tree {len(work_cases)}")
    same_eval = head_cases == work_cases
    print(f"ids and expectations identical = {same_eval}")

    if not (same_text and same_eval):
        for a, b in zip(head_cases, work_cases):
            if a != b:
                print(f"FAIL: case changed: {a} -> {b}", file=sys.stderr)
        print("FAIL: the CASES table is not unchanged", file=sys.stderr)
        return 1
    print("\nOK: same ids, same expectations, same bytes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
