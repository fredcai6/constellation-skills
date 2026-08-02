# Implementer Handoff

## Gate
`g1` (work-id `575-fuel-burn-calibration`, issue #575)

## Task
Build and validate a ZERO-FIT, per-season fuel burn-rate estimator derived
directly from telemetry + the FIA's own regulated fuel-flow limit — do NOT
wire it into `mass_model.py` yet. This gate produces evidence to answer one
question: does the "boring" relationship `lap_burn_kg ≈ flow_rate_cap_kg_per_s
× mean_throttle_fraction × lap_duration_s` actually hold up against real data?

## Protected Intent
- `src/physics/mass_model.py` stays byte-for-byte unchanged (read-only
  reference only) — no wiring, no constant changes, in this gate.
- The new estimator has ZERO fitted/regressed parameters. The flow-rate cap
  is a literal, cited regulatory constant, not something derived from data.
- Every season is computed fully independently — no cross-season pooling,
  shrinkage, or averaging of any kind (not for the throttle-integral
  estimate, not for the lap-time-slope cross-check).

## Test Mode
Test-after allowed (new standalone analysis module, no existing behavior to
protect via TDD) — but the module's pure-arithmetic core (the burn formula
itself, given throttle/duration/flow-rate inputs) must have direct unit tests
with hand-computed expected values (this is a formula with no external
dependency, straightforward to test as a pure function).

## Close Criteria
- `src/physics/burn_rate_calibration.py` exists, containing:
  - A cited per-season FIA fuel-regulation table: flow-rate cap (kg/h) and
    max race-start fuel (kg). Values: fuel-flow rate is a flat **100 kg/h**
    mass limit for **2014–2025** (unchanged across that whole span); from
    **2026** the limit becomes energy-based (**3000 MJ/h**, reported as
    ≈**70 kg/h** equivalent for the Advanced Sustainable Fuel energy
    density). Max race-start fuel: **110 kg** for 2019–2025, cut to **70 kg**
    for 2026. Cite these as a code comment/docstring (source: formula1.com
    "7 things you need to know about the 2026 F1 engine regulations";
    f1chronicle.com "F1 Fuel Flow in 2026: 3000MJ/h and the 70kg Race
    Allowance"; do not silently invent other seasons' figures — only 2019
    onward is needed, matching `SEASON_BASE_KG`'s existing earliest year).
  - A pure function computing per-lap burn from
    `(flow_rate_cap_kg_per_s, mean_throttle_fraction, lap_duration_s)` — unit
    tested directly with hand-computed values (e.g. 100 kg/h cap, throttle=1.0
    for 60s → 100/3600*60 ≈ 1.667 kg).
  - A per-season aggregator that, for a given `(year, gp_name)`, loads the
    race session via the telemetry-store seam below, computes each clean
    lap's burn estimate, and averages across laps/drivers for that one
    `(year, gp_name)` — NO cross-season or cross-circuit averaging inside
    this function; the caller controls what gets aggregated together.
  - A cross-check function comparing the throttle-integral estimate against
    an independent lap-time-slope estimate (OLS `lap_time ~ lap_number` on
    green-flag laps) at a given circuit, reporting both numbers plus the
    model's predicted slope at the throttle-derived kg/lap (reuse the same
    math style already prototyped in the uncommitted
    `scripts/mass_validation_dashboard.py` panel C — read it for reference,
    do not import or modify it).
