# Reviewer Handoff

## Gate
`g1` (work-id `575-fuel-burn-calibration`, issue #575)

## Survey State Location
Create your review survey checklist at
`.agent-work/575-fuel-burn-calibration/g1-review/review.json`.

## What Was Implemented
A new, standalone, zero-fit physics module
(`src/physics/burn_rate_calibration.py`) that estimates per-(season, circuit)
F1 fuel burn rate directly from telemetry: `lap_burn_kg =
flow_rate_cap_kg_per_s * mean_throttle_fraction * lap_duration_s`, where the
flow-rate cap is a literal, cited FIA regulation constant (100 kg/h flat
2014-2025; ~70 kg/h-equivalent from 2026), NOT a fitted parameter. Also: a
validation script (`scripts/validate_burn_rate_hypothesis.py`) that cross-
checks this estimate against an independent lap-time-slope OLS method at
Bahrain/Spain(-or-Barcelona-Catalunya)/Silverstone/Monaco across 2019-2026,
and reports an SC/VSC-vs-green burn ratio against the existing hardcoded
`mass_model.SC_BURN_FRACTION=0.5`. This gate is deliberately validation-only
— `mass_model.py` was NOT modified, nothing was wired.

## How to Inspect the Diff
```
git status --porcelain
git diff --stat HEAD
```
Branch: `feat/575-fuel-burn-calibration` off `main`. Only these three files
should be new/changed: `src/physics/burn_rate_calibration.py`,
`scripts/validate_burn_rate_hypothesis.py`,
`tests/unit/physics/test_burn_rate_calibration.py`. `src/physics/mass_model.py`
must show NO diff. The repo also has several PRE-EXISTING untracked scratch
scripts unrelated to this work (`mass_validation_dashboard.py`,
`mass_fuel_dashboard.py`, `bahrain_frontier_validation.py`,
`build_lateral_load_cache.py`, `lateral_load_unitization.py`,
`tyre_age_overview.py`, `tyre_degradation_validation.py`) — these should
remain untracked/untouched; do not flag their mere presence as a problem, but
DO flag it if any of them were modified.

## Task Statement
Build and validate (not wire) a zero-fit, per-season/per-circuit fuel
burn-rate estimator anchored to the FIA's literal fuel-flow regulation,
cross-checked against an independent lap-time-slope method across a WIDER
circuit range than just the original two "free-flow" anchors (human steer:
include Silverstone as a moderate case and Monaco as an adversarial
pace-managed case), plus report — informationally only — how the throttle-
integral method's SC/VSC-vs-green ratio compares to the existing hardcoded
`SC_BURN_FRACTION=0.5`. Full task detail:
`.agent-work/575-fuel-burn-calibration/crew-handoffs/g1-implementer-handoff.md`.

## Close Criteria
- `src/physics/burn_rate_calibration.py` exists with: a cited per-season FIA
  regulation table (verify the cited figures are accurate: 100 kg/h /
  110 kg for 2019-2025, ~70 kg/h / 70 kg for 2026 — cross-check against the
  citations in `.agent-work/575-fuel-burn-calibration/MISSION_FRAME.md`); a
  pure per-lap burn formula with direct hand-computed-value unit tests; a
  per-(season, circuit) aggregator with NO cross-season or cross-circuit
  pooling inside it; a lap-time-slope cross-check function.
- `scripts/validate_burn_rate_hypothesis.py` runs and produces real
  per-(season, circuit) numbers for: the throttle-integral estimate, the
  lap-time-slope cross-check (observed vs model slope vs %error), and the
  SC/VSC-vs-green ratio — for seasons 2019-2026 across Bahrain, Spain
  (2026: Barcelona-Catalunya), Silverstone, Monaco.
- The result HONESTLY reports whatever the numbers show — verify the
  IMPLEMENTER_RESULT's claimed finding (large ~80% mean error even at
  free-flow circuits, with Monaco much worse at ~365%) is actually reproduced
  by re-running the script yourself, not just quoted from the result file.
