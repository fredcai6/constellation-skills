# Plan-alternatives (design-it-twice) + converged gate plan — #628

## Two candidates under distinct constraints

### Candidate A — reuse-max (ratio observable)
**Constraint: minimal new code, max reuse of the shipped #510 layer.**
Observable = the existing `regime_utilization` ratio `U_r = mean(v_real/v_ideal)` per (driver,session,regime),
run through `characterize_cases`. Driver utility δ = shrunk driver-mean U_r from train sessions. Held-out:
predict held-out U_r from δ.
- Pros: almost no new modeling code; reuses a tested path.
- Cons (fatal for F4): the observable IS `observed÷capability`. A cold F4 critic reads the utility as the
  forbidden ratio; recomposition `δ × v_ideal ≈ v_real` does not RECOMBINE capability (it was already divided
  out) — the held-out test degenerates to "is the driver's ratio stable," not "capability ⊗ utility predicts
  behavior." Also uses the through-W ceiling (measured-driver-contaminated) → leakage risk on held-out.
- Compute: same 74–108 s/case (full MAP via characterize) → also worse on feasibility.

### Candidate B — absolute-deficit, causal-ceiling additive latent (RECOMMENDED)
**Constraint: structural anti-circularity cleanliness (F4) is load-bearing.**
Observable = absolute per-regime **speed deficit** `g_{d,s,axis} = mean(v_ideal_causal − v_real)` where
`v_ideal_causal` comes from `build_car_ceiling(strictly_pre=True)` (excludes the held-out round). Driver-utility
latent δ_{d,axis} = partial-pooled driver mean deficit over TRAIN rounds (+σ, +resolved/unresolved status).
Held-out gate recomposes `v_ideal_causal − δ_d` → predicted v_real, checks (1) beats δ=0 baseline OOS and
(2) per-axis structure (corner var ≫ straight var) replicates OOS.
- Pros: no `observed÷capability` anywhere; recomposition genuinely recombines capability+utility; causal
  ceiling kills the truth-leak (`loo-residual-diagnostic` lesson); lean `fit_best_lap_trace` path (~28 s/case).
- Cons: new observable module + strictly_pre wiring + resumable batch. Worth it — F4 is the mission.

## Convergence → Candidate B, with one folded hybrid from A
Recommend **B**. Fold A's ratio in as a **non-gating diagnostic** column (interpretability + reputational
smell-test only) — never as the utility or gate basis. Untaken road recorded: A's pure-reuse path rejected
because it cannot survive a cold F4 critic.

Panel-vs-single: this is a load-bearing modeling plan → **single cold critic** dispatched (bias-to-yes;
a 3-lens panel is available but one focused F4-centric critic is proportional for a bounded round-1 artifact;
the panel option is the surfaced untaken road).

## Converged gate plan (authored into execute.json)
- **G1 [crew]** Observable module `driver_utility_observable.py` (pure: causal ceiling ⊗ trace ⊗ regime masks
  → per-axis absolute deficit rows; reuses `_build_regime_masks`, `PhysicsSimulator`, NO ratio) + resumable
  batch CLI `scripts/build_driver_utility_observables.py` (lean `fit_best_lap_trace`; scratch untracked DB;
  idempotent skip-if-present) + unit tests (at-ceiling→g≈0; corner-slow→g>0 corners ≈0 straight; resume).
- **G2 [crew]** Driver-utility latent estimator `driver_utility.py` (partial-pooling per (driver,axis) →
  δ+σ+status; `UNRESOLVED_AXIS_SIGMA_FRAC` reserved slots when support thin) + banked artifact
  (parquet/table, untracked) + unit tests (shrinkage; status flips; schema; nothing dropped silently).
- **G3 [crew]** Held-out gate harness `driver_utility_gate.py` (fit δ on train → predict held-out via
  `v_ideal_causal − δ`; recomposition RMSE vs δ=0 baseline OOS; per-axis cross-driver variance OOS;
  reputational smell-test table labeled non-gating) + unit tests incl. a **leakage self-test** (feeding a
  through-W non-causal ceiling must visibly inflate replication vs strictly_pre).
- **G4 [reasoning]** Methodology FREEZE: train/held-out split + pass/honest-null rubric written to a frozen
  file BEFORE any real numbers are seen. Crew-waived (design note in own context).
- **G5 [reasoning/run]** Launch G1 batch OS-detached on bounded 2023-Q slice (state-note first), poll rows
  in-turn, run G2 estimator + G3 gate on landed rows, produce held-out verdict numbers + honest-null
  disposition + reputational read. Crew-waived (running produced+reviewed code and interpreting).

Sequencing keeps verification green at each boundary: G1→G3 are synthetic-tested code; the real-data run is
G5 only, after the methodology freeze (G4).
