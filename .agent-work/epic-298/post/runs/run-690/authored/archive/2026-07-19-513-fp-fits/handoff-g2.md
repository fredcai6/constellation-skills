# Implementer Handoff — G2

## Gate
`g2` (execute.json)

## Task
Add FP-session mass support to the physics estimator, as TWO deliverables:
1. `src/physics/mass_model.py`: new `fp_mass(...)` returning a MASS DISTRIBUTION (value + σ), not a scalar.
2. New `src/physics/layer2/fp_lap_latent.py`: per-lap latent-state extractor for an FP session
   (fuel mass estimate, compound [OBSERVED], tyre_life, run_purpose), yielding per-lap mass.

## Protected Intent
FP fits must stop silently assuming quali mass. The dominant FP fuel unknown — the per-run STARTING
fuel (intercept) — is UNOBSERVABLE; it MUST be carried as uncertainty (σ), NEVER as a confident point
value. This is the owner's explicit-unknown discipline: unmeasurable → wide σ, never bias.

## Test Mode
TDD required (pure arithmetic + deterministic classification; highly testable).

## Close Criteria
- `fp_mass(season, *, fuel_kg=None, fuel_sigma_kg=None, team=None) -> FpMass` where `FpMass` is a
  NamedTuple/frozen dataclass `(mass_kg: float, sigma_kg: float)`. `mass_kg = SEASON_BASE_KG[season] +
  fuel_kg + team_offset`; `sigma_kg` reflects the fuel uncertainty. When `fuel_kg is None`, use
  `NOMINAL_FP_FUEL_KG` with `FP_FUEL_INTERCEPT_SIGMA_KG` (the wide honest-unknown default).
- Invariant: `SEASON_BASE_KG[season] < fp_mass(...).mass_kg < quali_mass(season) + MAX_FUEL_KG` for a
  full-fuel FP lap; a low-fuel (push) fp_mass is below a long-run fp_mass.
- `fp_lap_latent.py`: `extract_fp_lap_latent(year, gp, session_type, *, db_path, driver=None) ->
  list[FpLapLatent]` (or per-driver dict). Each `FpLapLatent` carries:
  `(driver, lap_number, stint_id, lap_in_stint, compound, tyre_life, run_purpose, fuel_kg_est,
  fuel_sigma_kg, mass_kg, mass_sigma_kg, valid_lap, track_status)`.
- Per-lap fuel model (define as NAMED module constants — a decision-candidate, flag it as tunable):
  `fuel_kg_est(lap) = start_fuel(run) - burn_per_lap * (lap_in_stint - 1)`, floored at a reserve.
  `burn_per_lap` from `mass_model.DEFAULT_BURN_PER_LAP_KG` (reuse). `start_fuel(run)` inferred from
  `run_purpose`: push/quali-sim → `START_FUEL_PUSH_KG`; long-run → `START_FUEL_LONGRUN_KG`;
  ambiguous → mid with the WIDE `FP_FUEL_INTERCEPT_SIGMA_KG`. The intercept σ dominates `fuel_sigma_kg`.
- `run_purpose` EMERGENT from lap pattern, NEVER a session label: classify each lap into
  {out, push, in, long_run} from `lap_time` vs the driver's session-best (push = within a small margin
  of best; out/in = pit-adjacent via `pit_out_time`/`pit_in_time` or first/last stint lap) and stint
  position. Provide `classify_run_purpose(...)` as a pure, unit-tested function.
- Compound is OBSERVED — read it directly from `lap_times.compound`, never infer it.

## Allowed Scope
- `src/physics/mass_model.py` (add `fp_mass` + FpMass + FP fuel constants; do NOT change `quali_mass`/
  `race_mass`/existing behavior).
- New `src/physics/layer2/fp_lap_latent.py`.
- New tests `tests/unit/physics/test_mass_model.py` (extend if exists) + new
  `tests/unit/physics/test_fp_lap_latent.py`.
- May add a tiny synthetic fixture DB in tests (in-memory sqlite or tmp_path) — do NOT read real
  `data/*.db` in unit tests.

## Specific Exclusions
- Do NOT touch `session_estimator.py` (that is G5), `estimate_store.py` (G3), or any view.
- Do NOT commit or read/modify any `data/*.db` in tests (#632). Use tmp/in-memory sqlite fixtures.
- Do NOT wire fp_mass into any fitter yet.

## Constraints
- physics-region: NO imports from `evo_predictor`/`latent_power`/`compound_prior`/`fastf1`.
- The season-DB read follows the ALLOWED `physics → data` direction. Reuse the exact `lap_times` read
  pattern from `src/physics/layer2/session_race.py` (`_get_session_id`, `_load_driver_laps` — reads
  `lap_number, compound, tyre_life, stint_id, track_status, lap_time` joined via `sessions`) — mirror
  or import that read; open the DB read-only.
- All tunable constants named at module scope with a docstring flagging them as calibration
  placeholders / decision-candidates (no hidden inline tuning).
- No fit output feeds `fp_mass`/fuel (non-circular).

## Map Anchors (inbound)
- Structural: `struct:physics` — `mass_model.py`; `struct:physics.layer2` — new `fp_lap_latent.py`.
- Capability: `purpose:physics_estimation` — FP mass replaces quali_mass fuel bias.
- Constraints: `constraint:physics_region_no_evo_import`; assumption: FP starting fuel is UNOBSERVABLE.
- Decision anchor: mirrors `mass_model.quali_mass`/`race_mass` conventions (mass in kg, team offset).

## Deliverable Path Check
- Committed — `src/physics/mass_model.py`, `src/physics/layer2/fp_lap_latent.py`,
  `tests/unit/physics/test_mass_model.py`, `tests/unit/physics/test_fp_lap_latent.py`. Not gitignored
  (src/ + tests/ are tracked). New files appear in `git status`, not `git diff` until staged.

## Required Evidence
- `py -m pytest tests/unit/physics/test_mass_model.py tests/unit/physics/test_fp_lap_latent.py -q` green
  (paste the summary line).
- A short value table: fp_mass for a push lap vs a long-run lap (2023), showing mass ordering + σ.
- `py -m src.utils.simplification_limits` on the two touched/new src paths (strict) if it applies.

## Verification Commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/test_mass_model.py tests/unit/physics/test_fp_lap_latent.py -q
```

## Suggested Model Tier
`simple bounded` — clear arithmetic + deterministic classification, seams cited.

## Authority
The fuel-model FORM (start_fuel-by-run_purpose − burn·lap_in_stint, intercept-σ-dominant) and the
distribution-return contract are DECIDED (Ship I, per GATE_PROTOCOL.md F2). You choose the concrete
placeholder constant values (reasonable F1 figures) but must name them + flag tunable. Do not change
the return-a-distribution contract or infer compound.

## Stop Conditions
Stop and return if allowed scope must be exceeded, a data/*.db must be read in a test, or the
distribution contract cannot be met.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced,
assumptions used, stop conditions hit, out-of-scope observations, workflow feedback.
