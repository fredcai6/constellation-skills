# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
G1 — Field reference lap builder (issue #662, epic #659).

## Completed slice
Built the pooled FIELD reference lap for one (year, gp_name, session) weekend: a smoother-agnostic core
(`build_reference_lap`) that reuses `src.physics.ribbon.build_ribbon` verbatim for geometry and pools
speed (median) and brake state (active-fraction) onto the SAME arc-length progress grid, plus a
store-backed convenience loader (`reference_lap_from_store`) that sources per-lap position/speed/brake
from the durable telemetry store via the existing store-first fit chain (`session_fit.load_quali_session`).

## Scope
**Files changed:**
- `src/physics/segment_map/derivation/__init__.py` (new)
- `src/physics/segment_map/derivation/reference_lap.py` (new)
- `tests/unit/physics/segment_map/derivation/__init__.py` (new)
- `tests/unit/physics/segment_map/derivation/test_reference_lap.py` (new)
- `.agent-work/662-segment-map/crew-handoffs/g1-impl-plan.json` (new — this run's engine-driven plan)

**Specific exclusions touched:** no. Did not edit `docs/architecture/*`, any existing
`src/physics/segment_map/*.py` runtime file (`runtime.py`, `store.py`, `identity.py`, `from_mixture.py`,
`protocols.py`, `__init__.py`), did not call FastF1 directly, and did not use `ribbon.build_session_ribbon`.

## Map Impact
- **Structural anchors touched:** `ribbon.build_ribbon` (reused, unmodified, imported and called with the
  same parameters as always) and `session_fit.load_quali_session` (reused, unmodified) — both consumed,
  neither edited. NEW `src/physics/segment_map/derivation/reference_lap.py` (`ReferenceLap`,
  `build_reference_lap`, `reference_lap_from_store`).
- **Capabilities added/changed/affected:** `segment_map_derivation` (NEW) is now a real capability — the
  pooled field reference lap is buildable both from synthetic per-lap arrays (agnostic core) and
  end-to-end from the durable store for a real weekend (verified against 2026 Australia Q: 246 pooled
  laps).
- **Constraints/assumptions touched:** `constraint:db-only-analysis` honored — `reference_lap_from_store`
  never imports `fastf1`; all data comes through `session_fit.load_quali_session`'s store-first shim.
- **Decision candidates / resolved decisions:**
  - `decision:reference-lap-pooled-not-per-lap` — implemented as specified (median speed pooling,
    active-fraction brake pooling, across the WHOLE field's clean flying laps, not any single lap).
  - `decision:derivation-subpackage-placement` — new modules placed under
    `src/physics/segment_map/derivation/` per the settled decision.
  - New candidate (not yet graded, surfacing for Cartographer/Commander): the agnostic core's contract
    requires `laps_speed[i]`/`laps_brake[i]` to be PARALLEL arrays to `laps_xy[i]` (same length, same
    sample points) rather than independently-timed streams — this was my own design choice (the handoff
    didn't pin it down) and downstream gates (G2+) that call `build_reference_lap` directly need to know
    this contract. See "Workflow Feedback" below.
- **Claims/evidence produced:** both Required Evidence commands green (pasted below); 7/7 unit tests
  (6 synthetic + 1 real-store smoke) pass; `simplification_limits` clean.
- **Trust limitations / drift found:** none found in the reused seams. One clarification for future
  gates: `tele_laps.driver` (and therefore `DBSession.laps` / FastF1 `Laps.pick_drivers`) is keyed by
  **abbreviation** (e.g. `'RIC'`), NOT by driver number — `session.drivers` on `DBSession` is driver
  NUMBERS (car_data/pos_data keys). `reference_lap_from_store` tries `pick_drivers(driver_num)` first,
  then falls back to `pick_drivers(abbreviation)` via `session.get_driver(num)['Abbreviation']` — this
  fallback is load-bearing, not defensive dead code (confirmed via direct sqlite inspection of the real
  store, and the real-store smoke test exercises this exact path).
- **Triage candidates:** none raised (no out-of-scope defects found in the reused seams).

## Test mode
**Required:** test-first (TDD-lean per handoff) for the agnostic core; smoke test guarded on store
availability for the convenience loader.
**Satisfied:** yes. `test_reference_lap.py` was written and run BEFORE `reference_lap.py` existed
(RED: `ModuleNotFoundError`), then the implementation was added and the same file went green on the
first attempt (no rework needed). The store-backed smoke test was added last and exercised against the
real durable store (present in this environment at `C:/Programs/f1Brainz/data/telemetry_store.db`).

## Evidence

### Required Evidence 1 — pytest (LOAD-BEARING)

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/segment_map/derivation/test_reference_lap.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1brainz-wt\epic659-662
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 7 items

tests\unit\physics\segment_map\derivation\test_reference_lap.py .......  [100%]

============================== 7 passed in 0.85s ==============================
```

**Result:** pass.

### Required Evidence 2 — simplification_limits (LOAD-BEARING)

```bash
cd C:/Programs/f1brainz-wt/epic659-662
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m src.utils.simplification_limits --paths src/physics/segment_map/derivation/reference_lap.py
```
```
PASS (1 files checked)
```

**Result:** pass.

### Supplementary — real-store end-to-end run (2026 Australia Q, before the smoke test was folded in)

```
n_laps_pooled 246
lap_length_m 5223.391179795679
distance_m range 0.0 5218.02223880081
v_ref range 25.786861238703246 79.77453703703601
brake_active_frac range 0.0 0.9634146341463414
curvature range -0.031585043742020515 0.034254543137452666
```
Albert Park's nominal lap length is ~5278 m; 5223 m is plausible for the pooled/smoothed reference
geometry. Speed range 25.8-79.8 m/s = 93-287 km/h, plausible for a quali lap. All finite, all in-range.

## TDD evidence

- Failing test observed: ran `test_reference_lap.py` before `reference_lap.py` existed — all 6 tests
  failed with `ModuleNotFoundError: No module named 'src.physics.segment_map.derivation'`.
- Passing test observed: same 6 tests passed on the FIRST attempt after writing `reference_lap.py`
  (no rework cycle needed); the 7th (store smoke) test was added afterward for the convenience loader
  and also passed on first attempt.
- Refactor while green: no refactor pass was needed; the implementation was accepted as first-written.

## Store seam reused (confirmatory, per Required Evidence)

**Exact function called:** `src.physics.session_fit.load_quali_session(year, gp_name, session_type, cache=..., offline=..., store=...)`.

**Return shape:** `(session, rho, rho_is_fallback)` where:
- `session` — a FastF1-session-shaped object. In this environment it resolved to
  `src.data.telemetry_session.DBSession` (the durable store WAS present), exposing:
  `session.car_data[driver_num] -> DataFrame(SessionTime, Speed, Throttle, Brake, nGear, DRS)`,
  `session.pos_data[driver_num] -> DataFrame(SessionTime, X, Y, Z)` (decimetres, raw),
  `session.laps.pick_drivers(abbreviation) -> DataFrame(Driver, LapNumber, Stint, LapTime,
  LapStartTime, Time)` (Timedelta columns), `session.get_driver(id) -> dict(DriverNumber,
  Abbreviation, TeamName)`, `session.drivers -> list[str]` of driver **numbers** (car_data keys).
  Falls back to a FastF1-cache-backed session (same surface) when the store is absent.
- `rho` — float, air density (kg/m^3), unused by this gate (no physics estimation happens in G1).
- `rho_is_fallback` — bool, unused by this gate.

**Per-lap extraction (my own code, not part of the cited seam):** for each driver, position/speed
extracted via `src.preprocessing.trajectory.loaders.driver_streams(session, driver_num)` (returns
`(pos_d, spd_d)` dicts with keys `t/X/Y/Z` metres-and-seconds and `t/V` m/s-and-seconds respectively —
already metres/m/s, per that module's binding unit-conversion contract). Each clean lap's window
`[LapStartTime, Time]` (session seconds) slices `pos_d` for XY, then speed is `np.interp`-ed and brake
is nearest-sampled onto those same position timestamps so all three per-lap channels are parallel
arrays (`build_reference_lap`'s contract — see Assumptions).

## Brake source field (confirmatory, per Required Evidence)

`session.car_data[driver_num]["Brake"]` (the same column `session_fit._build_control_df` already reads
for its `control_df.brake` field), cast to float and treated as **nonzero = braking**. This is a raw
per-sample indicator column (boolean-like in the store: 0.0/1.0), nearest-sample-resampled per lap onto
the position sample times, then per-grid-point mean-pooled across laps into
`ReferenceLap.brake_active_frac` — a fraction in `[0, 1]` that later gates (G2's corner/braking gate) can
threshold for braking-zone onset/offset, as the handoff specifies.

## Assumptions

- **Clean flying lap filter (G1's minimal filter, no new threshold):** `LapTime.notna()` and
  `LapTime > 50.0 s`. This reuses the exact numeric floor `session_fit.fit_driver` already applies
  (`valid = valid[valid["LapTime"].dt.total_seconds() > 50]`) to reject aborted/implausible laps — not
  an invented constant. G1 does NOT do the fastest-lap-fraction ("flying lap") pooling `session_fit`
  additionally applies (its `_FLY_FRACTION = 1.08`); the handoff says "no thresholds here (frozen
  constants belong to later gates)", so I deliberately pooled ALL laps clearing the 50s floor across the
  WHOLE field rather than each driver's fastest-N%, on the reading that "clean" (G1's job: reject
  garbage) is distinct from "representative/fastest" (a later-gate concern). This is a judgment call
  within my latitude, not a settled decision — flagging it explicitly in case a later gate expected a
  tighter filter.
- **Per-lap channel contract:** `build_reference_lap`'s `laps_speed[i]`/`laps_brake[i]` must be the SAME
  LENGTH as `laps_xy[i]` (parallel arrays, sampled at the same points), not independently-timed streams.
  I chose this over an index-fraction proxy (the pattern `ribbon.drs_zone_mask` already uses in
  production) because the handoff's Close Criteria explicitly says "by **that lap's normalized
  arc-length** u=s/s[-1]" for speed/brake pooling — a real arc-length parameterisation requires knowing
  each speed/brake sample's own position, which only the parallel-array contract can provide honestly.
  `reference_lap_from_store` satisfies this contract by interpolating car_data onto pos_data's sample
  times before calling the core.
- **Brake resampling method:** nearest-sample (not linear interpolation) for the discrete brake channel,
  matching `ribbon.drs_zone_mask`'s already-established convention for pooling a boolean per-lap signal
  onto a shared grid — avoids inventing fractional in-between brake states.
- **`lap_length_m`:** computed as `distance_m[-1] + closing-segment-length` (Euclidean px[0]-to-px[-1]),
  since `build_ribbon`'s periodic geometry returns arc length TO each station but does not fold the
  final wrap-around segment into `distance_m` itself.
- Air density (`rho`, `rho_is_fallback`) from `load_quali_session` is accepted but unused — G1 does no
  physics estimation.

## Stop conditions hit
None. The store-first seam (`session_fit.load_quali_session`) was reusable without editing any
`segment_map` runtime file and without calling FastF1 directly; both required evidence commands were
producible; no decision outside the handoff's Authority section was needed (the abbreviation-vs-number
`pick_drivers` fallback and the 50s clean-lap floor were both within "you MAY decide the internal
dataclass shape and the exact store seam you reuse").

## Out-of-scope observations
- None found as defects. One forward-looking note (not a defect): `DBSession.laps` (the `_ShimLaps`
  wrapper) has no `PitInTime`/`PitOutTime` columns, unlike a real FastF1 `Laps` object — a future gate
  reusing `ribbon.py`'s private `_get_clean_laps` helper (which does `row.get("PitInTime")`) against a
  `DBSession` would silently skip the pit-lap filter rather than erroring, because `.get()` on a missing
  column returns `None` and `pd.notna(None)` is `False`. I did not reuse that helper (I wrote my own
  minimal filter) specifically to sidestep this, but it's worth flagging for whoever next touches
  `ribbon.py` against `DBSession` inputs.

## Workflow Feedback

- **Handoff gaps:** the Close Criteria's phrase "by that lap's normalized arc-length u=s/s[-1]" doesn't
  say whether `laps_speed`/`laps_brake` are expected to be parallel-sampled with `laps_xy` (my reading)
  or independently-timed streams resampled by an index/time proxy (the pattern already used by
  `ribbon.drs_zone_mask` in this same file). Both readings are defensible from the prose alone; I picked
  the parallel-array reading because it's the only one that makes "arc-length" (as opposed to "time" or
  "index") literally true, and documented the choice prominently in the module docstring and this
  result. A future gate calling `build_reference_lap` directly (not through `reference_lap_from_store`)
  needs to know this contract up front — worth pinning explicitly in the next handoff that references it.
- **Context rediscovered:** `tele_laps.driver` (hence FastF1-shaped `Laps.pick_drivers`) is keyed by
  **abbreviation**, while `DBSession.drivers`/`car_data`/`pos_data` are keyed by **driver number** — this
  wasn't stated anywhere in the handoff or the cited source docstrings and required a direct sqlite query
  against the real store to confirm. Worth a one-line addition to `telemetry_session.py`'s module
  docstring (which already documents the FastF1-shaped surface in detail) for the next agent who needs to
  enumerate the field.
- **Instructions improvised around:** none — the handoff's "you MAY decide... the exact store seam you
  reuse (cite it)" latitude covered everything I needed to decide.
- **What would have made this easier:** a one-line note in the handoff on whether "clean flying laps"
  means G1's own minimal garbage-filter (what I did) or additionally the fastest-N% pooling `session_fit`
  applies elsewhere in the codebase — I resolved it by reading "no thresholds here" as ruling out the
  latter, but it's the kind of ambiguity a future reviewer might read differently.

## Return status
`complete`
