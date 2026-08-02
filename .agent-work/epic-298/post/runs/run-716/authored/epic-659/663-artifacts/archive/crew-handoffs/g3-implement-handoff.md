# Implementer Handoff

## Gate
g3-implement

## Task
Create `src/physics/layer2/grip_batch.py`: the batch driver for grip-baseline module G (issue #663), mirroring `src/physics/layer2/estimate_batch.py`'s pattern. Also add `get_grip_at(...)` — the consumer-facing "subtract G" query function — to `src/physics/layer2/grip_store.py` (g1, complete).

Read `src/physics/layer2/estimate_batch.py` in full first (your primary pattern reference) and `src/physics/layer2/grip_baseline.py` (g2, complete — this is what your batch driver calls) and `src/physics/layer2/grip_store.py` (g1, complete — this is what your batch driver writes to and what `get_grip_at` reads from).

**`run_grip_batch`:** `run_grip_batch(store, *, seasons, db_path, force=False, session_type=None, fit_fn=..., calendar_fn=..., record_fn=..., log=print) -> dict`. Mirror `run_estimate_batch`'s shape: loop seasons -> GPs (via an injectable `calendar_fn`, matching the existing calendar convention) -> session types (all types if `session_type=None`, else just the one given — this matches g2's `decision:session-scope-uniform`) -> skip if already stored unless `force` -> call the injected `fit_fn` (defaulting to g2's real fit function) -> `store.upsert`. Every collaborator is an injectable `Callable` parameter defaulting to the real production function (this is the seam that lets tests inject fakes without touching the real DB/FastF1). **Per-unit failure isolation is required**: if fitting ONE session raises, catch it, call `grip_store.error_record(...)`, `store.upsert` that, and CONTINUE to the next session — one bad session must never sink the whole batch run. Return a `counts` dict (e.g. `fitted, skipped, errors, sessions_missing`) for a caller to log.

**`get_grip_at`:** add to `grip_store.py`: `get_grip_at(store: GripStore, year: int, gp_name: str, session_type: str, cumulative_track_laps: int) -> tuple[float, float]` returning `(mu, sigma)` — evaluates the stored session's fitted curve (`session_offset + curve_asymptote*(1-exp(-curve_rate*x))`, matching g2's exact functional form) at the given `cumulative_track_laps`, propagating sigma (combine `session_offset_sigma` with the curve's own parameter uncertainty at that x — a reasonable propagation is acceptable, e.g. a first-order/delta-method combination, or conservatively just `session_offset_sigma` if you state that as a deliberate simplification). Raise a clear, named exception (not a bare `KeyError`) if the (year, gp_name, session_type) has no stored record — a consumer must never silently get a wrong answer for missing data.

## Protected Intent
`get_grip_at` is THE call every future consumer uses to subtract G — it must be simple, well-tested, and honestly propagate uncertainty (never silently return a point estimate with an implied sigma=0).

## Test Mode
Test-after allowed.

## Close Criteria
- `run_grip_batch` mirrors `run_estimate_batch`'s injectable-fn seam exactly (same style of `Callable` defaults).
- Per-unit failure isolation genuinely works: a test that makes ONE session's fit raise, confirms the batch continues and produces an `error_record` for that session while still processing the rest.
- `get_grip_at` correctly evaluates the stored curve at a given `cumulative_track_laps`, returns `(mu, sigma)`, and raises clearly on a missing record.
- Tests at `tests/unit/physics/layer2/test_grip_batch.py` (this exact path — g3-integrate's postcondition hardcodes it).

## Allowed Scope
- New file: `src/physics/layer2/grip_batch.py`.
- New file: `tests/unit/physics/layer2/test_grip_batch.py`.
- Edit: `src/physics/layer2/grip_store.py` — ONLY to add the new `get_grip_at` function (additive, do not touch anything else in that file).

## Specific Exclusions
Do not modify `grip_baseline.py` (g2) or `estimate_batch.py`/`estimate_store.py`. Do not build the g4/g5 acceptance harnesses.

## Constraints
- Mirror `estimate_batch.py`'s injectable-collaborator-fn pattern exactly.
- Per-unit failure isolation is non-negotiable — this is the same repo-wide "never lose a failure" convention g1's `error_record` already implements for the store side.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2`.
- **Capability:** new — G batch driver + consumer query surface.
- **Constraints/assumptions:** none new beyond g1/g2's.
- **Decision anchors:** none new.
- **Evidence expectations:** none new.
- **Map confidence flags:** none.

## Deliverable Path Check
- **Committed** — `src/physics/layer2/grip_batch.py`; verify `git check-ignore` exit 1.
- **Committed** — `tests/unit/physics/layer2/test_grip_batch.py`; verify `git check-ignore` exit 1.
- `src/physics/layer2/grip_store.py` — existing untracked file (from g1), will show a diff now; state clearly in your result that this is an ADDITIVE edit only.

## Required Evidence
- `pytest tests/unit/physics/layer2/test_grip_batch.py -q` full output (load-bearing).
- The per-unit failure isolation test's output specifically (load-bearing — this is the most important behavior in this gate).
- `simplification_limits` clean (self-check before returning).
- Confirmation that `grip_store.py`'s only change is the additive `get_grip_at` function (e.g. paste a diff or describe exactly what was added).

## Verification Commands
```bash
cd /c/Programs/f1brainz-wt/epic659-663
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m pytest tests/unit/physics/layer2/test_grip_batch.py tests/unit/physics/layer2/test_grip_store.py -q
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m src.utils.simplification_limits --paths src/physics/layer2/grip_batch.py src/physics/layer2/grip_store.py tests/unit/physics/layer2/test_grip_batch.py
```
Use this exact launcher path — plain `py` resolves to a broken shim (confirmed by g1/g2).

## Suggested Model Tier
Simple bounded — precedented pattern (estimate_batch.py), moderate but bounded new logic (get_grip_at curve evaluation).

## Authority
The function signatures and behavior above are decided; the exact sigma-propagation method in `get_grip_at` is yours to choose within the stated constraint (must not silently imply sigma=0).

## Stop Conditions
Stop and return if `estimate_batch.py`'s pattern doesn't map cleanly (describe why) or a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT (write to `.agent-work/663-grip-g/crew-handoffs/g3-implement-result.md`, and return as final message text): completed slice, files changed, evidence produced (paste outputs), assumptions used, workflow feedback.
