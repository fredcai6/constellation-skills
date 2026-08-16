"""C4 — the case table's module docstring states what is now true.

It must no longer describe two implementations pinned equal, and it must say:
one lexical rule, one implementation, in the stdlib-only hook; the table is the
rule's SPECIFICATION; the engine-side copy was deleted in #609 g2 under
`ADMIRAL_RULING-2` N2 and re-lands in #610's wave with #315, its consumer, which
re-derives against this table.

Read from the parsed module docstring, not from a grep over the file, so a
matching sentence somewhere else in the file cannot satisfy it.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TARGET = ROOT / "tests" / "test_worktree_derivation.py"

REQUIRED = {
    "one-rule-one-implementation": r"one lexical rule and one implementation",
    "lives-in-the-stdlib-only-hook": r"stdlib-only hook",
    "names-the-survivor": r"_worktree_from_spine",
    "table-is-the-specification": r"specifies the worktree-derivation rule",
    "deleted-here": r"deleted in #609 g2",
    "under-the-ruling": r"admiral_ruling-2 n2",
    "re-lands-with-its-consumer": r"re-lands in #610's wave together with #315",
    "re-derives-against-this-table": r"re-derives against these cases",
    "why-a-copy-not-an-import": r"may gain no import",
}

# The retired claims, in the present tense the docstring used to carry them in.
# A future-tense sentence about the copies being pinned equal AGAIN is correct
# and must not be caught here.
FORBIDDEN = {
    "two-implementations-exist": r"there are deliberately two implementations",
    "table-pins-two-copies": r"pinning the two worktree-derivation copies equal",
    "must-drive-both": r"must drive both copies",
    "engine-consumes-it": r"the definition the engine consumes",
}


def main() -> int:
    source = TARGET.read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(source))
    if not doc:
        print("FAIL: no module docstring", file=sys.stderr)
        return 1
    blob = re.sub(r"[*`]", "", re.sub(r"\s+", " ", doc)).lower()

    failures = []
    for name, pattern in REQUIRED.items():
        if not re.search(pattern, blob):
            failures.append(f"missing required clause '{name}' (/{pattern}/)")
    for name, pattern in FORBIDDEN.items():
        if re.search(pattern, blob):
            failures.append(f"retired claim still present '{name}' (/{pattern}/)")

    # "Any guard that loops must assert what it looped over" (CREW_CONTEXT).
    print(f"checked {len(REQUIRED)} required and {len(FORBIDDEN)} forbidden clauses "
          f"against a {len(doc)}-character module docstring")
    if failures:
        for line in failures:
            print(f"FAIL: {line}", file=sys.stderr)
        return 1
    print("OK: the docstring describes one rule, one implementation, and the re-landing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
