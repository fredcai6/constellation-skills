# Reviewer Handoff

## Gate
`g4` — Layer 3 (field-car: relative + re-anchor) + Layer 4 (car signal) + `model.py` assembler, each with σ, leak-free on held-out.

## Survey State Location
`.agent-work/wave4-626/g4-review/review.json`.

## What Was Implemented
`layer3_fieldcar.py` (two-stage: relative = `floor.weekend_relative` + σ folding field-median SE; re-anchor via `pooling.fit_drift`/`DriftFit.predict` on per-weekend field medians; `absolute = fieldcar_traj + relative`), `layer4_car.py` (car signal = `pool_random_effects` EB-shrunk relative deltas; `fit_car_pools` on TRAIN, row-wise apply), `model.py` (`WeekendStateModel` L1→L2→L3→L4, explicit `fit(train)`→`car_signal(held-out)`, per-layer σ). 22 tests. Result: `.agent-work/wave4-626/g4-implementer-result.md`.

## How to Inspect the Diff
UNCOMMITTED tree; `git status --porcelain` then read the three `src/physics/weekend_state/{layer3_fieldcar,layer4_car,model}.py` + two tests directly.

## Task Statement
Build Layers 3+4 + assembler, each with σ, leak-free. Full task: `.agent-work/wave4-626/g4-implementer-handoff.md`.

## Close Criteria (each a review check)
- Two-stage decomposition correct: relative + re-anchored absolute both carry σ; reconstruction `field_car_traj + relative == absolute` holds (re-run the test; spot-check the algebra).
- **NO LEAKAGE (load-bearing):** READ `model.py`'s `fit(train)`→`predict/car_signal` path and confirm the held-out weekend's car-signal is driven by TRAIN-only hyperparameters (field-car drift step_var + per-car τ fit on train weekends only). Confirm the test that proves the held-out car-signal is identical whether or not the weekend is in the predict population is a REAL test (not trivially true). A leak here fakes the whole F6 result — this is the check that matters most.
- `pool_random_effects` + `fit_drift` are IMPORTED from `src/physics/layer2/pooling.py` (not copied) — confirm via grep + the identity-assertion test.
- `model.py` assembles all four layers each carrying its own σ (`layer_sigma_cols()`); Layer 2 kept as an inert wide-σ seam (not dropped).
- Model output `{axis}_car_signal` feeds g1 `gate_spec.signal_preservation_guard`/`evaluate_axis` (confirm the shape matches what gate_spec expects).
- No evo import; no `data/*.db` staged.

## Allowed Scope
`src/physics/weekend_state/{layer3_fieldcar,layer4_car,model}.py`, the two tests.

## Specific Exclusions
No g5 gate/writeup; g1/g2/g3/pooling.py/estimator/evo/config untouched.

## Constraints the Implementation Must Respect
Reuse pooling.py; no-leakage train-only hyperparameters; per-layer σ; `constraint:physics_region_no_evo_import`; absolute DB paths; no data/*.db commit.

## Map Anchors (inbound)
- Structural: `layer3_fieldcar/layer4_car/model.py` (NEW); `src/physics/layer2/pooling.py` (REUSE).
- Capability: field-car common-mode + car signal, each with σ.
- Constraints: no-leakage; no evo import.
- Decision: cake-and-eat-it two-stage; car-signal is the F6-measured quantity.

## Evidence Produced
`py -m pytest tests/unit/physics/weekend_state/test_layer3_fieldcar.py tests/unit/physics/weekend_state/test_model.py -q` → 22 passed (commander re-ran: 22 passed). No-leakage demo + real-frame smoke (0 mismatches/80 keys) in the implementer result.

## Suggested Model Tier
Stronger — the no-leakage discipline is the whole gate's integrity; scrutinize the fit/predict split hard.

## Stop Conditions
BLOCK if: the held-out path leaks (held-out data enters its own prediction's fit), pooling.py is copied/reinvented rather than imported, the two-stage reconstruction is wrong, a layer's σ is missing, or an evo import / data/*.db staged.

## Return Format
Return REVIEW_RESULT to `.agent-work/wave4-626/g4-reviewer-result.md`: verdict (APPROVE/BLOCK), per-check findings, blockers, out-of-scope observations, workflow feedback.
