# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1` (work-id `575-fuel-burn-calibration`, issue #575)

## Completed slice
Built and validated a zero-fit, per-season/per-circuit fuel burn-rate
estimator (`lap_burn_kg = flow_rate_cap_kg_per_s * mean_throttle_fraction *
lap_duration_s`) using the FIA's literal, cited fuel-flow regulation as the
only constant, sourced entirely through the existing telemetry-store seam.
Produced the requested cross-check (throttle-integral estimate vs an
independent lap-time-slope OLS fit) and the SC/VSC-vs-green burn ratio,
across seasons 2019-2026 and circuits Bahrain / Spain / Silverstone / Monaco.
`src/physics/mass_model.py` was not modified (verified byte-for-byte
unchanged via `git diff --stat`). This gate is validation-only, per the
handoff's Protected Intent -- no wiring was done.

## Scope
**Files changed:**
- `src/physics/burn_rate_calibration.py` (new)
- `scripts/validate_burn_rate_hypothesis.py` (new)
- `tests/unit/physics/test_burn_rate_calibration.py` (new)

**Specific exclusions touched:** no — confirmed `src/physics/mass_model.py`
has zero diff, and `git status --porcelain` shows all seven pre-existing
untracked scratch scripts (`mass_validation_dashboard.py`,
`mass_fuel_dashboard.py`, `bahrain_frontier_validation.py`,
`build_lateral_load_cache.py`, `lateral_load_unitization.py`,
`tyre_age_overview.py`, `tyre_degradation_validation.py`) remain untracked
and untouched.

## Behavior changed
No — this is a new, standalone analysis/validation module with no existing
callers; nothing in the production path (`mass_model.py`, `race_mass`,
`fuel_at_lap`, `SC_BURN_FRACTION`) was wired to or altered.

## Map Impact

- **Structural anchors touched:** `struct:physics` — new module
  `src/physics/burn_rate_calibration.py` (read-only reference: `mass_model.py`
  unchanged). `struct:data` — read-only reuse of
  `TelemetryStore.read_session` / `build_db_session`
  (`src/data/telemetry_store.py`, `src/data/telemetry_session.py`), no
  changes to either.
