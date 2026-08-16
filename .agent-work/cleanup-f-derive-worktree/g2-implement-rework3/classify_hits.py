#!/usr/bin/env python
"""Classify every live-zone hit `sweep_claims.py` reported (close criterion C1).

Reads a saved sweep run and assigns one class to every hit outside the record
zone (`.agent-work/`, `map/`, `episodes/` — dated records of what was said at
the time, never repaired). Refuses if any live hit is unclassified, so a hit
this gate has not looked at cannot pass silently.

Line numbers are those of the PRE-REPAIR tree; run it against
`m1-sweep-raw.txt`, which was captured before any edit.

  usage: py classify_hits.py [sweep-output.txt]
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

STALE = "stale -> repaired"
COUNT = "correct claim, consumer count harmonized"
OK = "already correct"
FENCED = "fenced (g3 / lane A) -> reported, not edited"
UNRELATED = "unrelated to either family"

# (file, line) -> (class, note). Pre-repair line numbers.
CLASSIFICATION = {
    # ---- derive family -------------------------------------------------
    ("scripts/checklist_engine.py", 3498): (STALE, "main() load-time block: 'the worktree is derived from the spine's own path where it is needed' — the engine derives nothing anywhere"),
    ("scripts/checklist_engine.py", 3499): (STALE, "same sentence, second line of the wrap"),
    ("scripts/spine_lifecycle.py", 92): (STALE, "build_origin docstring: '(#609 -- a spine's worktree is derived from its path, and ownership is the lease)' — both families in one parenthesis"),
    ("scripts/checklist_engine.py", 95): (COUNT, "module header: the rule is not retired, only the engine's copy — true; count sentence harmonized"),
    ("docs/CHECKLIST_SCHEMA.md", 128): (COUNT, "origin section: same true sentence; count sentence harmonized"),
    ("tests/test_spine_origin_isolation.py", 44): (COUNT, "module docstring: same true sentence; count sentence harmonized"),
    ("tests/test_worktree_derivation.py", 1): (COUNT, "table docstring: one rule, one implementation in the hook — true; count sentence harmonized to the same wording"),
    ("tests/test_spine_origin_isolation.py", 51): (OK, "'re-derives against that same table' — the hook's rule, true"),
    ("tests/test_spine_origin_isolation.py", 448): (OK, "records that the derivation was deleted and why the anchor moved — true"),
    ("tests/test_worktree_derivation.py", 112): (OK, "_expected()'s docstring: 'a derived worktree, in the normalized form the rule returns' — about the table, not the engine"),
    ("scripts/hooks/spine_rail.py", 1171): (FENCED, "g3: '_is_claim_layout ... until the derivation was widened' — the hook's own history"),
    **{("tests/test_spine_rail.py", n): (FENCED, "g3: the hook's derivation tests, incl. two stale references to the deleted engine twin") for n in (874, 885, 903, 904, 909, 911, 925, 930, 944, 945, 946, 947, 950, 1917, 1918, 2654, 2656)},
    ("docs/GAUGE_WRITER_HOOK.md", 566): (UNRELATED, "gauge binding keyed by spine path rather than a derived worktree"),
    ("docs/GAUGE_WRITER_HOOK.md", 568): (UNRELATED, "same paragraph"),
    ("docs/GAUGE_WRITER_HOOK.md", 659): (UNRELATED, "the gauge hook's worktree root, derived from `git worktree list`"),
    ("docs/GAUGE_WRITER_HOOK.md", 661): (UNRELATED, "same paragraph"),
    ("notes-1.md", 41): (UNRELATED, "another run's working notes (commander-315-native), a dated record of the #315 defect"),
    ("notes-1.md", 43): (UNRELATED, "same notes"),
    ("scripts/episode_capture.py", 126): (UNRELATED, "a derived project name, not a worktree"),
    ("scripts/mcp_spine_server.py", 590): (UNRELATED, "lane A; the door's own `_worktree_root_for_lifecycle`, a git call, not this rule"),
    ("scripts/mcp_spine_server.py", 593): (UNRELATED, "lane A; same paragraph"),
    ("scripts/mcp_spine_server.py", 811): (UNRELATED, "lane A; primary-checkout derivation"),
    ("scripts/mcp_spine_server.py", 870): (UNRELATED, "lane A; same"),
    ("scripts/mcp_spine_server.py", 981): (UNRELATED, "lane A; work_id derived from a worktree path"),
    ("scripts/mcp_spine_server.py", 1367): (UNRELATED, "lane A; tool-list derivation"),
    ("scripts/spine_lifecycle.py", 230): (UNRELATED, "`git worktree` arguments this call itself derived"),
    ("scripts/spine_lifecycle.py", 231): (UNRELATED, "same sentence"),
    ("tests/test_episode_fields.py", 143): (UNRELATED, "derived project name again"),
    ("tests/test_iterative_planning_doctrine.py", 1329): (UNRELATED, "a `git rev-parse` fragment in a shipped command"),
    ("tests/test_mcp_lifecycle.py", 25): (UNRELATED, "lane A; the door's derived path"),
    ("tests/test_mcp_lifecycle.py", 236): (UNRELATED, "lane A; `_default_wt_root`"),
    ("tests/test_spine_lifecycle.py", 144): (UNRELATED, "work-id segment derived from a directory name"),
    ("tests/test_spine_lifecycle.py", 146): (UNRELATED, "same test"),
    ("tests/test_worktree_derivation.py", 268): (UNRELATED, "symlink-escape reasoning; names the retired predicate — reported as tc-A, outside both families"),
    ("tests/test_worktree_derivation.py", 270): (UNRELATED, "same docstring"),
    ("tests/test_worktree_derivation.py", 274): (UNRELATED, "test body, `derive = IMPLEMENTATIONS[impl_name]`"),
    # ---- ownership-guard family ----------------------------------------
    ("scripts/checklist_engine.py", 3507): (STALE, "main(): 'The lease, which is the actual ownership guard, is enforced inside dispatch()' — unqualified, the claim R1 narrowed"),
    ("scripts/checklist_engine.py", 3508): (STALE, "same sentence: 'as it always was'"),
    ("scripts/spine_lifecycle.py", 94): (STALE, "build_origin: 'and ownership is the lease' — unqualified"),
    ("scripts/checklist_engine.py", 106): (OK, "module header: 'ownership is the LEASE, but only where one is actually held' — R1-narrowed"),
    ("tests/test_spine_origin_isolation.py", 27): (OK, "module docstring: same R1-narrowed sentence"),
    ("tests/test_worktree_derivation.py", 8): (OK, "the 2026-08-16 worktree-is-location frame: what the DERIVATION answers, not the guard-removal claim; carries the single repo-wide citation of that ruling (C8) and is left exactly as it stands"),
    ("scripts/hooks/spine_rail.py", 721): (FENCED, "g3: the same worktree-is-location frame in the hook's docstring"),
    ("scripts/checklist_engine.py", 982): (UNRELATED, "require_session's docstring on which refusal instruction is printed"),
    ("docs/superpowers/plans/2026-06-24-lease-owner-liveness.md", 15): (UNRELATED, "a plan doc on lease liveness"),
    ("docs/superpowers/plans/2026-06-24-lease-owner-liveness.md", 147): (UNRELATED, "same doc"),
    ("scripts/install_constellation.py", 546): (UNRELATED, "'main() stays as pure as it always was' — lane A, different subject"),
    ("tests/test_install_constellation.py", 4067): (UNRELATED, "the same sentence in its test"),
}

RECORD_PREFIXES = (".agent-work/", "map/", "episodes/")


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "m1-sweep-raw.txt"
    family = None
    live: list[tuple[str, str, int, str]] = []
    record = Counter()
    for line in src.read_text(encoding="utf-8").splitlines():
        m = re.match(r"=== family: (\w+)", line)
        if m:
            family = m.group(1)
            continue
        hit = re.match(r"^([\w./-]+):(\d+): (.*)$", line)
        if not hit or family is None:
            continue
        rel, lineno = hit.group(1), int(hit.group(2))
        if rel.startswith(RECORD_PREFIXES):
            record[family] += 1
            continue
        live.append((family, rel, lineno, hit.group(3)))

    missing = [(f, r, n) for f, r, n, _ in live if (r, n) not in CLASSIFICATION]
    counts = Counter(CLASSIFICATION[(r, n)][0] for f, r, n, _ in live if (r, n) in CLASSIFICATION)

    print(f"live-zone hits classified: {len(live) - len(missing)}/{len(live)}")
    print(f"record-zone hits (dated records, never repaired): {dict(record)}\n")
    for family in ("derive", "ownership"):
        print(f"--- {family} ---")
        for f, rel, lineno, excerpt in live:
            if f != family:
                continue
            cls, note = CLASSIFICATION.get((rel, lineno), ("UNCLASSIFIED", ""))
            print(f"{rel}:{lineno}\n    [{cls}] {note}")
        print()
    print("class totals:", dict(counts))

    if missing:
        print("\nFAIL: unclassified live hits:")
        for f, r, n in missing:
            print(f"  {f} {r}:{n}")
        return 1
    if not live:
        print("\nFAIL: no live hits read — the sweep output is not being parsed.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
