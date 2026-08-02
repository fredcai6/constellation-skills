# Implementer Handoff — G1 Field reference lap builder

## Gate
g1 (issue #662, epic #659). Pinned interpreter: `C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe` (Python 3.14, fastf1 3.8.1). Bare `py` is the WRONG interpreter (3.12, no fastf1) — do not use it.

## Task
Build a **pooled FIELD reference lap** for one (year, gp_name, quali) weekend — the geometry+speed backbone the corner/braking gate and corner descriptors are computed off. New files:
- `src/physics/segment_map/derivation/__init__.py` (new subpackage)
- `src/physics/segment_map/derivation/reference_lap.py`
- `tests/unit/physics/segment_map/derivation/__init__.py` (if the test dir needs it)
- `tests/unit/physics/segment_map/derivation/test_reference_lap.py`

Produce a frozen dataclass (e.g. `ReferenceLap`) carrying, on ONE shared progress/distance grid:
`distance_m`, `curvature`, `v_ref` (pooled speed, m/s), a pooled brake signal (see below), `px`, `py`,
plus `lap_length_m` and `n_laps_pooled`. Provide a builder
`build_reference_lap(laps_xy, laps_speed, laps_brake, n_grid=1500, smooth_window=9, min_laps=3)`
that is **smoother-agnostic** (like `ribbon.build_ribbon`): it takes already-extracted per-lap arrays,
NOT a FastF1 session. Also provide a thin convenience loader
`reference_lap_from_store(year, gp_name, session_type="Q", ...)` that sources the per-lap arrays from the
durable telemetry store via the existing fit chain (see Constraints) and calls the agnostic core.

## Protected Intent
The map is a **fixed-per-weekend** structure; the reference lap must be POOLED across the field's clean
flying laps (representative), NEVER a single lap, and must NOT leak race outcomes (quali-side only).
All channels MUST share one grid so a distance maps to the same station in curvature, speed, and brake.

## Test Mode
TDD-lean: write `test_reference_lap.py` FIRST for the agnostic core on synthetic laps (deterministic).
The store-backed loader gets a smoke test guarded on store availability (skip cleanly if absent).

## Close Criteria
- `build_reference_lap` reuses `src.physics.ribbon.build_ribbon` for the median-pooled XY geometry
  (`distance_m`, `curvature`, `px`, `py`) — do NOT re-derive curvature by hand; call build_ribbon.
- `v_ref` and the brake signal are pooled onto the SAME `u`-grid build_ribbon uses (resample each lap's
  speed/brake onto `np.linspace(0,1,n_grid)` by that lap's normalized arc-length `u=s/s[-1]`, then
  **median** across laps for speed; for brake, pool the per-lap brake-active fraction per grid point).
- `distance_m` strictly increasing 0→lap_length; all channels length `n_grid`; curvature+v_ref finite.
- `min_laps` guard raises `ValueError` when fewer laps are supplied.
- Tests: synthetic laps prove (a) grid alignment (all channels length n_grid, distance monotone),
  (b) v_ref median pooling (a known set of laps → expected median speed at a station),
  (c) curvature comes through build_ribbon, (d) min_laps ValueError.

## Allowed Scope
`src/physics/segment_map/derivation/` (new); `tests/unit/physics/segment_map/derivation/`. You MAY read
(not edit): `src/physics/ribbon.py`, `src/physics/session_fit.py`, `src/data/telemetry_store.py`,
`src/physics/segment_classifier.py`, `src/physics/physics_data_models.py`,
`src/preprocessing/trajectory/loaders.py`.

## Specific Exclusions
- Do NOT build the corner/braking gate, tiling, sector logic, descriptors, or severity here (later gates).
- Do NOT edit `docs/architecture/*` (map fence) or any `src/physics/segment_map/` runtime/store file.
- Do NOT call FastF1 directly and do NOT use `ribbon.build_session_ribbon` (it pulls FastF1).

## Constraints
- **DB-only analysis:** the per-lap arrays MUST come from the durable telemetry source, not a live API.
  The sanctioned path is the existing fit chain that reads STORE-FIRST: inspect
  `src/physics/session_fit.py::load_quali_session` (rebuilds from `TelemetryStore` when present, cache
  fallback) and how it yields per-driver smoothed lap streams / KinematicSamples (position m, speed m/s,
  brake state). Reuse that loader to get `laps_xy` (metres), `laps_speed` (m/s), `laps_brake` for the
  field's clean flying laps. If the exact reuse seam is awkward, extract per-lap `(X,Y)`+speed+brake
  from the same store the fit chain uses — cite the exact function you call and its return shape in
  IMPLEMENTER_RESULT. Do NOT invent a second telemetry source.
- **No thresholds here** (frozen constants belong to later gates).
- Brake signal: use whatever brake channel the store/fit chain exposes (e.g. `KinematicSample.regime ==
  "straight_brake"`, or the car-data `brake` column) — a per-grid-point brake-active fraction that g2
  can threshold for onset. Name the exact source field in IMPLEMENTER_RESULT.
- Units: X/Y in metres (loaders.driver_streams already converts from decimetres); speed m/s.

## Map Anchors (inbound)
- **Structural:** `ribbon.build_ribbon` (reuse for geometry); `session_fit.load_quali_session`
  (store-first source); `telemetry_store.py` (#541 durable store); NEW `segment_map/derivation/reference_lap.py`.
- **Capability:** segment_map_derivation (NEW) — reference-lap foundation.
- **Constraints/assumptions:** constraint:db-only-analysis (store-first, never FastF1).
- **Decision anchors:**
  - decision:reference-lap-pooled-not-per-lap — gate off a POOLED field lap; per-lap gates are demoted
    to observation filters. @grade: settled/human (launch order Pre-Rulings) · leans g1
  - decision:derivation-subpackage-placement — new modules under `src/physics/segment_map/derivation/`.
    @grade: settled/measured · leans g1..g6
- **Evidence expectations:** the reference lap shares ONE progress grid across curvature/speed/brake.
- **Map confidence flags:** reference-lap builder has NO prior implementation — build fresh, test-led.

## Deliverable Path Check
- **Committed:** `src/physics/segment_map/derivation/reference_lap.py`, `__init__.py`,
  `tests/unit/physics/segment_map/derivation/test_reference_lap.py` — `git check-ignore` on the .py exits
  1 (NOT ignored), verified. New files appear in `git status` (untracked) until staged.

## Required Evidence
- pytest output: `test_reference_lap.py` green on the pinned interpreter (LOAD-BEARING).
- `simplification_limits --paths src/physics/segment_map/derivation/reference_lap.py` clean (LOAD-BEARING).
- In IMPLEMENTER_RESULT: name the EXACT store/fit function you called for per-lap arrays + its return
  shape, and the exact brake source field (confirmatory).

## Verification Commands
```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_reference_lap.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/reference_lap.py
```

## Suggested Model Tier
Stronger — the DB-only store-first plumbing + cross-channel grid alignment are the subtle risks.

## Authority
Subpackage placement, pooled-not-per-lap, and DB-only source are DECIDED (see anchors) — do not relitigate.
You MAY decide the internal dataclass shape and the exact store seam you reuse (cite it).

## Stop Conditions
Stop and return if: the store-first per-lap source cannot be reused without editing a `segment_map`
runtime file or calling FastF1; required evidence cannot be produced; a decision outside the above is needed.

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/662-segment-map/g1-impl-result.md`: completed slice, files
changed, test mode satisfied, evidence (pytest + simplification_limits output), the store seam reused +
its return shape, brake source field, assumptions, stop conditions hit, out-of-scope observations,
workflow feedback. **Deliver the result to "cmdr-662" via SendMessage before ending your turn.**