- `scripts/validate_burn_rate_hypothesis.py` — a runnable script that, for
  seasons **2019–2026** and circuits **Bahrain, Spain (2026: use
  `"Barcelona-Catalunya"` — verified via `SELECT DISTINCT gp_name FROM
  sessions WHERE session_type='R'` against `data/f1_data_2026.db`, which has
  NO Bahrain round and names the Spain-equivalent round
  `"Barcelona-Catalunya"`), Silverstone, Monaco**:
  1. Prints/tabulates the throttle-integral kg/lap estimate per (season, circuit).
  2. Prints/tabulates the lap-time-slope cross-check per (season, circuit):
     observed slope, throttle-derived model-predicted slope, %error.
  3. Explicitly calls out the expected pattern: agreement at Bahrain/Spain/
     Silverstone; a larger gap at Monaco (known pace-management confound) —
     report whether this pattern is actually observed, do not just assert it.
  4. Computes and prints the SC/VSC-vs-green throttle-integral burn ratio
     (join `lap_times.track_status` from the season's `data/f1_data_{year}.db`
     — non-`'1'` status = SC/VSC, matching `mass_model.fuel_at_lap`'s own
     status convention) and reports it next to the existing hardcoded
     `SC_BURN_FRACTION = 0.5` for comparison — informational only, do not
     change `SC_BURN_FRACTION`.
  5. Handles a season/circuit combination with too little data (e.g. 2026
     Monaco/Silverstone/Barcelona-Catalunya only has however many races are
     actually collected — verify via the DB `has_lap_times`/`has_telemetry`
     flags first) by skipping with a printed reason, not crashing or
     silently faking a number.
- New unit tests under `tests/unit/physics/test_burn_rate_calibration.py`
  covering: the pure burn-formula function (hand-computed values), the
  regulation table (correct values for at least 2023 and 2026), and the
  per-season aggregator/cross-check functions against a small synthetic
  telemetry-store fixture (do not require a live DB for the test suite —
  build a minimal fixture, consistent with how existing physics tests avoid
  live-DB dependencies; check `tests/unit/physics/test_mass_model.py` and
  `tests/unit/physics/layer2/` for the fixture-building convention already
  used in this test tree).
- `py -m src.utils.simplification_limits` clean on touched `src/` and
  `tests/` paths.

## Allowed Scope
- New file: `src/physics/burn_rate_calibration.py`
- New file: `scripts/validate_burn_rate_hypothesis.py`
- New file: `tests/unit/physics/test_burn_rate_calibration.py`
- Read-only: `src/physics/mass_model.py`, `src/data/telemetry_store.py`,
  `src/data/telemetry_session.py`, `scripts/mass_validation_dashboard.py`
  (reference only, do not modify or import from it)

## Specific Exclusions
- Do NOT modify `src/physics/mass_model.py` (no new constants, no signature
  changes) — this gate is validation-only.
- Do NOT modify or delete the pre-existing UNTRACKED scratch scripts already
  in the working tree: `scripts/mass_validation_dashboard.py`,
  `scripts/mass_fuel_dashboard.py`, `scripts/bahrain_frontier_validation.py`,
  `scripts/build_lateral_load_cache.py`, `scripts/lateral_load_unitization.py`,
  `scripts/tyre_age_overview.py`, `scripts/tyre_degradation_validation.py` —
  these belong to a different, unrelated prior thread of work and are simply
  sitting untracked in this working copy. Do not `git add` them either.
- Do NOT re-run or modify any batch population scripts
  (`fit_batch.py`/`estimate_batch.py`/`race_stint_batch.py`).
- Do NOT change `SC_BURN_FRACTION` or any other `mass_model.py` constant.

## Constraints
- DB-only/telemetry-store-only data access (no direct FastF1 calls). Reuse
  the EXACT existing seam: `TelemetryStore().read_session(year, gp_name,
  'R')` (from `src.data.telemetry_store`) fed into
  `src.data.telemetry_session.build_db_session(...)`, which returns a
  `DBSession` with `.car_data` (dict keyed by driver -> DataFrame with
  `Throttle` (0-100 scale) and `SessionTime` as a `pd.Timedelta` column) and
  `.laps` (a `_ShimLaps` wrapper over a DataFrame with columns `Driver`,
  `LapNumber`, `Stint`, `LapTime`, `LapStartTime`, `Time` — all as
  `pd.Timedelta` except `Driver`/`LapNumber`/`Stint`). `.laps.pick_drivers(id)`
  filters by driver abbreviation. Verified present for race sessions (checked
  2023 Bahrain R: `tele_car.throttle` + `tele_laps.lap_start_time_s`/
  `lap_end_time_s` both populated).
