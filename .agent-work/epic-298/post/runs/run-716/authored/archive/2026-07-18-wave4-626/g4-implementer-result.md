# Implementation Result — g4

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g4` — Layer 3 (field-car common-mode: relative + smooth re-anchor) + Layer 4 (car signal) + `model.py` (four-layer assembler), each carrying honest σ, leak-free on held-out.

## Completed slice
All three source files + two test files built and green. The four-layer decomposition (L1→L2→L3→L4) composes into a per-car-weekend×axis state with an explicit `fit(train)`→`transform/car_signal(held-out)` split that is provably leak-free. The `{axis}_car_signal` column feeds g1 `gate_spec` directly.

## Scope
**Files changed (all NEW, untracked):**
- `src/physics/weekend_state/layer3_fieldcar.py` — two-stage field-car decomposition (relative + smooth re-anchored absolute).
- `src/physics/weekend_state/layer4_car.py` — shrunk car signal (`pool_random_effects` EB deltas off the field car).
- `src/physics/weekend_state/model.py` — `WeekendStateModel`, the L1→L2→L3→L4 assembler.
- `tests/unit/physics/weekend_state/test_layer3_fieldcar.py` — 9 tests.
- `tests/unit/physics/weekend_state/test_model.py` — 13 tests (layer4 + model).
- `.agent-work/wave4-626/g4-implementer-plan.json` + this result (workflow artifacts).

**Specific exclusions touched:** no. Did NOT touch g1/g2/g3 files, `pooling.py`, estimator, evo, config, or any `data/*.db`.

## Behavior changed
Yes — adds the Layer-3/Layer-4 model and the four-layer assembler. New capability; no existing behavior altered.

## Design realized (matches frozen authority)
- **L3 (a) RELATIVE** = car residual − weekend field median, reusing `floor.weekend_relative` verbatim (test asserts equality). σ = quadrature of car axis σ and the field-**median** SE (`sqrt(pi/2)·field_sd/√n`).
- **L3 (b) RE-ANCHOR** = smooth field-car ABSOLUTE trajectory per year, fit with `pooling.fit_drift` over `round_idx` on the per-weekend field-median series; `DriftFit.predict` gives the smooth level+σ. `absolute = fieldcar_traj + relative` (reconstruction identity is a test).
- **L4 car signal** = `pool_random_effects` EB-shrunk per-weekend relative deltas; `fit_car_pools` learns per-car-season (μ, τ, σ_μ) on TRAIN; `car_signal_for_row` applies the SAME shrink algebra (`shrink=τ²/(τ²+σ²)`, `signal=μ+shrink·(y−μ)`) row-wise.
- **L2** kept in the pipeline as a documented near-no-op (g3 FLOAT): grip-`g` latent is unmapped to the 11 axis units and the frame has no per-car `cumulative_track_laps` bridge, so `{axis}_l2_delta=0`, residual passes through. Not dropped.

## Test mode
**Required:** test-after (handoff Test Mode).
**Satisfied:** yes — load-bearing tests written and green: reconstruction identity, pooling.py import assertions, faithful `shrunk` reproduction, no-leakage (two framings), gate_spec feed.

## Evidence
```bash
cd C:/Programs/f1-626
py -m pytest tests/unit/physics/weekend_state/test_layer3_fieldcar.py tests/unit/physics/weekend_state/test_model.py -q
```
**Result:** pass — `22 passed in 2.81s` (9 layer3 + 13 model).

### No-leakage demonstration
- **Test `test_model_heldout_car_signal_has_no_leakage`**: fit on train; transform (A) only the target held-out round vs (B) the entire held-out set; every `(car-season, round=3)` car-signal is bit-identical across A and B. Adding/removing OTHER held-out weekends of that car-season changes nothing.
- **Test `test_model_heldout_signal_independent_of_train_membership_of_holdout`**: predicting a single held-out car-weekend in isolation equals predicting it inside the full held-out frame (the predict path never re-pools).
- **Real-data smoke** (`physics_estimates.db`, 1562 rows, train=1061/hold=501): no-leakage check on round 6 → 80 keys, **0 mismatches**; car_signal defined on 486/501 held-out rows.
- Mechanism: `fit(train)` learns all hyperparameters train-only (L1 density betas, L3 field-car `DriftFit` step_var, L4 pool μ/τ). L1 is applied **per-year** so `mass_kg_assumed` (year-constant) makes the mass term inert and the residual row-local; L3 re-anchor reads the stored train trajectory; L4 shrink is per-row against the stored train pool.

### pooling.py-reuse confirmation (grep)
```
src/physics/weekend_state/layer3_fieldcar.py:58: from src.physics.layer2.pooling import DriftFit, fit_drift
src/physics/weekend_state/layer4_car.py:51:     from src.physics.layer2.pooling import PooledParameter, pool_random_effects
```
Tests additionally assert `l3.fit_drift is pooling.fit_drift`, `l3.DriftFit is pooling.DriftFit`, `l4.pool_random_effects is pooling.pool_random_effects`, that no `def fit_drift`/`class DriftFit`/`def pool_random_effects` is reinvented, and that the row-wise shrink reproduces `PooledParameter.shrunk` exactly.

### Per-layer σ note (deliverable)
Every layer carries its own explicit σ column (`model.layer_sigma_cols()` enumerates them per axis):
- L1: `{axis}_layer1_sigma` (stored axis σ ⊕ density-fit σ ⊕ mass σ ⊕ rho-fallback penalty; from g2).
- L2: `{axis}_l2_delta_sigma` = 0 in axis units — honest: the grip-`g` latent is unmapped to physics-axis units (g3 FLOAT), so its correction and correction-σ are 0 on this frame; kept explicit.
- L3: `{axis}_l3_relative_sigma` (car σ ⊕ field-median SE), `{axis}_l3_fieldcar_sigma` (`DriftFit.predict` SE), `{axis}_l3_absolute_sigma` (quadrature of the two).
- L4: `{axis}_car_signal_sigma` = `sqrt((1−shrink)²·σ_μ² + shrink²·σ²)` — a hard-shrunk weekend inherits the season-mean uncertainty, a trusted one keeps its own.

## Docs/contracts touched
- None beyond the new modules' own docstrings.

## Assumptions
- **L1 applied per-year** in `model.py` so the mass term is exactly inert — consistent with layer1's own honest-null stance ("mass contributes ZERO to same-year comparisons"). This is the clean way to keep held-out L1 residuals row-local without modifying the frozen `layer1_physics.py`. Documented in `_apply_layer1_per_year`.
- **Field-median SE** uses the asymptotic median-vs-mean factor `sqrt(pi/2)`; a reasonable, standard honest inflation over the mean SE.
- **Re-anchor trajectory fit per year** (each season is its own random walk over `round_idx`); `fit_drift` returns a flat season mean when development is indistinguishable from field-median noise (step_var clamps to 0) — correct, not a bug. Synthetic test fixtures set development above the median-noise floor so `step_var>0` and the trajectory tracks.
- Layer-4 rows whose car-season has no train pool → `NaN` (never fabricated); the gate's `dropna` handles them.

## Stop conditions hit
- None. `pooling.py`'s API fit both needs cleanly (`fit_drift`/`DriftFit` for the re-anchor, `pool_random_effects` for the car signal); no-leakage was guaranteeable in the composition (proved by test + real-data smoke).

## Out-of-scope observations
- **L2 remains a FLOAT** on the frozen split (as g3 concluded): no per-car `cumulative_track_laps` bridge on the physics-estimate frame and a grip-`g`→axis-unit mapping is unmeasured. The assembler holds the seam so a future bridge (attach per-car representative-lap track state to each physics estimate — estimator work, out of scope here) slots straight in.
- The g5 F6 gate/writeup (not built here, per exclusions) can call `WeekendStateModel(...).fit(train)` then `gate_spec.evaluate_gate(train_frame, hold_frame, axes, model.model_cols())` directly — verified the guard and `evaluate_axis` run end-to-end on the model output.

## Workflow Feedback
- **Handoff gaps:** The handoff named "g2/g3 layers you compose" but the g2/g3 files are `layer1_physics.py`/`layer2_evolution.py` (numbered by model layer, not by gate) — I had to map gate→layer myself by reading. Minor; a one-line "g2=layer1_physics, g3=layer2_evolution" would have saved a lookup.
- **Context rediscovered:** That `fit_drift` returns a FLAT season mean when `step_var` clamps to 0 (random-walk smoother, not a slope fit) is not obvious from the seam signature and cost one red-test iteration on my synthetic fixture — worth a note in the pooling.py reuse block that the re-anchor only "moves" when development clears the field-median noise floor.
- **Instructions improvised around:** The engine `current` verb rejects `--session-id` (read-only), while every mutating verb requires it — the reference says `current` "needs no session" but the RAIL after `advance` pushed toward a session-scoped check; I dropped the flag. No real friction.
- **What would have made this easier:** none — confirmed after review: handoff carried task/intent/scope/exclusions/evidence/test-mode/stop-conditions, and the exact pooling.py signatures inline were exactly right.

## Map Impact
- **Structural anchors touched:** `layer3_fieldcar.py` / `layer4_car.py` / `model.py` — NEW modules under `src/physics/weekend_state/`; each imports the `src/physics/layer2/pooling.py` seam (REUSE edge: `fit_drift`/`DriftFit`, `pool_random_effects`) and the g1 `floor`/`frame` modules.
- **Capabilities added:** field-car common-mode decomposition (relative + re-anchored absolute) and the shrunk car signal, each with explicit σ; assembled leak-free via `WeekendStateModel.fit`/`transform`.
- **Constraints honored:** `constraint:physics_region_no_evo_import` (asserted per module); no-leakage held-out (train-only hyperparameters, proved); no `data/*.db` staged.
- **Decision realized:** cake-and-eat-it two-stage L3; car-signal = the F6-measured quantity; L2 kept-but-inert per the g3 FLOAT.
- **Claims/evidence produced:** reconstruction identity, pooling.py faithful reuse, and no-leakage all backed by green tests + a real-frame smoke.
- **Triage candidates:** L2 grip→axis-unit bridge (estimator work) to un-float Layer 2 on the frozen split.

## Return status
`complete`
