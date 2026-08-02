# Issue #142 — Cartographer reconcile summary

**Gate:** reconcile (post `ee6d501..d3827fe` on `codex/issue-142-sigma-calibration`)  
**Date:** 2026-05-29  
**Scope:** `docs/architecture/index.md`, packets, overlays — no code changes.

## Code truth verified (read-only)

| Claim | Evidence |
|---|---|
| `target_mode` is `retro_delta` only | `LatentPowerConfig.ALLOWED_TARGET_MODES`, `gold_defaults.toml` `[training]`, `training.py` requires `target_mu` |
| BCE / triangle retired | `modules.loss_from_pairwise` uses `student_t_nll` only; no `triangle_loss` / BCE branch in `src/latent_power` |
| Detached sigma NLL (term B) | `modules.loss_from_pairwise` + `lambda_sigma_nll` on config; gold default `1.0` in `[uncertainty]` |
| Field-solve W cap | `field_solve._solve_one_component` clamps with `config.solve_sigma_floor` before `W = 1/sigma^2` |
| Post-hoc calibration orthogonal | `enable_sigma_calibration` unchanged in gold defaults; ADR 0008 §4 |

## Doc state before reconcile

| Artifact | Status |
|---|---|
| `docs/architecture/packets/latent_power.md` | **Current** — updated in `d3827fe` (retro-delta sole path, sigma NLL, BCE/triangle removal, `solve_sigma_floor`) |
| `docs/adr/0008-retro-delta-supervision.md` | **Current** — created in `d3827fe` |
| `docs/architecture/overlays/` | **Current** — no BCE/triangle/BT-loss stale strings |
| `docs/architecture/index.md` | **Stale** — `struct:lp.training` still said "pairwise BT loss"; `struct:lp.field_solve` / `struct:lp.retro` underspecified |
| `docs/architecture/packets/evo_predictor.md` | **Stale** — gold_cycle section omitted ADR 0008 supervision passthrough and report flags |

## Changes made

1. **`docs/architecture/index.md`**
   - Verification stamp → issue-142 sigma calibration reconcile.
   - `struct:lp.training` purpose → retro-delta + detached sigma NLL (not BT loss).
   - `struct:lp.field_solve` purpose → `solve_sigma_floor` before precision weighting.
   - `struct:lp.retro` purpose → ADR 0008 retro-delta inputs; confidence `high`.

2. **`docs/architecture/packets/evo_predictor.md`**
   - Gold cycle paragraph: ADR 0008, `retro_delta` only, `lambda_sigma_nll` passthrough, orthogonality of post-hoc calibration, gold report fields.

## Intentionally not changed

- **Code** — per gate instructions.
- **`docs/architecture/packets/latent_power.md`** — already reconciled in implementation commit.
- **`src/latent_power/README.md`** — still says "trained on pairwise outcomes" in Known baseline limits; outside Cartographer-owned paths (`packets/`, `index.md`, `overlays/`). Route to Triage if module-local README should track ADR 0008.
- **`configs/evo/gold_defaults.toml` comments** — still mention `bce` historically in `[training]` comment block; config value is `retro_delta` only.
- **`docs/evo/modules/race_weekend_driver.md`** — validation gate still references "BCE-at-0.5 baseline" as an eval metric threshold, not a training path.

## Verdict

Map reconciled for issue #142 sigma calibration. Index and evo_predictor packet now align with latent_power packet and ADR 0008.
