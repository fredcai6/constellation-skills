# Issue #373 — Resolved Problem Statement

**Goal.** Build the durable offline fusion-replay harness over #371 records; implement
correlated-covariance fusion (variant A) plus the constructor↔driver cheap-B special case
as **opt-in offline variants** (production `fuse_module_fields_ordered` default UNCHANGED);
and deliver THE measurement the epic gates on: does correct redundancy handling move
**ORDERING** or only **CALIBRATION**.

## Reconciled facts (verified against code, not assumed)

1. **Production fusion** = `fuse_module_fields_ordered` (`src/evo_predictor/fusion.py:153`):
   sequential per-entity Gaussian precision product (`posterior_precision = prior_precision
   + obs_precision`, no off-diagonal) over a task's 4 modules. Canonical 4-tuple order
   (`module_names_for_task`): `(constructor_recent, driver_recent, constructor_weekend,
   driver_weekend)`. Production flattens the hierarchical 3-block config to one
   `FusionLayerConfig` via `to_runtime_fusion_layer_config` (prior_sigma=10, per-module
   `covariance_scale`, jitter 1e-6).

2. **The gold REPORT fingerprint** (pairwise LL 2.94→1.76, rank MAE ~0.2) comes from
   `_measured_fusion_metrics` (`fusion_training/_helpers.py:222`) = a **scalar
   inverse-trace-weighted blend of per-module precomputed backtest metrics** from
   `details.json`. It does **not** call `fuse_module_fields_ordered`. Therefore the harness
   **validation gate** = exact reproduction of `fuse_module_fields_ordered` (the harness
   calls the real function / matches it to ≤1e-9). The gold scalar number is reported as
   **context**, not the validation gate. *(Commander ruling — surfaced as a decision.)*

3. **R** = 4×4 cross-**module** error correlation, estimated in per-(event,module)
   **standardized residual** space (residual = `module_pi − target_mu`), pooled across
   events on common entities, shrunk toward I (Ledoit-Wolf-style; sweep λ as an ablation).
   Applied **per entity**: `Sigma_i = D_i R D_i`, `D_i = diag(per-entity module sigmas)`;
   GLS-combine the 4 observations of that entity's latent πᵢ. **R=I must reproduce the
   baseline exactly** — the implementer picks the A formulation that achieves the ≤1e-9
   identity and documents which.

4. **cheap-B** = variant A with R masked to only the constructor↔driver same-evidence
   block (R=I elsewhere). Isolates the worst redundancy (projected constructor field vs
   driver field, ~0.71–0.99).

5. **Scorecard** per task, baseline vs A vs cheap-B (+ ablations R=I, λ sweep), numpy-only:
   - pairwise log-loss (vs `actual_positions` ordering)
   - rank MAE (fused-π rank vs `actual_positions` rank)
   - spearman (fused-π vs `actual_positions`)
   - credible-interval coverage (fraction of entities whose `target_mu` falls in the k-σ
     interval from fused (π, diag σ_π); report 50/80/95% + coverage error)
   Per-event then averaged per task; also paired A−baseline deltas.

6. **Record generation** = **no training**. All 12 gold module bundles already exist at
   `outputs/evo_runs/gold_module_training_cycle/modules/`; retro_truth + compound_prior
   present for all years. Generate via **backtest-only** against existing bundles with
   `--emit-module-record` (schema doc "Direct backtest invocation"). Verify one
   single-backtest wall-time before committing to all 12. Records are non-committed
   generated artifacts (gitignored). Budget ≤ ~90 min.

## Constraints
- numpy-only harness under `scripts/` (importable helpers where natural), built for reuse
  by the epic's later steps.
- Sole code ownership this wave: `src/evo_predictor/fusion.py`, `fusion_training/`, new
  files under `scripts/` and `tests/`. Do NOT touch quali-head / latent_power
  evidence-weighting code or `docs/evo/prediction_ceiling_and_priorities.md`.
- Baseline-reproduction encoded as an automated test if a compact fixture is feasible;
  else a script assertion with logged evidence.
- DB read-only via absolute paths (`C:/Programs/f1Brainz/data/`). `PYTHONIOENCODING=utf-8`.
- Evo/probability rigor: calibrated metric evidence; one canonical path; no silent
  fallback/imputation (missingness explicit). `py -m src.utils.simplification_limits` on
  touched py paths.

## Protected intent
Production prediction behavior must NOT change in this issue. The reusable harness + the
ordering-vs-calibration measurement are the deliverables. A measured "A doesn't move
ordering" is a complete, successful result — do not stretch into interaction-headroom
(#374) territory.

## Substitution note (no live human)
This is a background run; the spine's `user-decision` checkpoints cannot reach a person.
Resolutions are adopted from the admiral brief + pre-rulings + verified code and logged as
the decision evidence. The verdict returns to the user via the issue comment + PR + final
report.
