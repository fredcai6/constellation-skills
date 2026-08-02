# Reviewer Handoff

## Gate
g1 — Calibrate the decoupled longitudinal estimator HPs across the full 2023-Q season (review).

## What Was Implemented
A calibration harness for the decoupled-longitudinal estimator: a `make_synthesis_variant(**hp)`
factory (additive) on `decoupled_longitudinal.py`, a new `decoupled_calibration.py` harness, a
season-sweep CLI (`scripts/calibrate_decoupled_hp_2023Q.py`), a true-regime validation script
(`scripts/_validate_true_regime.py`), and 32 unit tests. The full-season raw-regime sweep
(220/220 cases) tripped a stop condition (ringing_ok 7.7%), which a true-regime validation
(12 cases via the production `run_case()` path) then resolved as a raw-regime artifact —
confirming the EXISTING DEFAULT HPs (tv_lambda=0.10, sig_a_soft_brake=0.10) as the season-validated
calibration (no `_DEFAULT_*` change). Reports written; `_DEFAULT_*` constants unchanged.

## How to Inspect the Diff
```bash
cd /c/Programs/f1Brainz
git status --short
git diff -- src/physics/layer2/decoupled_longitudinal.py
git diff --stat
# new files:
#   src/physics/layer2/decoupled_calibration.py
#   scripts/calibrate_decoupled_hp_2023Q.py
#   scripts/_validate_true_regime.py
#   tests/unit/physics/layer2/test_decoupled_calibration.py
# reports (gitignored): reports/physics/decoupled_hp_calibration_2023Q.{json,md}, true_regime_validation_2023Q.json
```
Full implementer result: `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g1-implement-result.md`.
Report: `reports/physics/decoupled_hp_calibration_2023Q.md` (incl. the True-Regime Validation section).

## Task Statement
Build a reproducible calibration harness, evaluate the estimator HPs across the full 2023-Q season
using the scoreboard metrics, and decide + persist a calibrated HP set with season-wide
generalization evidence (no hidden inline tuning; report where it does NOT improve).

## Close Criteria
- The HP decision is justified by the **true production-regime** validation (`run_case`/
  `_build_case_inputs`, smoother-based regime), NOT only the confounded fast raw-regime sweep.
- The chosen HP set is persisted in named constants/config — here DEFAULT is confirmed-as-calibrated
  (the `_DEFAULT_*` constants already hold the validated values); confirm this is honest, not a dodge.
- DEFAULT-wins reasoning is sound: same ringing_ok (11/12) as the candidate but a tighter knee
  (+0.70 vs +2.60 m/s² gap) — verify against `true_regime_validation_2023Q.json`.
- Honest reporting: the raw-regime artifact, the Mexico/PER failure (3.95 ringing, both HPs), and
  the gaussian/kind3 baselines (1/12) are all reported, not buried.
- `py -m pytest tests/unit/physics/layer2/ -q` green (184) and `py -m src.utils.simplification_limits`
  clean on touched paths — re-run to confirm.
- No production wiring; no scoreboard-metric/built-in-variant change; no evo-region import.

## Allowed Scope
`src/physics/layer2/decoupled_longitudinal.py` (additive factory only), new
`decoupled_calibration.py` + the two scripts + the test file, `reports/physics/` (gitignored).

## Specific Exclusions (flag if touched)
- `braking_view.clean_longitudinal_from_raw`, scoreboard metric core (`braking_knee`,
  `non_throttle_ringing`, `score_variant`), built-in variants — must be UNCHANGED.
- `EstimateStore`, `car_prior`, utilization layer, any production view (session_braking/traction/coast)
  — must be UNTOUCHED.
- `_DEFAULT_*` constants — must be unchanged (DEFAULT was confirmed, not re-tuned).

## Constraints the Implementation Must Respect
- `py` not `python`; tunable HPs in named constants (no hidden inline tuning).
- `constraint:physics_region_no_evo_import` — verify no `src.evo_predictor/latent_power/compound_prior` imports.
- `decision:two_cycle_external_anchor_design` — the anchor is the TV-denoised RAW `a_long`, never
  re-read from a smoothed trajectory (check the fast extractor + the variant factory honor this).
- Honest covariance preserved.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `decoupled_longitudinal.py`, `decoupled_calibration.py`, `scoreboard.py` (read-only).
- **Capability:** physics capability-frontier measurement — the estimator HP noise model.
- **Constraints:** `constraint:physics_region_no_evo_import`; `decision:two_cycle_external_anchor_design`.
- **Decision anchors:** `decision:decoupled_1d_longitudinal` — the HP calibration basis is recorded here; confirm the Known-Limits "VER/3-circuit" flag is now genuinely resolved by season evidence.
- **Evidence:** scoreboard `braking_knee` + `non_throttle_ringing` pass-rate on the true regime.
- **Map confidence:** the HP-defaults VER/3-circuit flag — confirm the resolution is evidence-backed, not asserted.

## Evidence Produced
- `py -m pytest tests/unit/physics/layer2/ -q` → 184 passed.
- `py -m src.utils.simplification_limits` → PASS (2 files).
- True-regime validation: default 11/12 (91.7%) ringing_ok, +0.70 knee gap; candidate 11/12, +2.60;
  gaussian/kind3 1/12. Mexico/PER fails on both.

## Suggested Model Tier
Stronger — the review hinges on judging whether the true-regime validation soundly resolves the
raw-regime confound and whether DEFAULT-confirmation is honest; that is a judgment call, not a checklist.

## Stop Conditions
BLOCK if: the diff cannot be accessed; the true-regime validation does not actually use the
production `run_case` regime; the DEFAULT-confirmation is not evidence-backed; a `_DEFAULT_*` change
slipped in unvalidated; an exclusion was touched; or tests/simplification do not reproduce.

## Return Format
Return REVIEW_RESULT to `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g1-review-result.md`:
verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, and Workflow
Feedback. Set a clear `verdict: APPROVE` or `verdict: BLOCK` line.
