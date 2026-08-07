# Implementer Handoff — x13 map dogfood trial (f1Brainz #708)

First real instance of the Map entry point handoff pattern. Besides fixing the issue, this dispatch measures whether the map earns its place — keep the use-trace honestly.

## Gate
x13 (explore-code-map cycle 4 dogfood trial)

## Task
f1Brainz issue #708: `split_half_boundary_drift` (in `scripts/validate_segment_map_662.py`) relies on the default `data/telemetry_store.db` resolving; in a worktree without a resolvable default store, C gating fails with a confusing error. Add an explicit store argument (plumbed, not defaulted-and-ignored), update all callers, and make the no-store failure mode a clear error.

## Protected Intent
C gating must keep working unchanged where it works today (default store resolves), and must fail with an actionable message where it doesn't. No behavior change to the drift computation itself.

## Test Mode
Test-after allowed. The gating test file must pass; add/adjust a test for the explicit-arg path if the existing scenario doesn't cover it.

## Close Criteria
- `split_half_boundary_drift` takes an explicit store argument; every caller passes it deliberately (or the default is derived once at a caller that owns the decision, not silently inside the function).
- All callers found via the map's referenced-by line are updated; state the count and compare it against a grep for the symbol (this comparison is trial evidence).
- Gating test file green; clear error message on unresolvable store.

## Allowed Scope
`scripts/validate_segment_map_662.py`, its callers (`src/physics/pilot/pipeline.py`, `tests/unit/physics/segment_map/derivation/test_segment_map_gating.py`, plus any the map or grep surfaces), and minimally the test file's fixtures if the new arg requires it.

## Specific Exclusions
- The drift computation's numerics — off-limits.
- No edits to f1Brainz `main`. Work in a NEW git worktree of f1Brainz (`git worktree add <path> -b map-trial-708`), commit there, do NOT push.
- Do not touch other open issues' territory (#722, #710) even where adjacent.

## Constraints
- Comment grammar (trial): where your change embodies an assumption, constraint, or rationale, record it as a comment at the code using a bare `Word:` prefix — `Assumption:`, `Constraint:`, `Rationale:`, `Rejected:`, `See: <target>`. Example: `# Constraint: store path must resolve before gating starts — worktrees have no default store.` Write them where a future reader needs them, not everywhere. Mint a bracketed anchor id (`# [kebab-slug]` line above a def) ONLY if something external needs to point at it — likely not needed here.
- Plain error message with the attempted path in it.

## Map Anchors (inbound)
- **Map entry point:** start with `evidence/x13/map/scripts.validate_segment_map_662/split_half_boundary_drift.md` (this worktree's `.agent-work/explore-code-map/`), then the module page beside it. Resolve any naming drift via `evidence/x13/map/INDEX.md`. Pull the pages for each symbol you're about to change and read its `referenced by` line before editing.
- **Structural:** `scripts/validate_segment_map_662.py:160` (function), callers per the map.
- **Constraints/assumptions:** worktrees have no default telemetry store — the issue's whole point.
- **Map confidence flags:** this map was built minutes ago from the ruled extractor; `unresolved:` lines on pages are honest extractor limits — verify against source where they matter.

## Deliverable Path Check
- Committed (to the f1Brainz trial worktree branch, not this repo): the code changes above.
- Local-only: your use-trace and result file (paths below, in the constellation worktree).

## Required Evidence
1. **Use-trace (load-bearing, the trial's measurement):** for every map page you load: which page, what question it answered, and whether the answer was available from grep/one file-read at similar cost. For every place you skipped the map for grep/source: why. Honesty over advocacy — "the map added nothing here" is a valid, valuable trace line.
2. Caller count: map's referenced-by vs `grep -rn "split_half_boundary_drift"` — do they agree? (load-bearing)
3. Gating test output (load-bearing). Full-suite not required (known stalls exist, e.g. #703's region).
4. Diff of the change; list of tagged comments written (confirmatory).

## Wiring Grep
```bash
grep -rn "split_half_boundary_drift" --include=*.py C:/Programs/f1Brainz/src C:/Programs/f1Brainz/scripts C:/Programs/f1Brainz/tests
```
State the count of call sites found and reconcile with the map's referenced-by count.

## Verification Commands
```bash
cd <your f1Brainz worktree> && py -m pytest tests/unit/physics/segment_map/derivation/test_segment_map_gating.py -q
```
(If pytest is unavailable under `py`, use the repo's documented test entry point — check its Makefile/TESTING.md.)

## Suggested Model Tier
simple bounded — small mechanical change; the measurement discipline is the real work.

## Authority
Issue #708's recommendation (explicit store arg) is decided. You decide the arg's exact signature/default-derivation site. Do not decide to push, merge, or touch main.

## Stop Conditions
Stop and return if: the change wants to spread beyond the named files, the gating test can't run at all, or the map pages for the entry point are missing/garbled (that's a prep-fullmap defect — report, don't work around silently).

## Return Format
IMPLEMENTER_RESULT at `.agent-work/explore-code-map/excursions/x13-result.md`: completed change (worktree path + branch + commit sha), files changed, evidence 1–4 inline, tagged comments written, workflow feedback (what in this handoff or the map made work harder), out-of-scope observations.
