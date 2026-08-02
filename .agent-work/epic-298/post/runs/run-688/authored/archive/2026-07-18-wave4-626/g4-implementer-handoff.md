# Implementer Handoff

## Gate
`g4` — Layer 3 (field-car common-mode: relative + smooth re-anchor) + Layer 4 (car signal) + `model.py` (four-layer assembler), each carrying honest σ, leak-free on held-out.

## Task
Build three files:
- `src/physics/weekend_state/layer3_fieldcar.py` — the cake-and-eat-it two-stage field-car decomposition.
- `src/physics/weekend_state/layer4_car.py` — the car signal (shrunk deltas off the field car).
- `src/physics/weekend_state/model.py` — composes L1→L2→L3→L4 into a decomposed per-car-weekend state, each layer carrying its own σ, TRAIN/HELD-OUT aware with NO leakage.

## Layer 3 — two-stage (cake-and-eat-it)
Operate per axis on the Layer-1 residual (Layer-2 is a wide-σ near-no-op on the frozen split per g3 — apply it where present, it just won't move much; do NOT drop it from the pipeline):
- **(a) RELATIVE** = car value − that weekend's `(year, round_idx)` field MEDIAN (this is the fast-resolving component; identical median transform as g1 `floor.weekend_relative`). σ from the car's axis `_sigma` + the field-median SE.
- **(b) RE-ANCHOR** — fit a SMOOTH field-car ABSOLUTE trajectory per axis over the season so absolute development still accrues. The "field car" = the per-weekend field-median series; fit its smooth trajectory over `round_idx` with `fit_drift`, then `DriftFit.predict(round_idx)` gives the smooth absolute field-car value + σ at each weekend. Reconstruct: `absolute_state = field_car_trajectory(round) + relative`. Both stages carry σ.

## Layer 4 — car signal
The car signal = the shrunk/partial-pooled per-weekend RELATIVE deltas off the field car (the quantity the F6 gate measures). Pool each car-season's per-weekend relative readings with `pool_random_effects` → the empirical-Bayes `shrunk` per-weekend estimates (partial pooling toward the car-season mean; τ answers "how much does this car really move week to week"). Lower jitter than the raw per-weekend relative → the mechanism to beat x4's floor. Carry σ (the pooled `sigma_mu` + per-session shrink).

## pooling.py — EXACT signatures to REUSE (verified this run; cite them, do not reinvent)
`src/physics/layer2/pooling.py`:
- `pool_random_effects(values, sigmas, *, sigma_floor=1e-9) -> PooledParameter` where `PooledParameter(mu, sigma_mu, tau, n, q_stat, i2, shrunk: np.ndarray, weights: np.ndarray)`. DerSimonian–Laird τ²; `shrunk` = per-session EB partial-pooled estimates; k==1 returns the point unchanged.
- `fit_drift(values, clock, sigmas=None) -> DriftFit` where `DriftFit(drift_rate, step_var, clock, values, sigmas)` and `DriftFit.predict(clock_target: float) -> (mu, sigma)`. Random-walk-along-clock: `Var(θ_s−θ_t)=step_var·|Δclock|`; predict down-weights sessions far in development. USE this for the field-car trajectory (values = per-weekend field medians, clock = round_idx, sigmas = field-median SE).
- `weighted_trend(values, sigmas, times, *, sigma_floor=1e-9) -> dict` — drift/upgrade-direction flag; use to report whether the field car is developing.

## NO-LEAKAGE discipline (load-bearing — this is what makes the F6 gate honest)
The car-signal must be computable on a HELD-OUT weekend using ONLY hyperparameters fit on TRAIN weekends. Concretely: fit the field-car `DriftFit` step_var and each car's pool τ on TRAIN weekends only; the held-out weekend's car-signal = predicted from the train-only fit (its relative reading scored against the train-fit trajectory). DO NOT let a held-out weekend enter the pool/drift fit that produces its own prediction. Wire `model.py` so a `fit(train_df)` → `predict(any_weekend)` split is explicit and testable. This aligns with g1 `gate_spec.py`'s F1 signal-preservation guard (out-of-sample residual around the train-fit trajectory) — READ gate_spec.py and make model.py's held-out output feed it directly.

## model.py — assembler
`model.py` composes L1 (explained physics removal) → L2 (within-session evolution, wide-σ where absent) → L3 (relative + re-anchor) → L4 (shrunk car signal), producing per car-weekend×axis a decomposed state where EACH layer carries its own explicit σ (the honest per-layer σ is a deliverable — it feeds Phase-3 σ-honesty). Provide `fit(train_df)` and `car_signal(df, holdout-aware)` that g5 will call.

## Protected Intent
The decomposition is only useful if the σ are honest and the held-out path has NO leakage. A car-signal that beats the floor by leaking held-out data into its own fit is a fake win.

## Test Mode
Test-after allowed. Load-bearing tests: two-stage reconstruction (relative + re-anchor = absolute), no-leakage (held-out prediction unchanged whether or not the held-out weekend is in the "predict" call's own fit set), pooling.py reused (not reinvented).

## Close Criteria
- Layer 3 produces relative + re-anchored absolute, both with σ; reconstruction `field_car_traj + relative == absolute` holds (test).
- Layer 4 car signal = `pool_random_effects` shrunk deltas with σ.
- `pool_random_effects` + `fit_drift` from `src/physics/layer2/pooling.py` are IMPORTED and used (not copied/reinvented) — a test asserts the import.
- `model.py` assembles all four layers, each carrying σ; `fit(train)`→`predict(held-out)` has NO leakage (a test proves the held-out car-signal is identical whether or not that weekend is included in the predict-call's fit population — i.e. it's driven by train-only hyperparameters).
- `test_layer3_fieldcar.py` + `test_model.py` pass.
- No evo import; no `data/*.db` staged.

## Allowed Scope
`src/physics/weekend_state/{layer3_fieldcar,layer4_car,model}.py`; `tests/unit/physics/weekend_state/{test_layer3_fieldcar,test_model}.py`. MAY read g1/g2/g3 files + `src/physics/layer2/pooling.py`.

## Specific Exclusions
Do NOT build the g5 F6 gate/writeup. Do NOT modify g1/g2/g3 files, `pooling.py`, estimator, evo, config. Do NOT commit/modify `data/*.db`.

## Constraints
- Python `py`. Absolute DB paths into `C:/Programs/f1Brainz/data/*`.
- REUSE pooling.py (cite exact signatures above); lesson:handoff-cite-exact-seam-signature.
- No leakage: train-only hyperparameters for held-out prediction.
- `constraint:physics_region_no_evo_import`. Every layer carries explicit σ.

## Map Anchors (inbound)
- Structural: `layer3_fieldcar.py`/`layer4_car.py`/`model.py` (NEW); `src/physics/layer2/pooling.py` (REUSE — pool_random_effects, fit_drift/DriftFit, weighted_trend).
- Capability: field-car common-mode (relative + re-anchored absolute) + car signal, each with σ.
- Constraints: no-leakage held-out; no evo import.
- Decision: cake-and-eat-it two-stage; car-signal is the F6-measured quantity.
- Evidence: pooling.py reused faithfully; reconstruction + no-leakage tests pass.

## Deliverable Path Check
- Committed: the three `src/physics/weekend_state/*.py` + two tests (not gitignored). Untracked until staged.

## Required Evidence
- `py -m pytest tests/unit/physics/weekend_state/test_layer3_fieldcar.py tests/unit/physics/weekend_state/test_model.py -q` → pass.
- A no-leakage demonstration (held-out car-signal identical with/without the held-out weekend in the predict population).
- Confirmation the pooling.py symbols are imported (grep).

## Verification Commands
```bash
cd C:/Programs/f1-626
py -m pytest tests/unit/physics/weekend_state/test_layer3_fieldcar.py tests/unit/physics/weekend_state/test_model.py -q
```

## Suggested Model Tier
Stronger — the no-leakage held-out composition + honest per-layer σ assembly is subtle; a leak here silently fakes the whole F6 result.

## Authority
Two-stage design + pooling.py reuse + no-leakage are frozen. The exact σ-combination formulae are yours but must be honest and per-layer.

## Stop Conditions
Stop/return if: pooling.py's API doesn't fit the re-anchor need (report the mismatch — do not hand-roll a divergent pool), or no-leakage cannot be guaranteed in the composition (that is a design problem to surface, not paper over).

## Return Format
Return IMPLEMENTER_RESULT to `.agent-work/wave4-626/g4-implementer-result.md`: completed slice, files changed, test output, the no-leakage demonstration, the pooling.py-reuse confirmation, per-layer σ note, assumptions, stop conditions, out-of-scope observations, workflow feedback.
