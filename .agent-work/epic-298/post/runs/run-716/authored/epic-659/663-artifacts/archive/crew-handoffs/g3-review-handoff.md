# Reviewer Handoff

## Gate
g3-implement (reviewing for g3-review)

## Survey State Location
`.agent-work/663-grip-g/g3-review/review.json`

## What Was Implemented
`src/physics/layer2/grip_batch.py` (`run_grip_batch`, injectable-fn batch driver mirroring `estimate_batch.py`, per-unit failure isolation) + `get_grip_at` added to `grip_store.py` (delta-method sigma propagation, `GripRecordNotFoundError`).

## How to Inspect the Diff
```bash
cd /c/Programs/f1brainz-wt/epic659-663
git status --porcelain
```
`grip_batch.py` + `test_grip_batch.py` are new (untracked). `grip_store.py` is ALREADY untracked from g1/g2 (never committed in this run), so there is no `git diff` to show the incremental edit — read the file directly and confirm the implementer's claim that only an `import math` line, a new `GripRecordNotFoundError` class, and a new `get_grip_at` function were added (nothing else in the file changed).

## Task Statement
Build the batch driver + consumer query surface, per the implement handoff (`.agent-work/663-grip-g/crew-handoffs/g3-implement-handoff.md`).

## Close Criteria
- `run_grip_batch` mirrors `estimate_batch.run_estimate_batch`'s injectable-`Callable` seam.
- Per-unit failure isolation genuinely works — re-run the specific isolation test(s), confirm a raising `fit_fn` for one session produces an `error_record` and the batch continues to the NEXT session (not just "the test passes," actually read the assertions).
- `get_grip_at` correctly evaluates the curve, raises `GripRecordNotFoundError` (not a bare `KeyError`) on missing data, and never silently implies sigma=0.

## THE ONE THING TO SCRUTINIZE CAREFULLY
The implementer self-flagged: g2's `fit_session_grip_baseline` has a thin-session neighbor-lookup mechanism (tested directly in g2 by passing an explicit neighbor session), but `run_grip_batch` as built does NOT wire sibling-session results together across sessions within a weekend — each session is fit independently by the batch loop. In a REAL batch run over a full weekend, this means a thin session's fallback would likely hit the degenerate "no neighbor available" branch even when a normal FP2 fit genuinely exists for the same weekend, because the batch driver never passes it along.

**Your job:** determine whether this is (a) a genuine functional gap that should BLOCK this gate (if the handoff's Close Criteria implicitly required end-to-end weekend-neighbor wiring and it's silently missing), or (b) a real but appropriately out-of-scope-for-g3 limitation, GIVEN that g4/g5 (the two GATING acceptance harnesses, built next) are expected to call g2's fit function fairly directly on specific sessions/slices rather than through the full `run_grip_batch` orchestrator — read `.agent-work/663-grip-g/execute.json`'s g4-implement/g5-implement imperatives to check this assumption. If (b), it must be recorded as an explicit, honestly-scoped triage candidate (not silently dropped) — check whether the implementer already flagged it clearly enough in their IMPLEMENTER_RESULT, and add your own assessment of whether it could bite the GATING gates specifically.

## Allowed Scope
New files (`grip_batch.py`, `test_grip_batch.py`) + the additive `get_grip_at` edit to `grip_store.py`.

## Specific Exclusions
Must not modify `grip_baseline.py` (g2) or `estimate_batch.py`.

## Constraints the Implementation Must Respect
Injectable-fn pattern, per-unit failure isolation, honest sigma propagation.

## Map Anchors (inbound)
Same as `g3-implement-handoff.md` — `struct:physics.layer2`; no new decision anchors.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/663-grip-g/crew-handoffs/g3-implement-result.md` — 22/22 tests, simplification PASS. Use `"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe"` for every command.

## Suggested Model Tier
Stronger — reason: the weekend-neighbor scrutiny requires reading ahead into g4/g5's plan to judge scope-correctness, not just re-running tests.

## Stop Conditions
Stop and return BLOCK if per-unit isolation doesn't actually work, `get_grip_at` silently mishandles missing data, or the weekend-neighbor gap turns out to invalidate g4/g5's planned approach.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/663-grip-g/crew-handoffs/g3-review-result.md`, and return as final message text): verdict (APPROVE or BLOCK), per-check findings, blockers, your explicit determination on the weekend-neighbor question (a) vs (b) with reasoning, out-of-scope observations, workflow feedback.