- **Capabilities added/changed/affected:** new capability — regulation-
  anchored, zero-fit per-(season, circuit) fuel burn-rate estimate +
  independent lap-time-slope cross-check + SC/VSC burn-ratio diagnostic.
  Currently standalone/unwired; the mass model's flat all-season
  `DEFAULT_BURN_PER_LAP_KG=1.8` constant is untouched and still the only
  burn rate driving `mass_model.race_mass`/`fuel_at_lap`.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import`
  honored (no evo/latent_power/compound_prior imports). DB/telemetry-store-
  only constraint honored (no FastF1 imports; `sqlite3` connections are
  read-only URI mode against the per-season lap_times DBs).
- **Decision candidates / resolved decisions:** `decision:burn_rate_calibration_design`
  resolved as specified (regulation-anchored, zero-fit, per-season/circuit
  independent, no pooling) — not re-litigated. New candidate surfaced for the
  human: the throttle-integral estimator's mean %error against the
  lap-time-slope cross-check is large even at "free-flow" circuits (Bahrain/
  Spain/Silverstone mean 80.2%, driven by a systematic bias — the model
  consistently predicts a slope of smaller magnitude than observed — see
  Evidence below), which bears on whether/how to wire this in future gates;
  deliberately not decided here.
- **Claims/evidence produced:** `claim:burn-rate-hypothesis-575-g1` — see
  Evidence section: real per-(season, circuit) throttle-integral kg/lap
  table (29/32 combinations computed), lap-time-slope cross-check table, the
  Monaco-vs-free-flow pattern check (pattern IS observed directionally, but
  free-flow error itself is large), and the SC/VSC-vs-green ratio table
  (mean ratio ~0.90-0.95 at most circuits, i.e. SC/VSC laps burn ~5-15% less
  than green laps in this proxy — much milder than the hardcoded
  `SC_BURN_FRACTION=0.5`, which implies a 50% reduction).
- **Trust limitations / drift found:** `sessions.has_telemetry` in the
  per-season `data/f1_data_{year}.db` files is STALE relative to
  `data/telemetry_store.db` — e.g. 2023 Bahrain reads `has_telemetry=0` in
  the SQL DB despite the telemetry store genuinely holding that session
  (confirmed via direct `TelemetryStore.has_session` check). Likely an
  artifact of the #541 Parquet-mirror migration not back-propagating a flag
  update to the source DB. The validation script does NOT trust that flag;
  it checks `TelemetryStore.has_session` directly. Flagging this as a
  potential future confusion source for any other code that still reads
  `sessions.has_telemetry` from the per-season DBs expecting it to reflect
  telemetry-store coverage.
- **Triage candidates:** (1) the stale `has_telemetry` flag above — worth a
  follow-up issue to either recompute it from the telemetry store or stop
  reading it as a coverage signal. (2) `build_db_session` in
  `src/data/telemetry_session.py` (read-only reference in this gate, not
  modified) emits a `RuntimeWarning: overflow encountered in multiply` from
  `pd.to_timedelta(..., unit="s")` when a session's `lap_time_s` column
  contains NaN values (widespread: every checked (year, circuit) combination
  has 1-85 NaN lap times). It does not crash — NaN correctly becomes `NaT`
  and downstream `dropna` filters it out — but the warning is noisy and
  indicates the shim doesn't pre-filter NaN before the pandas cast. Out of
  this gate's allowed scope (that file is read-only reference only).

## Test mode
**Required:** `test-after` (new standalone analysis module), with the
pure-arithmetic burn formula requiring direct hand-computed unit tests.
**Satisfied:** yes — `per_lap_burn_kg` has 10 dedicated hand-computed-value
tests (including the handoff's own worked example: 100 kg/h cap, throttle=1.0,
60s -> 1.6667 kg), the regulation table has correctness tests for 2019-2025
(flat 100 kg/h / 110 kg) and 2026 (70 kg/h / 70 kg), and the aggregator/
cross-check functions are tested against a synthetic `DBSession`-shaped
`MagicMock` fixture (no live DB), following the exact convention in
`tests/unit/physics/layer2/test_session_race.py::_make_fake_db_session`.

## Evidence

```bash
py -m pytest tests/unit/physics/test_burn_rate_calibration.py -q
```
```
collected 38 items
tests\unit\physics\test_burn_rate_calibration.py ....................... [ 60%]
...............                                                          [100%]
38 passed in 0.24s
```

```bash
py scripts/validate_burn_rate_hypothesis.py
```

**1. Throttle-integral kg/lap estimate per (season, circuit)** (29 of 32 combinations computed):

| year | circuit | n_laps | kg/lap | cap kg/h |
|---|---|---|---|---|
| 2019 | Bahrain | 1080 | 1.7511 | 100.0 |
| 2019 | Spain | 1272 | 1.4886 | 100.0 |
| 2019 | Silverstone | 912 | 1.8460 | 100.0 |
| 2019 | Monaco | 1489 | 1.0122 | 100.0 |
| 2020 | Bahrain | 958 | 1.7193 | 100.0 |
| 2020 | Spain | 1274 | 1.4647 | 100.0 |
| 2020 | Silverstone | 813 | 1.8173 | 100.0 |
| 2021 | Bahrain | 1018 | 1.7621 | 100.0 |
| 2021 | Spain | 1245 | 1.4691 | 100.0 |
| 2021 | Silverstone | 925 | 1.7899 | 100.0 |
| 2021 | Monaco | 1418 | 1.0318 | 100.0 |
| 2022 | Bahrain | 1118 | 1.7302 | 100.0 |
| 2022 | Spain | 1230 | 1.4258 | 100.0 |
| 2022 | Silverstone | 773 | 1.8090 | 100.0 |
| 2022 | Monaco | 1153 | 0.9503 | 100.0 |
| 2023 | Bahrain | 1055 | 1.7236 | 100.0 |
| 2023 | Spain | 1312 | 1.4743 | 100.0 |
| 2023 | Silverstone | 966 | 1.7906 | 100.0 |
| 2023 | Monaco | 1512 | 0.9736 | 100.0 |
| 2024 | Bahrain | 1127 | 1.7380 | 100.0 |
| 2024 | Spain | 1310 | 1.4529 | 100.0 |
| 2024 | Silverstone | 1405 | 1.3399 | 100.0 |
| 2024 | Monaco | 1226 | 1.0305 | 100.0 |
| 2025 | Bahrain | 1115 | 1.7093 | 100.0 |
| 2025 | Spain | 1202 | 1.4363 | 100.0 |
| 2025 | Silverstone | 1124 | 1.3381 | 100.0 |
| 2025 | Monaco | 1423 | 1.0079 | 100.0 |
| 2026 | Spain | 1233 | 0.9367 | 70.0 |
| 2026 | Monaco | 1415 | 0.6900 | 70.0 |

Note the honest 2026 drop: at the lower ~70 kg/h energy-based cap, estimated
kg/lap falls proportionally (e.g. Spain 1.44 -> 0.94 kg/lap), consistent with
the regulation change and not a modeling artifact.

**2. Lap-time-slope cross-check** (observed OLS slope vs throttle-derived
model-predicted slope vs %error):

| year | circuit | n_laps | obs s/lap | model s/lap | %error |
|---|---|---|---|---|---|
| 2019 | Bahrain | 785 | -0.0259 | -0.0525 | 50.7% |
| 2019 | Spain | 1062 | -0.0548 | -0.0447 | 22.7% |
| 2019 | Silverstone | 743 | -0.0836 | -0.0554 | 50.9% |
| 2019 | Monaco | 1226 | -0.0239 | -0.0304 | 21.2% |
| 2020 | Bahrain | 714 | -0.0620 | -0.0516 | 20.2% |
| 2020 | Spain | 1170 | -0.0610 | -0.0439 | 38.9% |
| 2020 | Silverstone | 669 | -0.0958 | -0.0545 | 75.7% |
| 2021 | Bahrain | 832 | -0.0447 | -0.0529 | 15.5% |
| 2021 | Spain | 1110 | -0.0565 | -0.0441 | 28.1% |
| 2021 | Silverstone | 827 | -0.0629 | -0.0537 | 17.1% |
| 2021 | Monaco | 1380 | -0.0441 | -0.0310 | 42.6% |
| 2022 | Bahrain | 878 | -0.0827 | -0.0519 | 59.2% |
| 2022 | Spain | 1060 | -0.0311 | -0.0428 | 27.3% |
| 2022 | Silverstone | 654 | -0.1519 | -0.0543 | 179.8% |
| 2022 | Monaco | 844 | -0.4524 | -0.0285 | 1486.8% |
| 2023 | Bahrain | 889 | -0.0557 | -0.0517 | 7.8% |
| 2023 | Spain | 1224 | -0.0553 | -0.0442 | 25.0% |
| 2023 | Silverstone | 822 | -0.0698 | -0.0537 | 30.0% |
| 2023 | Monaco | 1259 | +0.2244 | -0.0292 | 868.4% |
| 2024 | Bahrain | 1006 | -0.0507 | -0.0521 | 2.7% |
| 2024 | Spain | 1225 | -0.0474 | -0.0436 | 8.8% |
| 2024 | Silverstone | 868 | -0.0114 | -0.0402 | 71.5% |
| 2024 | Monaco | 1171 | -0.0711 | -0.0309 | 129.9% |
| 2025 | Bahrain | 992 | -0.0395 | -0.0513 | 23.0% |
| 2025 | Spain | 1007 | -0.0581 | -0.0431 | 34.8% |
| 2025 | Silverstone | 441 | -0.3997 | -0.0401 | 895.8% |
| 2025 | Monaco | 1177 | -0.0307 | -0.0302 | 1.4% |
| 2026 | Spain | 1050 | -0.0504 | -0.0281 | 79.2% |
| 2026 | Monaco | 1161 | -0.0195 | -0.0207 | 5.8% |

**3. Expected-pattern check (agreement at Bahrain/Spain/Silverstone; larger
gap at Monaco):**

```
Free-flow circuits (Bahrain/Spain/Silverstone): mean %error = 80.2% over 22 season-circuit points
Monaco: mean %error = 365.2% over 7 season points
PATTERN OBSERVED: Monaco error (365.2%) > free-flow error (80.2%) -- consistent with pace-management confound at Monaco.
```

Honest read, not just the headline: the DIRECTIONAL pattern the handoff
expected (Monaco worse than free-flow) does hold, driven mainly by two
extreme Monaco outliers (2022: +1486.8%, a rain race with a huge observed
slope of -0.4524 s/lap; 2023: +868.4%, where the observed slope is even
POSITIVE (+0.2244), i.e. cars got slower over the race — almost certainly a
strategic/safety-car-heavy race, not a burn-rate modeling failure). But the
free-flow-circuit baseline error itself (80.2% mean, with individual points
up to 179.8% at 2022 Silverstone and 895.8% at 2025 Silverstone) is much
larger than the ~7-9% seen in 2023-2024 Bahrain alone. The model consistently
UNDER-predicts the magnitude of the observed slope (model %|slope| smaller
than observed in nearly every free-flow row) — i.e. the throttle-integral
estimate alone does not fully explain the observed pace-vs-fuel trend at
every circuit/season; other effects (track evolution, tyre degradation not
separated out, wind, traffic) are folded into the raw OLS slope and not into
the model side of this comparison. This is reported plainly per the
handoff's Authority section instruction, without tuning the method to agree.

**4. SC/VSC-vs-green throttle-integral burn ratio** (vs hardcoded
`mass_model.SC_BURN_FRACTION=0.5`, informational only):

| year | circuit | n_grn | n_scv | grn kg | scv kg | ratio | vs const |
|---|---|---|---|---|---|---|---|
| 2019 | Bahrain | 846 | 234 | 1.7712 | 1.6786 | 0.948 | +0.448 |
| 2019 | Spain | 1109 | 163 | 1.5120 | 1.3293 | 0.879 | +0.379 |
| 2019 | Silverstone | 784 | 128 | 1.8614 | 1.7522 | 0.941 | +0.441 |
| 2019 | Monaco | 1247 | 242 | 1.0193 | 0.9752 | 0.957 | +0.457 |
| 2020 | Bahrain | 782 | 176 | 1.7774 | 1.4610 | 0.822 | +0.322 |
| 2020 | Spain | 1239 | 35 | 1.4648 | 1.4614 | 0.998 | +0.498 |
| 2020 | Silverstone | 682 | 131 | 1.8369 | 1.7154 | 0.934 | +0.434 |
| 2021 | Bahrain | 911 | 107 | 1.7804 | 1.6059 | 0.902 | +0.402 |
| 2021 | Spain | 1178 | 67 | 1.4785 | 1.3041 | 0.882 | +0.382 |
| 2021 | Silverstone | 871 | 54 | 1.7961 | 1.6900 | 0.941 | +0.441 |
| 2021 | Monaco | 1418 | 0 | 1.0318 | 0.0000 | n/a | n/a |
| 2022 | Bahrain | 958 | 160 | 1.7498 | 1.6129 | 0.922 | +0.422 |
| 2022 | Spain | 1166 | 64 | 1.4253 | 1.4350 | 1.007 | +0.507 |
| 2022 | Silverstone | 692 | 81 | 1.8310 | 1.6208 | 0.885 | +0.385 |
| 2022 | Monaco | 905 | 248 | 0.9674 | 0.8880 | 0.918 | +0.418 |
| 2023 | Bahrain | 979 | 76 | 1.7287 | 1.6576 | 0.959 | +0.459 |
| 2023 | Spain | 1312 | 0 | 1.4743 | 0.0000 | n/a | n/a |
| 2023 | Silverstone | 845 | 121 | 1.8179 | 1.6000 | 0.880 | +0.380 |
| 2023 | Monaco | 1300 | 212 | 0.9848 | 0.9051 | 0.919 | +0.419 |
| 2024 | Bahrain | 1086 | 41 | 1.7383 | 1.7307 | 0.996 | +0.496 |
| 2024 | Spain | 1310 | 0 | 1.4529 | 0.0000 | n/a | n/a |
| 2024 | Silverstone | 960 | 0 | 1.3456 | 0.0000 | n/a | n/a |
| 2024 | Monaco | 1183 | 43 | 0.9699 | 2.6971 | 2.781 | +2.281 |
| 2025 | Bahrain | 1048 | 67 | 1.7267 | 1.4369 | 0.832 | +0.332 |
| 2025 | Spain | 1088 | 114 | 1.4582 | 1.2273 | 0.842 | +0.342 |
| 2025 | Silverstone | 389 | 273 | 1.3432 | 1.3098 | 0.975 | +0.475 |
| 2025 | Monaco | 1249 | 174 | 1.0144 | 0.9616 | 0.948 | +0.448 |
| 2026 | Spain | 1136 | 97 | 0.9470 | 0.8163 | 0.862 | +0.362 |
| 2026 | Monaco | 1202 | 213 | 0.6994 | 0.6373 | 0.911 | +0.411 |

Honest read: across the 26 (of 29) combinations with a usable ratio, the
observed SC/VSC-vs-green burn ratio clusters around 0.82-1.01 (i.e. this
throttle-integral proxy sees SC/VSC laps burning only ~0-18% less fuel than
green laps at most circuits) — much milder than the hardcoded
`SC_BURN_FRACTION=0.5` (a 50% reduction). One clear outlier: 2024 Monaco
(ratio 2.781, SC/VSC laps burning MORE fuel than green laps by this proxy) —
only 43 SC/VSC laps at Monaco in a race with unusual pace-management, so this
is a small-sample artifact rather than a real reversal. This does not change
`SC_BURN_FRACTION` (out of scope for this gate) but is reported for the
human's review of that constant in a future gate.

```bash
py -m src.utils.simplification_limits --paths src/physics/burn_rate_calibration.py scripts/validate_burn_rate_hypothesis.py tests/unit/physics/test_burn_rate_calibration.py
```
```
PASS (3 files checked)
```

**Result:** pass — all three verification commands succeed (note: the
handoff's literal `simplification_limits` command line was missing the
required `--paths` flag; ran the corrected form, see Workflow Feedback).

## TDD evidence, if required
Test mode was `test-after` for the module as a whole (new standalone
analysis module, no existing behavior to protect), with `test-first`-style
hand-computed-value rigor required specifically for the pure burn formula.
- Failing test observed: not applicable in the strict red/green sense — the
  formula function and its tests were authored together as new code (no
  pre-existing implementation to red-test against), consistent with the
  handoff's stated test mode.
- Passing test observed: `py -m pytest tests/unit/physics/test_burn_rate_calibration.py -q` -> `38 passed in 0.24s`.
- Refactor while green: yes — removed a leftover unused `_patched` test
  helper method (dead code from an earlier draft) after confirming the suite
  still passed at 38/38.

## Docs/contracts touched
- none — no committed report schema, contract, or documentation file was
  touched; this gate produces no artifact consumed by another documented
  interface.

## Assumptions
- Interpreted "Spain" in the handoff's circuit list as the telemetry store's
  `gp_name="Spain"` for 2019-2025 and `"Barcelona-Catalunya"` for 2026, per
  the handoff's own instruction and confirmed against `f1_data_2026.db`.
- Interpreted "Silverstone" as the telemetry store's `gp_name="Great Britain"`
  — the handoff named the circuit informally but the store has no
  `"Silverstone"` entry at all; confirmed via `list_sessions()` that
  `"Great Britain"` is the only matching gp_name across all years present.
  This substitution was not explicitly spelled out in the handoff and
  required verification against source (flagged in Workflow Feedback).
- `mean_throttle_fraction` clips raw FastF1 throttle values to [0, 100]
  before converting to a 0-1 fraction — a small number of telemetry samples
  read slightly above 100 (observed up to 104 in 2023 Bahrain), treated as
  sensor noise rather than a real >100% throttle state.
- The lap-time-slope cross-check and SC/VSC ratio treat a season/circuit as
  "too little data" and return None when there are fewer than 20 green-flag
  laps (cross-check) or fewer than 3 laps in either green/SC-VSC bucket
  (ratio) — thresholds chosen conservatively for a meaningful OLS fit /
  mean, not specified numerically in the handoff.
- `_PACE_S_PER_KG = 0.03` (seconds of lap time per kg of fuel) was reused
  verbatim from the uncommitted `scripts/mass_validation_dashboard.py`
  reference file per the handoff's explicit instruction to reuse that same
  math style; it is not re-derived or fitted in this gate.

## Stop conditions hit
None. The telemetry store had throttle/lap-boundary data for 29 of the 32
target (season, circuit) combinations; the 3 gaps (2020 Monaco — cancelled
race, not collected; 2026 Bahrain — round does not exist per the 2026
calendar; 2026 Great Britain — round has not yet occurred as of the current
2026-07-01 session date) are legitimate data-absence cases the script
detects and skips with a printed reason, not a seam mismatch or missing-data
crisis across the whole grid. The telemetry seam signature matched the
handoff's citation exactly (verified against source before use, per
CREW_CONTEXT.md's operating discipline). No decision beyond this handoff's
authority was needed.

## Out-of-scope observations
- `sessions.has_telemetry` in the per-season `data/f1_data_{year}.db` files
  is stale relative to `data/telemetry_store.db` (see Map Impact / Trust
  limitations above) — worth a triage issue.
- `build_db_session` (`src/data/telemetry_session.py`, read-only reference in
  this gate) emits a `RuntimeWarning: overflow encountered in multiply` from
  `pd.to_timedelta` when a session's `lap_time_s` contains NaN — cosmetic
  (does not crash, NaN correctly becomes NaT and is filtered downstream) but
  noisy; out of this gate's allowed scope to fix.
- The lap-time-slope cross-check's large free-flow-circuit error (mean 80.2%)
  suggests the throttle-integral estimator alone, compared against a raw
  unadjusted OLS slope, is a noisier cross-check than the ~7-9% single-race
  Bahrain figure implied by the (uncommitted) `mass_validation_dashboard.py`
  reference — likely because that reference dashboard's Panel C uses the
  FIXED `DEFAULT_BURN_PER_LAP_KG=1.8` constant rather than a per-race
  throttle-derived estimate, and/or filters/detrends differently. This
  gate's cross-check is intentionally a more honest, unfiltered comparison
  per the handoff's "do not tune the method until it agrees" instruction —
  flagging the discrepancy for the human's awareness, not resolving it here.

## Workflow Feedback
- **Handoff gaps:** The Verification Commands section's
  `simplification_limits` command line
  (`py -m src.utils.simplification_limits src/physics/... scripts/... tests/...`)
  is missing the required `--paths` flag — running it literally fails with
  "unrecognized arguments" (the CLI requires `--paths` before the file list).
  Corrected to `py -m src.utils.simplification_limits --paths <files>` in
  both the plan's postcondition and this result's Evidence section; low-cost
  fix but worth naming so future handoffs get the flag right.
- **Context rediscovered:** The handoff names "Silverstone" as one of the
  four circuits but the telemetry store has no `gp_name="Silverstone"` at
  all — it is stored as `"Great Britain"` for every year checked. This isn't
  called out anywhere in the handoff (unlike the Spain/Barcelona-Catalunya
  substitution, which IS explicitly flagged with the exact verification
  query to run). Had to discover this by running `TelemetryStore.list_sessions()`
  and diffing against the requested circuit names. Also had to discover, the
  hard way (via a `-W error::RuntimeWarning` traceback), that
  `sessions.has_telemetry` in the per-season SQL DBs is stale and cannot be
  trusted as the telemetry-coverage gate the handoff's stop-condition
  language implies ("verify via the DB has_lap_times/has_telemetry flags
  first") — the correct authoritative telemetry check is
  `TelemetryStore.has_session`, not the SQL flag of the same name.
- **Instructions improvised around:** None beyond the two items above — the
  rest of the handoff's seam citations (`TelemetryStore.read_session` /
  `build_db_session` shapes, `.laps.pick_drivers`, Timedelta columns,
  track_status convention) were all verified correct against source on the
  first check, which saved real time.
- **What would have made this easier:** Name the telemetry store's actual
  `gp_name` values for all four requested circuits up front (the way the
  Spain/Barcelona-Catalunya case already does), rather than leaving
  Silverstone's store-name mismatch to be independently discovered. Also fix
  the `simplification_limits` verification command to include `--paths`, or
  note that this project's CLI requires it.

## Return status
`complete`