- `tests/unit/physics/test_burn_rate_calibration.py` passes (38 tests claimed).
- `py -m src.utils.simplification_limits --paths <touched files>` passes.
- `mass_model.py` has zero diff; no pre-existing untracked scratch script was
  touched; `SC_BURN_FRACTION` is unchanged.

## Allowed Scope
Same as the implementer handoff: new files only
(`src/physics/burn_rate_calibration.py`,
`scripts/validate_burn_rate_hypothesis.py`,
`tests/unit/physics/test_burn_rate_calibration.py`); everything else
read-only.

## Specific Exclusions
`src/physics/mass_model.py` must be untouched. The pre-existing untracked
scratch scripts must be untouched. No re-run of any batch population script.

## Constraints the Implementation Must Respect
- Zero-fit: the flow-rate cap must be a literal constant, not derived via
  regression anywhere in the estimator.
- No cross-season/cross-circuit pooling anywhere (throttle-integral estimate
  AND lap-time-slope cross-check both stay per-(season, circuit)).
- Reuses the existing `TelemetryStore`/`build_db_session` seam — verify it
  does not implement a parallel/duplicate telemetry loader.
- DB/telemetry-store-only data access — no direct FastF1 calls (`grep -rn
  "import fastf1" src/physics/burn_rate_calibration.py
  scripts/validate_burn_rate_hypothesis.py` should be empty).

## Map Anchors (inbound)
- **Structural:** `struct:physics` — new module
  `src/physics/burn_rate_calibration.py`; `mass_model.py` read-only
  reference (verify unchanged). `struct:data` —
  `src/data/telemetry_store.py`/`src/data/telemetry_session.py`, read-only
  reuse (verify no modification).
- **Capability:** new standalone capability (regulation-anchored zero-fit
  burn-rate estimate + cross-check + SC/VSC diagnostic); explicitly NOT wired
  into the production `race_mass`/`fuel_at_lap` path — verify this claim by
  checking `mass_model.py`'s diff is empty and nothing else in `src/`
  imports the new module.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import` —
  verify no evo/latent_power/compound_prior import in the new files.
- **Decision anchors:** `decision:burn_rate_calibration_design` (regulation-
  anchored, zero-fit, per-season/circuit independent, no pooling, wiring
  deferred) — verify the implementation matches this design, not something
  else.
- **Evidence expectations:** real per-(season, circuit) numbers for both the
  cross-check and the SC/VSC ratio — flag if any claim in the result is
  asserted without a corresponding number in the script's actual output.
- **Map confidence flags:** none.

## Evidence Produced
See `.agent-work/575-fuel-burn-calibration/crew-handoffs/g1-implementer-result.md`
for the full IMPLEMENTER_RESULT, including:
- `py -m pytest tests/unit/physics/test_burn_rate_calibration.py -q` → claimed `38 passed`.
- `py scripts/validate_burn_rate_hypothesis.py` → claimed full per-(season,circuit) tables (throttle-integral kg/lap; lap-time-slope cross-check with %error; SC/VSC ratio).
- `py -m src.utils.simplification_limits --paths <files>` → claimed `PASS`.
Re-run all three yourself; do not take the pasted numbers on faith.

## Suggested Model Tier
Stronger — reason: this gate's entire value is an honest empirical finding
(the hypothesis is only partially validated); the reviewer must independently
re-derive/re-run the evidence, not rubber-stamp a plausible-looking table.

## Stop Conditions
Stop and return BLOCK if: the diff touches anything outside allowed scope
(especially `mass_model.py` or the pre-existing scratch scripts); any of the
three verification commands fail on re-run; the claimed evidence numbers
don't reproduce; the estimator is not actually zero-fit (contains a hidden
regression/fitted constant) or pools across seasons/circuits somewhere.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings,
blockers, out-of-scope observations, workflow feedback.
