# Launch Order: `epic-568-510 — repair — pending-gate HARD handoff`

**Issued:** 2026-08-14 by `admiral-epic-568` · **Boundary:** `wave-2-gate-refusal` · **Launch:** `epic-568-wave-2-repair`
**Frozen.** Read it as written. Where it is wrong, say so and float rather than quietly working around it.

## Mission

Your lane's implementation is done and independently APPROVEd. It does not merge, because the lane
fails its own full Linux suite. Make it green without weakening what it proved, then take it to
`archive`. You are repairing a launched issue: its identity, intent, and desired outcome are
unchanged and are not yours to revise.

## Prior-Wave Verdicts (pasted)

Verbatim from the wave-2 gate, measured by the Admiral at 2026-08-14T20:0xZ, cache-clean:

```
FAILED tests/test_checklist_engine.py::TripLedgerComplianceOnTheHardAdvisory::test_compliance_line_also_rides_the_already_requested_hard_advisory
FAILED tests/test_checklist_engine.py::TripLedgerComplianceOnTheHardAdvisory::test_compliance_line_appears_on_the_hard_advisory_only_in_the_defective_world
FAILED tests/test_checklist_engine.py::TripLedgerComplianceOnTheHardAdvisory::test_live_line_is_absent_after_the_offenders_own_close_but_the_historical_line_still_names_it
FAILED tests/test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build
4 failed, 2977 passed, 7 skipped, 1130 subtests passed in 120.91s
```

`main` baseline re-measured at the same gate: **2980 passed, 7 skipped, 0 failed** at `0448275e`.
Every failure above is therefore introduced by this lane. Your reviewer's APPROVE stands on the
change's substance; it was reached on targeted tests only and did not cover this.

The three failures are expected-vs-actual advisory text mismatches. Your diff added a new
`pending`-gate branch to `_trip_advisory` (`scripts/checklist_engine.py:1724`), and these three
tests build gates in `pending` status while asserting the pre-change in-progress wording.

## Pre-Rulings

1. **`decision:tests-follow-the-ruled-intent` — settled.** #510's ruled purpose is a distinct
   pending-gate instruction. If the three tests assert the old wording purely because they predate
   that distinction, updating their expectations to the shipped wording is correct and is yours to
   do. Say so explicitly in your result, naming which expectation changed and why.
2. **`decision:advisory-wording-is-surfaced` — NOT yours.** If measurement shows the shipped wording
   is itself wrong — misleading, contradictory, or changing behavior for a case #510 never intended
   to touch — that is agent-visible behavior and sits in the human's decision class. **Float it. Do
   not fix it in the lane.** State what you measured and stop at that gate.
3. **`decision:repro-before-and-after` — settled.** The issue still closes on a repro that fails
   before and passes after. Do not delete or weaken a failing test to reach green.
4. **`decision:map-refresh-is-mechanical` — settled.** Regenerate with
   `python -m scripts.code_map build --root .` and commit it. No judgement required.
5. **`decision:clear-caches-before-measuring` — settled.** `find . -name __pycache__ -type d -not
   -path './.git/*' -prune -exec rm -rf {} +` before **every** suite run. A stale `.pyc` carrying the
   pre-relocation path `constellation-skills-wt/` fabricated a failure elsewhere in this wave and
   cost four falsifications to attribute. Do not trust a gate measured without this.

## Honest-Null Clause

A measured negative is a complete, successful deliverable. If you find the three assertions are
right and the shipped wording is wrong, that is a real result — report it under pre-ruling 2 rather
than manufacturing a green suite. Do not invent work to look productive.

## Inherited Latitude

Bounded internals inside your own diff are yours. Direction, intent, scope, production defaults, and
agent-visible behavior are not. You may not revise the issue's identity or desired outcome — this is
a repair, not a re-cut.

## File Ownership

Yours: `scripts/checklist_engine.py` (only the `_trip_advisory` region your diff already touches),
`tests/test_checklist_engine.py`, `map/INDEX.md`, your own episode records.
Not yours: `scripts/hooks/spine_rail.py` and `scripts/agent_work_root.py` — #530 holds the
serialized `spine_rail` lane concurrently. Touching them breaks the one-implementer rule.

## Workspace

Worktree `.worktrees/epic-568-510`, branch `epic-568/510-hard-advisory`, spine
`.agent-work/epic-568-510/spine.json`. It is yours alone; no second Commander enters it. The spine's
lease is live and held by your predecessor's dead session — take it over, do not recreate it, and
release it last. Your spine is at `archive` blocked; reopen the gate you actually need through MCP
rather than editing spine state by hand.

## Inherited Context

Wave 1 (`#576`, `#577`, `#578`) put spine origin and worktree isolation on `main` at `0448275e`.
Spine interaction is MCP-only.

## Pre-empted Steps

Do not re-run `understand` or `plan`; they are complete and their conclusions stand. Do not redesign
the change. Start from the four failures above.

## Data Locations

Findings file: `.agent-work/epic-568-510/FINDINGS-wave2-repair.md`. Anything you learn that is real
but outside this repair goes there, not into the diff.

## Budget

One bounded repair. If it grows past its own diff, stop and float.

## Stop Conditions

Stop and report if any of these fire:
- The shipped advisory wording turns out to be wrong (pre-ruling 2).
- Green requires touching a file outside your ownership.
- Green requires deleting or weakening a test rather than correcting an expectation.
- The suite stays red after the repair for a cause you cannot attribute.

## Return Shape

Report: which expectations changed and why; the cache-clean full Linux suite counts before and after;
confirmation the map is fresh; anything floated. **You are fenced from push, PR, and merge** — that
is the Admiral's delegated class. Take the lane to the point where publication is all that remains,
park at `archive`, and say so. Parking there is correct behavior, not failure.
