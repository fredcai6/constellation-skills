"""C6/C7/C8 — the three hand-copied prose copies must carry the SAME claim.

Inherited from the rework-1 implementer, which wrote it for exactly this
agreement check, and UPDATED here for rework 2. What changed: the clause that
required all three copies to point at `checklist_engine.worktree_from_spine_path`
as the thing that now answers location. That symbol was deleted in #609 g2 under
`ADMIRAL_RULING-2` N2, so the clause was requiring a claim that is now false. It
is replaced by the four clauses of the repaired sentence -- the engine reads no
location at all, the rule survives in the hook, the case table specifies it, and
it re-lands with its consumer -- and the old pointer is added to FORBIDDEN so a
copy that still names the deleted symbol fails here rather than at review.

Rework 1's clauses are otherwise untouched: the R1 narrowing is a ruled
statement and stays.

The reviewer's Fowler pass flagged `duplicated-code`: this claim lives in three
files with nothing checking the copies, and "repairing it in one place and not
the other two is the concrete risk." This check is that missing comparison.

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
    # --- rework 2: what replaces the pointer at the deleted engine copy ---
    "engine-reads-no-location": r"reads no location",
    "ambient-or-derived": r"ambient or derived",
    "rule-survives-in-the-hook": r"spine_rail\._worktree_from_spine",
    "table-is-the-specification": r"case table is its specification",
    "deleted-under-the-ruling": r"deleted in #609 g2 under admiral_ruling-2 n2",
    "re-lands-with-its-consumer": r"re-lands in #610's wave together with #315",
}

# The falsified sentences. Anchored so the NARROWED forms (which reuse the same
# opening words and then qualify them) do not count as a match.
FORBIDDEN = {
    "unqualified-no-guard": r"removed no guard\s*[.,]",
    "unqualified-nothing-unguarded-removal": r"nothing was left unguarded by that removal\s*[.,]",
    "unqualified-nothing-unguarded-removing": r"nothing was left unguarded by removing it\s*[:.]",
    "unqualified-always-was": r"ownership is the lease,? and (always was|was already)",
    # --- rework 2: the engine no longer holds a derivation to point at ---
    "points-at-the-deleted-engine-copy": r"checklist_engine\.worktree_from_spine_ ?path",
    "spine-path-answers-outright": r"the spine's own path now answers outright",
    "engine-still-derives": r"a spine's worktree is now derived from its",
}


def normalize(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    # `#` comment markers -- but NOT an issue reference like `#610`, which is
    # part of the claim. A line wrapped so that `#610` lands first would
    # otherwise be silently renumbered to `610` and read as a missing clause.
    text = re.sub(r"(?m)^[ \t]*(?:#(?!\d)[ ]?)+", " ", text)
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