- Per-lap green-flag/clean-lap filtering should follow the same convention
  already used elsewhere in this codebase for race-lap population
  (`lap_times.track_status='1'`, no pit in/out, valid lap) — see
  `scripts/mass_validation_dashboard.py::_green_race_laps` for the exact
  query shape (reference only, do not import it).
- No cross-season pooling/shrinkage anywhere in this gate.
- No regression/fitted parameters in the primary estimator — the flow-rate
  cap is the literal regulated constant.
- Cite the regulatory source values inline as a comment/docstring.

## Map Anchors (inbound)
- **Structural:** `struct:physics` — `src/physics/mass_model.py` (read-only:
  `DEFAULT_BURN_PER_LAP_KG`, `MAX_FUEL_KG`, `SC_BURN_FRACTION`,
  `SEASON_BASE_KG` pattern to follow for the new regulation table).
  `struct:data` — `src/data/telemetry_store.py` (`TelemetryStore.read_session`),
  `src/data/telemetry_session.py` (`build_db_session`/`DBSession` shim) — the
  seam to reuse.
- **Capability:** physics mass/fuel accounting — currently a flat all-season
  burn constant; this gate produces validation evidence only, no behavior
  change.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import` (no
  evo-region imports from `src/physics/`); ORCHESTRATOR_CONTEXT canonical-data
  constraint (DB/telemetry-store only, no direct FastF1).
- **Decision anchors:** decision pressure `decision:burn_rate_calibration_design`
  — regulation-anchored, zero-fit throttle-integral, independently-per-season,
  no pooling; the wiring decision is explicitly deferred to the human after
  this gate, do not pre-empt it.
- **Evidence expectations:** report real per-(season, circuit) numbers for
  the cross-check and the SC/VSC ratio — a claim without numbers doesn't
  satisfy this gate.
- **Map confidence flags:** none — this is genuinely new structure, no prior
  packet documents a burn-rate calibration module.

## Required Evidence
- The new module + script + tests, committed to the branch (or ready to
  stage — Commander handles the actual `git add`/commit).
- Full text output of running `scripts/validate_burn_rate_hypothesis.py`
  (paste or summarize the per-season/per-circuit table + SC/VSC ratio in the
  IMPLEMENTER_RESULT).
- `py -m pytest tests/unit/physics/test_burn_rate_calibration.py -q` output.

## Verification Commands

```bash
py -m pytest tests/unit/physics/test_burn_rate_calibration.py -q
py scripts/validate_burn_rate_hypothesis.py
py -m src.utils.simplification_limits src/physics/burn_rate_calibration.py scripts/validate_burn_rate_hypothesis.py tests/unit/physics/test_burn_rate_calibration.py
```

## Suggested Model Tier
Stronger — reason: this is a genuinely new physics-region estimator with a
real hypothesis to validate (not a mechanical change), touching telemetry
data plumbing and requiring judgment about clean-lap filtering, SC/VSC status
joins, and honest reporting of whether the hypothesis holds or doesn't.

## Authority
Already decided (do not re-litigate): wire-vs-defer → deferred, this gate is
validation only; pooling → none, per-season and per-circuit independent;
primary method → throttle-integral zero-fit estimator, not lap-time-slope
regression; cross-check circuit set → Bahrain, Spain/Barcelona-Catalunya,
Silverstone, Monaco (not just two anchors); regulation figures → as cited
above. If evidence suggests the hypothesis clearly does NOT hold (large,
unexplained divergence even at Bahrain/Spain/Silverstone), report that
plainly as the finding — do not tune the method until it agrees, and do not
decide unilaterally to change scope; stop and return with the evidence.

## Stop Conditions
Stop and return if: the telemetry store lacks throttle/lap-boundary data for
enough of the target seasons/circuits to compute anything meaningful; the
seam signature differs from what's cited above; a decision beyond this
handoff's authority is needed (e.g. whether to widen scope back to wiring).

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode
satisfied, evidence produced (paste the key validation numbers, don't just
say "passed"), assumptions used, stop conditions hit, out-of-scope
observations, workflow feedback.
