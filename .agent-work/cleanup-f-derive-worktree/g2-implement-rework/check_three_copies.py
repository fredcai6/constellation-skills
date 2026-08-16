"""C6 — the three hand-copied prose copies must carry the SAME narrowed claim.

The reviewer's Fowler pass flagged `duplicated-code`: this claim lives in three
files with nothing checking the copies, and "repairing it in one place and not
the other two is the concrete risk." This check is that missing comparison, run
as the m2-prose postcondition.

It normalizes each copy (lowercase, strip markdown emphasis and comment
markers, collapse whitespace) so the same sentence counts as present whether it
is wrapped as Markdown prose, a `#` comment block, or a docstring. Then:

  * every load-bearing clause of the narrowed claim must appear in ALL THREE;
  * every falsified sentence must appear in NONE.

Exit 0 = the three copies agree. Exit 1 = drift, naming the file and clause.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

COPIES = {
    "docs/CHECKLIST_SCHEMA.md": None,
    "scripts/checklist_engine.py": None,
    "tests/test_spine_origin_isolation.py": None,
}

# Each clause the Admiral's R1 requires the narrowed claim to carry.
REQUIRED = {
    "lease-qualifier": r"wherever a lease exists",
    "leaseless-population": r"no active lease",
    "never-or-released": r"never claimed, or claimed and since released",
    "is-a-widening": r"widen(ed|ing)",
    "widening-accepted": r"accepted",
    "forgeable-ne-absent": r"forgeable guard is not the same as no guard",
    "writes-into-foreign-tree": r"writing state into a tree the agent is not standing in",
    "active-lease-unchanged": r"active lease held by another session, nothing changed",
    "mechanism-named": r"require_session",
    "released-reads-absent": r"reads a released lease as absent",
    "supersession-kept": r"supersedes the 2026-08-15 worktree-identity ruling",
    # the engine header wraps this symbol mid-token across two comment lines
    "derivation-kept": r"worktree_from_spine_ ?path",
}

# The falsified sentences. Anchored so the NARROWED forms (which reuse the same
# opening words and then qualify them) do not count as a match.
FORBIDDEN = {
    "unqualified-no-guard": r"removed no guard\s*[.,]",
    "unqualified-nothing-unguarded-removal": r"nothing was left unguarded by that removal\s*[.,]",
    "unqualified-nothing-unguarded-removing": r"nothing was left unguarded by removing it\s*[:.]",
    "unqualified-always-was": r"ownership is the lease,? and (always was|was already)",
}


def normalize(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^\s*#+ ?", " ", text)   # `#` comment markers
    text = re.sub(r"[*`]", "", text)            # markdown emphasis; NOT `_`, which is in symbol names
    text = re.sub(r"\s+", " ", text)            # wrapping is not meaning
    return text.lower()


def main() -> int:
    failures: list[str] = []
    for name in COPIES:
        path = Path(name)
        if not path.is_file():
            failures.append(f"{name}: MISSING")
            continue
        blob = normalize(path)
        for clause, pattern in REQUIRED.items():
            if not re.search(pattern, blob):
                failures.append(f"{name}: missing required clause '{clause}' (/{pattern}/)")
        for clause, pattern in FORBIDDEN.items():
            if re.search(pattern, blob):
                failures.append(f"{name}: falsified claim still present '{clause}' (/{pattern}/)")

    checked = len(COPIES) * (len(REQUIRED) + len(FORBIDDEN))
    # "Any guard that loops must assert what it looped over" (CREW_CONTEXT).
    print(f"checked {checked} clause-assertions across {len(COPIES)} copies")
    if failures:
        for line in failures:
            print(f"DRIFT: {line}", file=sys.stderr)
        return 1
    print("OK: all three copies carry the same narrowed claim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
