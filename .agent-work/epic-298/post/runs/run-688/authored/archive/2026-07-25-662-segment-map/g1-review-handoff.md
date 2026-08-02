# Reviewer Handoff — G1 Field reference lap builder

## Gate
g1 (issue #662). Pinned interpreter: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`.

## What was implemented
A pooled FIELD reference lap. New files:
- `src/physics/segment_map/derivation/__init__.py`, `reference_lap.py` (`ReferenceLap` dataclass +
  `build_reference_lap` agnostic core + `reference_lap_from_store` loader)
- `tests/unit/physics/segment_map/derivation/__init__.py`, `test_reference_lap.py` (7 tests)
Implementer result (read it): `.agent-work/662-segment-map/g1-impl-result.md`.

## How to inspect
```bash
cd C:/Programs/f1brainz-wt/epic659-662
git status --porcelain src/physics/segment_map/derivation tests/unit/physics/segment_map/derivation
git diff -- src/physics/segment_map/derivation tests/unit/physics/segment_map/derivation   # untracked: use `git add -N` or read files directly
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_reference_lap.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/reference_lap.py
```
Read `src/physics/ribbon.py::build_ribbon`, `src/physics/session_fit.py::load_quali_session`,
`src/preprocessing/trajectory/loaders.py::driver_streams` to verify the reuse claims.

## Task statement
Build a POOLED field reference lap (curvature/speed/brake on one shared grid) from the durable
store-first telemetry path, reusing build_ribbon for geometry. Verify it against the gate's Close Criteria.

## Reviewer FOCUS (from the plan)
1. **Cross-channel grid alignment:** curvature, v_ref, and the brake signal share the EXACT
   `build_ribbon` progress grid — no off-by-one/misaligned resample; all channels length `n_grid`;
   `distance_m` strictly increasing 0→lap_length. Confirm the pooling resamples each lap onto the
   ribbon's `u=s/s[-1]` grid before medianing.
2. **DB-only source:** per-lap arrays come from `session_fit.load_quali_session` (store-first,
   cache-fallback) — NO direct `fastf1` import in `reference_lap.py`; `ribbon.build_session_ribbon`
   NOT used. Grep the module for `fastf1` / `build_session_ribbon` and confirm absent.
3. **Pooled not per-lap:** the reference lap is a median across the field's clean flying laps, not a
   single lap; `min_laps` guard raises `ValueError`.
4. **Reuse correctness:** `build_ribbon` is called (geometry not hand-re-derived); the parallel-array
   contract (laps_speed[i]/laps_brake[i] same length as laps_xy[i]) is honored by the store loader.
5. **No scope breach:** no edit to `docs/architecture/*` or any existing `src/physics/segment_map/*.py`
   runtime file; no frozen-constant literals introduced (none belong in G1).

## Close Criteria (verdict basis)
- Tests green on the pinned interpreter (7/7); simplification_limits clean.
- Grid alignment + DB-only source + pooled-not-per-lap all hold on inspection.
- Note (do NOT block on): the implementer flagged a judgment call — pooling ALL clean laps (50s floor)
  across the field rather than each driver's fastest-N%. This is acceptable for G1 (a representative
  racing-line geometry); confirm it is a reasonable "clean" filter, not silently wrong.

## Constraints
- DB-only analysis (no FastF1 in analysis code); pinned interpreter for all commands.
- Reviewer does not edit code; report BLOCK with specific findings or APPROVE.

## Map Anchors (inbound)
Inherits g1-implement anchors: decision:reference-lap-pooled-not-per-lap (@grade settled/human),
decision:derivation-subpackage-placement (@grade settled/measured), constraint:db-only-analysis.

## Required Evidence
Re-run the two verification commands and paste the tail; grep-confirm no `fastf1`/`build_session_ribbon`
in reference_lap.py; a one-line confirmation of grid alignment from reading the pooling code.

## Return Format
Return REVIEW_RESULT to `.agent-work/662-segment-map/g1-review-result.md`: verdict APPROVE or BLOCK,
findings (each with severity + file:line), evidence reproduced, workflow feedback. **Deliver a concise
summary (verdict + result path) to "cmdr-662" via SendMessage before ending your turn.**
