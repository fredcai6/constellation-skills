# Reviewer Handoff — G1 Common Scoreboard Harness

## Gate
g1-review (work-id 496-physics-aware-estimator, branch `feat/physics-aware-estimator-496`, MAIN checkout)

## What Was Implemented
A common scoreboard harness so five later spikes are measured head-to-head:
- NEW `src/physics/layer2/scoreboard.py` — pure metric core (`braking_knee`,
  `non_throttle_ringing`, `VariantScore`, `score_variant`), an injected-variant seam
  (`VariantFn`, `CaseInputs`, `run_case`, `run_scoreboard`, `ScoreboardTable`), and two
  built-in baseline variants (`"gaussian"`, `"kind3"`).
- NEW `tests/unit/physics/layer2/test_scoreboard.py` — 25 synthetic-array unit tests.
- REFACTOR `scripts/validate_refine_505.py` — removed inline `_knee_and_ringing`; all
  knee/ringing now route through `score_variant`; writes `reports/physics/scoreboard_baseline_2023Q.json`.

## How to Inspect the Diff
```bash
cd C:/Programs/f1Brainz
git status --short
git diff -- scripts/validate_refine_505.py
# new files (untracked):
cat src/physics/layer2/scoreboard.py
cat tests/unit/physics/layer2/test_scoreboard.py
cat reports/physics/scoreboard_baseline_2023Q.json
```
Full IMPLEMENTER_RESULT: `.agent-work/496-physics-aware-estimator/crew-handoffs/g1-implement-result.md`.

## Task Statement
Build the trust-anchor scoreboard (pure, unit-tested metric core + injected-variant seam)
that measures EXISTING gaussian + kind3 trajectory variants identically per lap, and record a
current-smoother baseline reproducing the #505 numbers within tolerance. No new estimation
mechanism. (Full task: `.agent-work/496-physics-aware-estimator/crew-handoffs/g1-implement.md`.)

## Close Criteria (each a review check)
- Metric core is **pure + deterministic**: `braking_knee = min(a_long[brake])`,
  `non_throttle_ringing = max(a_long[non_throttle])`; signs/units correct (decel negative,
  knee is the min, ringing is the max-positive); NaN handling for empty masks.
- Per-lap **masks + raw reference are held FIXED across variants** — only the variant's
  `a_long` changes (the comparability guarantee). Confirm `raw_a_long` comes from
  `clean_longitudinal_from_raw` and is not re-derived per variant.
- The **injected-variant seam** genuinely lets an arbitrary estimator be scored without
  editing the core (a `VariantFn` callable consumed by `run_case`/`run_scoreboard`).
- Baseline JSON **reproduces #505** within ~0.5 m/s² (claimed <0.01) for gaussian + kind3
  on Belgium/Monaco/Bahrain 2023 Q VER.
- Unit tests green; no layer2 regressions; `simplification_limits` clean on the NEW files.
- `constraint:physics_region_no_evo_import` honored (no evo/latent_power/compound_prior import).

## Allowed Scope
NEW `scoreboard.py` + its test; REFACTOR `validate_refine_505.py`; GENERATE the baseline JSON.

## Specific Exclusions (flag if touched)
No new estimation mechanism; no modification to `smoother.py`, `accel_obs.py`,
`trajectory_refine.py`, `braking_view.py`, `calibration.py`, `session_fit.py`; raw reference
definition unchanged.

## Constraints the Implementation Must Respect (each a check)
- `py` launcher; `decision:two_cycle_external_anchor_design` (raw `a_long` un-biased reference);
  `decision:smoother_rounds_braking_knee`; no evo import; explicit units/signs.

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `src/physics/layer2/scoreboard.py`.
- **Capability:** trajectory-estimation eval (comparable scoreboard for spikes).
- **Constraints/decisions:** `constraint:physics_region_no_evo_import`,
  `decision:two_cycle_external_anchor_design`, `decision:smoother_rounds_braking_knee`.
- **Evidence:** reproduces #505 baseline within tolerance.

## Evidence Produced (verify, don't just trust)
- `py -m pytest tests/unit/physics/layer2/test_scoreboard.py -q` → 25 passed.
- `py -m pytest tests/unit/physics/layer2/ -q` → 126 passed (no regressions).
- `py scripts/validate_refine_505.py` → baseline table reproducing #505 (<0.01 m/s²).
- `py -m src.utils.simplification_limits --paths src/physics/layer2/scoreboard.py tests/unit/physics/layer2/test_scoreboard.py` → PASS.
- **Re-run the pytest yourself** to confirm; spot-check one metric by hand against the JSON.

## Known out-of-scope items the implementer flagged (assess, do not require fixes)
1. `validate_refine_505.py` loads each session twice when `run_scoreboard` runs (acceptable
   for a script; a future `run_case(session=...)` seam would remove it).
2. Pre-existing `simplification_limits` violations in `validate_refine_505.py` `main()`
   (CC 43→44, fn_lines 196→213) + `_run_one_circuit` — predate G1; G1 nudged them slightly.
   This is #504-style cleanup territory, not a G1 blocker.
3. Pre-existing unused imports (`driver_num`/`driver_streams`/`stint_span`) in that script.
These three are triage candidates, NOT block reasons — confirm they are genuinely pre-existing
/ cosmetic and not correctness issues.

## Suggested Model Tier
simple-bounded (Sonnet) — bounded review of a pure module + a refactor with verified evidence.

## Stop Conditions
BLOCK if: the metric core is impure/non-deterministic or sign/unit-wrong; masks or the raw
reference vary per variant (breaks comparability); the seam can't actually accept an arbitrary
variant; the baseline does NOT reproduce #505; tests fail; or an evo import exists.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/496-physics-aware-estimator/crew-handoffs/g1-review-result.md`):
verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations, and
Workflow Feedback. State the verdict literally as `verdict: APPROVE` or `verdict: BLOCK`.
