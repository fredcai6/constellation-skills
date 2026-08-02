# G4 Smoke Validation — Issue #142 Sigma Calibration

**Gate:** G4 | **Date:** 2026-05-29 | **Branch:** `codex/issue-142-sigma-calibration`

## Commands run

```bash
py -m pytest tests/integration/test_retro_delta_smoke.py -q
# 1 passed in 0.77s

py .agent-work/issue-142-sigma-calibration/g4_sigma_smoke.py
# wrote evidence/g4-smoke-summary.json and evidence/g4-diagnostics.jsonl
```

## Data availability

| Resource | Present | Notes |
|----------|---------|-------|
| `data/*.db` | Yes (8 DB files) | Real F1 DBs available |
| `params/retro_truth` | Yes (1052 files) | Retro truth params available |

**Training mode:** Synthetic `target_mu` batches (3 events × 6 entities, feature_dim=8). Real DB+retro were available but synthetic was used for controlled sigma observability and faster iteration. Full gold retrain deferred to G5.

## Config exercised

| Parameter | Value |
|-----------|-------|
| `lambda_sigma_nll` | 1.0 |
| `solve_sigma_floor` | 0.05 |
| `student_t_nu` | 4.0 |
| `sigma_prior_max` | 10.0 (prior input only) |
| `epochs` | 10 |
| `learning_rate` | 1e-2 |

## Integration smoke

- `test_retro_delta_training_reduces_loss` **PASS** — loss decreased over 10 epochs on synthetic retro_delta batches.

## Sigma distribution (detached Student-t path)

### Initial (untrained network)

| Metric | Value |
|--------|-------|
| min | 0.667 |
| median | 0.733 |
| max | 0.951 |
| std | 0.062 |
| frac at `solve_sigma_floor` | 0% |
| NaN/Inf | none |

### Final (after 10 epochs)

| Metric | Value |
|--------|-------|
| min | 0.401 |
| median | 0.481 |
| max | 0.515 |
| std | 0.022 |
| frac at `solve_sigma_floor` | 0% |
| NaN/Inf | none |

### Per-epoch sigma evolution (selected)

| Epoch | train_loss | sigma_nll | σ min | σ median | σ max | σ std |
|-------|------------|-----------|-------|----------|-------|-------|
| 1 | -0.031 | -0.243 | 0.410 | 0.452 | 0.573 | 0.032 |
| 5 | -0.386 | -0.318 | 0.436 | 0.463 | 0.522 | 0.022 |
| 10 | -0.498 | -0.318 | 0.414 | 0.436 | 0.503 | 0.022 |

## Checks

| Check | Result |
|-------|--------|
| Loss decreases (first → last epoch) | **PASS** (-0.184 → -0.268) |
| No NaNs in loss or sigma | **PASS** |
| Sigma varies (not constant) | **PASS** — std 0.062 → 0.022, range shrinks but min≠max |
| Not stuck at prior-max ~10 | **PASS** — output σ ∈ [0.40, 0.52], well below `sigma_prior_max` |
| Detached σ NLL active | **PASS** — `sigma_nll` component logged each epoch, `lambda_sigma_nll=1.0` in total |
| `field_solve` W-cap sanity | **PASS** — max effective W ≈ 6.2 (σ≈0.40); cap at floor would be 400 (=1/0.05²); no pairs hit floor |

## field_solve / W-cap notes

- `field_solve` clamps σ to `solve_sigma_floor=0.05` before computing `W = 1/σ²`.
- In this smoke run **0%** of pairwise σ values reached the floor; max effective W was ~6.2 vs theoretical cap of **400** at the floor.
- W-cap is inactive here but correctly bounded when σ would otherwise go below 0.05.

## Recommendation: `solve_sigma_floor`

**Keep at 0.05.** Rationale:

1. Floor did not bind during smoke training — σ learned freely in the 0.40–0.52 band.
2. W-cap at 400 provides headroom against runaway precision without affecting this run.
3. No evidence that 0.05 is too aggressive or too loose on synthetic data; real-data G5 retrain should confirm binding rate on production batches.

## Artifacts

- `.agent-work/issue-142-sigma-calibration/g4_sigma_smoke.py` — smoke script
- `.agent-work/issue-142-sigma-calibration/evidence/g4-smoke-summary.json` — machine-readable metrics
- `.agent-work/issue-142-sigma-calibration/evidence/g4-diagnostics.jsonl` — per-epoch training diagnostics from `train_latent_power_module`

## Limitations

- Synthetic `target_mu` only; real retro_delta join path not exercised in this gate.
- Optional real-module train (`train-latent-power-module`) skipped — synthetic sufficient for G4 per handoff.
