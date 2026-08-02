# Mission Frame — Issue #575: per-season fuel burn rate calibration

## Intent
**Third revision (2026-07-01, plain-text steer — narrows this run's scope):**
focus THIS run entirely on validating whether the "boring" zero-fit
relationship holds — `lap_burn_kg = flow_rate_cap_kg_per_s ×
mean_throttle_fraction × lap_duration_s` — computed independently per season,
cross-checked against the original lap-time-slope method at free-flow anchor
circuits, AND checked for whether it naturally reproduces sane SC/VSC-vs-green
burn behavior (the user's point: SC/VSC is "decidedly handled" by a
throttle-anchored estimator since low-throttle SC/VSC laps organically
produce a low estimate, without needing the existing hardcoded
`SC_BURN_FRACTION = 0.5` — worth checking whether the natural ratio is
anywhere near 0.5 as a validation signal, not an assumption). Wiring the
result into `mass_model.race_mass`/`fuel_at_lap` (previously planned G2/G3) is
explicitly DEFERRED until this validation evidence is reviewed — "worry about
wider wiring" after. This run's execute.json therefore contains ONE gate:
build the estimator + produce the cross-check/validation evidence. The
review/triage steps of the Commander spine are where the human decides
whether/how to proceed to wiring, as a follow-up.

~~Replace the flat `DEFAULT_BURN_PER_LAP_KG = 1.8` (all seasons) with a
per-season calibrated burn rate... wired into `race_mass`/`fuel_at_lap`~~ —
superseded by the above; kept struck through for the paper trail.

## Affected Capabilities
- `struct:physics` mass/fuel accounting (`mass_model.py`) — currently a pure
  arithmetic anchor with one global burn constant; this run adds a per-season
  calibration input while keeping the module DB-free and fit-free itself.

## Examples / Events
- Bahrain 2023 raw-vs-model slope match (~4% error) is the validation
  precedent already explored in the (uncommitted) `scripts/mass_validation_dashboard.py`
  — panel C already computes `avg_burn = (race_mass(...,1,n) - race_mass(...,n,n))/n`
  as the "model prediction" against observed OLS slope. This run generalizes
  that one-off comparison into a fitted per-season ratio.
- 2026 has 7 completed races in `data/f1_data_2026.db` (Australia through
  round 7 `Barcelona-Catalunya`) with `has_lap_times=1` — enough for a
  season-specific 2026 estimate now, not just a carried-forward prior.

## Structural Anchors
- `struct:physics` — `src/physics/mass_model.py` (path/symbol: `DEFAULT_BURN_PER_LAP_KG`,
  `fuel_at_lap`, `race_mass`, `TEAM_OFFSETS` precedent for "ships computed values,
  populated externally").
- `struct:physics.layer2` — `session_braking.py`, `session_traction.py`,
  `session_coast.py`, `session_estimator.py`, `session_race.py` (W3 race-stint
  path) all call `race_mass`/`quali_mass`; these are the consumers whose
  numeric output changes once the calibration is wired.
- `struct:physics.utilization` — `car_prior.py` imports `quali_mass` only (no
  race-side burn rate involved — unaffected by this run beyond the shared module).
- New module: `src/physics/burn_rate_calibration.py` (proposed) — the
  fitting/pooling logic (per-season ratio regression + historical pooling +
  2026 shrinkage), kept separate from `mass_model.py`'s pure-arithmetic design
  intent, analogous to how `layer2/pooling.py` is separate from the modules
  that consume pooled results.

## Governing Constraints / Assumptions
- `constraint:physics_region_no_evo_import` — the new calibration module stays
  within `src/physics/`, no evo-region import.
- Canonical-data constraint (`ORCHESTRATOR_CONTEXT.md`) — the per-season ratio
  fit reads the SQLite DB only (`lap_times`/`sessions`), no direct FastF1 calls;
  the per-season DB path convention (`data/f1_data_{year}.db`) is already
  established by `scripts/mass_validation_dashboard.py`/`_DEF_DB`.
- Mass-model design intent (`mass_model.py` module docstring): "Pure arithmetic
  anchors — nothing fitted or optimised here." The fitted calibration values
  are computed OFFLINE and land as literal constants in `mass_model.py`
  (matching the `SEASON_BASE_KG`/`TEAM_OFFSETS` precedent), not computed live
  at import/call time — keeps `mass_model.py` DB-free.
- `fuel_at_lap`'s `circuit` parameter is already documented "reserved for
  future per-circuit calibration; unused now" — the per-season burn rate is
  threaded in as a new *parameter* (`burn_per_lap_kg` override, default =
  `DEFAULT_BURN_PER_LAP_KG`), not as an internal season lookup inside
  `fuel_at_lap` — keeps `fuel_at_lap` itself season-agnostic and all existing
  direct callers (`scripts/mass_fuel_dashboard.py`) behavior-unchanged by default.
- **FIA regulation values (verified via web search, 2026-07-01):** fuel-flow
  rate has been a flat mass limit of **100 kg/h since 2014, unchanged through
  2025**; max race-start fuel load was **105 kg (2014-2018)**, raised to
  **110 kg in 2019** (unchanged through 2025); **2026** switches to an
  energy-based flow limit of **3000 MJ/h** (~70 kg/h equivalent for the new
  Advanced Sustainable Fuel energy density) and cuts max race fuel to **70 kg**.
  Sources: formula1.com "7 things you need to know about the 2026 F1 engine
  regulations", f1chronicle.com "F1 Fuel Flow in 2026: 3000MJ/h and the 70kg
  Race Allowance", borntoengineer.com engineering history summary. `MAX_FUEL_KG`
  is currently a single flat constant (110.0) in `mass_model.py` — it must
  become a season dict alongside this issue's burn-rate change, since it is
  independently wrong for any pre-2019 or 2026+ season use.
- Data reality (verified this run): Bahrain is **absent** from the 2026
  calendar (`data/f1_data_2026.db` sessions table has no Bahrain round); 2026's
  Spain race is named `"Barcelona-Catalunya"` in the DB, while 2019-2025 all
  use `"Spain"`. The issue's literal "Bahrain and Spain are reliable anchors"
  does not hold as a flat constant across seasons — anchor circuits must be a
  **per-season map**, not a single hardcoded list.

## Decision Anchors & Decision Pressure
- Resolved this run (interrogation, `.agent-work/575-fuel-burn-calibration/interrogation.json`):
  1. Wire the calibration into `mass_model.race_mass`/`fuel_at_lap` now (not
     measured-not-wired) — accepted cost: already-stored `session_estimates`/
     `race_stint_estimates` artifacts go stale until re-batched (out of scope
     here, see below).
  2. Anchor circuits = an explicit per-season map (handles Bahrain's absence
     and the Barcelona-Catalunya rename), not a flat 2-item list.
  3. Compute 2026's own factor from its 7 available races (revised below —
     no longer a shrinkage-to-pooled-prior; see regulatory-anchor pivot).
- **Second revision (2026-07-01, plain-text, before execute.json finalized):**
  the primary calibration method changes from lap-time-slope regression to a
  **zero-fit throttle-integral estimator**: `burn_per_lap ≈
  flow_rate_cap_kg_per_s × mean(throttle_fraction over the lap) ×
  lap_duration_s`, where `flow_rate_cap_kg_per_s` is the literal regulated
  constant (100 kg/h flat 2014-2025; ~70 kg/h-equivalent from 2026 per the
  energy-based 3000 MJ/h limit) — not a fitted parameter. Verified feasible
  against the existing durable telemetry store schema: `tele_car.throttle`
  (0-100%) + `tele_laps.lap_start_time_s`/`lap_end_time_s` are present for
  race ('R') sessions on every circuit/season checked (e.g. 2023 Bahrain R).
  This needs no anchor-circuit selection (works on every lap, sidestepping
  the Bahrain-absent/Barcelona-Catalunya-rename problem for the PRIMARY
  estimate), is inherently per-season (each season uses its own telemetry +
  its own regulated constant, no pooling), and is robust to pace management
  (measures actual fuel burned via telemetry, not a lap-time-trend proxy that
  Monaco/Hungary-style pace management confounds). The original free-flow
  lap-time-slope regression (Bahrain/Spain anchor circuits) demotes from
  PRIMARY fitting mechanism to a G3 VALIDATION cross-check — proving the
  throttle-integral estimate and the independent lap-time-slope signal agree
  at genuinely free-flow circuits, rather than being the fitting method itself.
- **First revision (2026-07-01, plain-text, before execute.json authored):**
  two corrections to the original plan —
  1. **No cross-season pooling/shrinkage.** Each season's empirical
     free-flow-circuit ratio is computed **independently**; do not borrow
     strength across seasons (no DerSimonian-Laird/random-effects pooling of
     the burn-rate ratio, unlike `layer2/pooling.py`'s use for physics
     parameters that genuinely drift with car development). Fuel burn is
     regulation-bound, not a smoothly-drifting car parameter — pooling across
     a rule-change boundary (2026) would contaminate the estimate.
  2. **Anchor to the actual FIA regulation, not just data.** Verified via web
     search (see Governing Constraints below): fuel-flow rate was a flat
     **100 kg/h mass limit, unchanged 2014-2025**; max race-start fuel load
     was **105 kg (2014-2018) → 110 kg (2019-2025)**; **2026 changes both**:
     energy-based flow limit (3000 MJ/h ≈ 70 kg/h equivalent) and max race
     fuel **cut to 70 kg**. This explains WHY 2019-2024 pooling to a flat
     1.8 kg/lap was reasonable (regs were constant, so no season-to-season
     regulatory drift existed to pool over) and why 2026 is a genuine regime
     break, not a point on a smooth curve. Design: add an explicit,
     source-cited per-season regulation table (`MAX_FUEL_KG` becomes a
     season dict, next to `SEASON_BASE_KG`) and use the regulatory
     load ratio as the primary, cited anchor for the 2026 shift; the
     independent per-season empirical free-flow fit is the validation/
     cross-check signal, not a pooled-and-shrunk estimate.
- New decision surfaced for Cartographer reconciliation: the `mass_model.py`
  "pure arithmetic, nothing fitted" design intent now has an explicit external
  fitting module feeding it computed literals, anchored to cited FIA
  regulation values — worth a durable decision anchor
  (`decision:burn_rate_calibration_design`) so future changes don't silently
  re-fit inline or re-introduce cross-season pooling.

## Claims / Evidence Surfaces
- Physics model change → requires truth-anchored evidence per
  `ORCHESTRATOR_CONTEXT.md` Evidence Requirements table: L1/L2 test coverage
  on the new calibration fit + validation that free-flow circuits (Bahrain
  pre-2026, Spain/Barcelona-Catalunya) show corrected residual slope ≈ 0
  after calibration (extending the existing `mass_validation_dashboard.py`
  panel-C logic).
- `tests/unit/physics/test_mass_model.py` (50 tests) is the existing regression
  surface for `mass_model.py` — any signature change (`fuel_at_lap` gaining
  `burn_per_lap_kg`) must keep all 50 green plus new calibration tests.

## Map Confidence / Staleness / Disputes
- No architecture packet currently documents a burn-rate calibration module —
  this is genuinely new structure, not a stale-map risk.
- `scripts/mass_validation_dashboard.py`, `scripts/mass_fuel_dashboard.py`,
  `scripts/bahrain_frontier_validation.py` are UNCOMMITTED, untracked
  exploratory scripts already in the working tree (pre-existing, unrelated to
  this branch's origin) that overlap conceptually with this issue's
  validation goal. Treat them as prior scratch exploration to draw on for the
  regression/plotting approach, not as authoritative or as this run's own
  deliverable — they belong to a different in-progress thread and are left
  untouched unless the human says otherwise.

## Out of Scope
- Per-circuit burn rate variation (already modelled via lap length).
- Replacing `SC_BURN_FRACTION` — this run only CHECKS whether the
  throttle-integral method naturally reproduces a sane SC/VSC-vs-green ratio;
  it does not change the existing hardcoded 0.5 fraction.
- Pace-management circuit flagging (companion issue under #509).
- **Wiring into `mass_model.race_mass`/`fuel_at_lap` — deferred per the
  third-revision steer above.** This run stops at validation evidence; wiring
  (the original G2/G3) is a follow-up once the human reviews the evidence.
- Re-running `physics_estimates.db`/`race_stint_estimates.db` batch
  populations — moot until wiring happens, and deferred regardless.
