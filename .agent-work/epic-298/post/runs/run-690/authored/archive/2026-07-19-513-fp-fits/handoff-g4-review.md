# Reviewer Handoff — G4 (representativeness weighting)

## What was implemented
New `src/physics/layer2/fp_representativeness.py` (348 lines): `ObservationFeatures` (fuel_proximity,
compound_softness, run_purpose_score, track_evolution_score), `WeightParams` (named coefficients,
`DEFAULT_WEIGHT_PARAMS`), `observation_weight(...) -> w in [0,1]` (transparent logistic). Result:
`.agent-work/513-fp-fits/result-g4-implement.md`.

## How to inspect
`git diff -- src/physics/layer2/fp_representativeness.py` (new) + tests
`tests/unit/physics/layer2/test_fp_representativeness.py`. Task spec: `.agent-work/513-fp-fits/handoff-g4.md`.

## Close criteria to verify (reproduce, don't trust)
- LOAD-BEARING EMERGENCE (critic F3/F4) — verify these tests exist AND genuinely test the property:
  - `test_lap3_low_fuel_soft_push_beats_lap18_high_fuel_hard_long_run_same_session` (within-session, SAME
    track_evolution — proves discrimination isn't riding the track-evolution term).
  - `test_within_session_gap_survives_even_if_track_evolution_term_zeroed` (orthogonality).
  - `test_fp2_like_push_beats_fp3_like_long_run` (cross-session: push at low track_evo beats long-run at
    high track_evo — a track-evolution-ONLY weighting would get this backwards; confirm the test asserts
    the non-trivial direction).
- `test_no_session_type_string_in_module_source` — the module contains NO session-type string. Independently
  grep the module for `FP1|FP2|FP3|session_type|"Q"` and confirm empty.
- `w in [0,1]` for all inputs; NOTHING binary-dropped (thin/unrepresentative → LOW weight, never None/excluded).
- Leakage (F6): track_evolution feature consumes NO qualifying-session input (verify by reading the feature).
- Weighting form is TRANSPARENT (inspectable), coefficients named + DEFAULTS flagged tunable; NOT fit on
  real data here (that is G6).

## Constraints to verify
- physics-region: no evo/latent_power/compound_prior/fastf1 imports.
- No `data/*.db` read in tests (synthetic FpLapLatent only); `git status --short data/` clean.
- `py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/fp_representativeness.py tests/unit/physics/layer2/test_fp_representativeness.py` PASS.

## Evidence produced
`py -m pytest tests/unit/physics/layer2/test_fp_representativeness.py -q` → 35 passed (reproduce).

## Verification commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_fp_representativeness.py -q && grep -nE "FP1|FP2|FP3|session_type" src/physics/layer2/fp_representativeness.py; git status --short data/
```

## Return format
REVIEW_RESULT: verdict APPROVE or BLOCK + findings (severity, defect, location). BLOCK on: any session-type
string in the module, a weighting that collapses to a monotone function of session-mean track_evolution
(calendar-in-disguise — the emergence tests must genuinely prevent this), any binary-drop of observations,
any Q-session leakage into features, or any real-data fit. Write REVIEW_RESULT to
`.agent-work/513-fp-fits/result-g4-review.md` AND SendMessage to "ShipI-513".
