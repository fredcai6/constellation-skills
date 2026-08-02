# G4-B — Race-start σ correlation investigation

**Module:** `driver_race_start_power_from_race_weekend`
**Smoke:** [2023] → 2024, epochs=5

**Verdict:** `flat_signal_artifact`

**Archive G5 reference (full gold, not re-run):** λ=0 corr=0.105, λ=1 corr=-0.397

**G5 recommendation:** λ_sigma_nll=1.0, student_t_nu=4.0

Keep repo-wide λ=1 unless human overrides after G5; race-start event-corr is misleading.

## Findings
- **Archive G5 flip (−0.40)** used full-gold 2018–2024 event-level corr on σ_π trace; **smoke 2024 retrains** all show **positive** corr (0.43–0.56) — sign is not stable under budget/window.
- **Promoted bundle** (no-train, 2024 eval): event corr **+0.16** pearson / **+0.08** spearman; per-pair σ_std **0.0014** (collapsed) vs smoke λ=1 σ_std **~0.039** — field-level σ_π trace is a poor race-start diagnostic.
- σ_π trace spread across smoke events (std): λ=0.0:0.001016 … λ=2.0:0.000944 — sub-millimeter dynamic range; LOO stable → not outlier-driven on smoke.
- λ sweep **does not** fix a negative corr on smoke; higher λ **increases** positive corr — no evidence for λ=0.5 repo-wide change from this module alone.

## λ sweep (smoke retrain)
| λ | pearson | spearman | LOO pearson μ | σ_pair std (median event) |
|---:|---:|---:|---:|---:|
| 0.0 | 0.43054573326442497 | 0.3095652173913043 | 0.4299990270259209 | 0.042927488684654236 |
| 0.5 | 0.48867456372173385 | 0.3643478260869565 | 0.48799654978937657 | 0.039627715945243835 |
| 1.0 | 0.5106611068761 | 0.37913043478260866 | 0.5099402148761608 | 0.0381796732544899 |
| 2.0 | 0.5618526789140701 | 0.48260869565217385 | 0.5610428741986848 | 0.036580100655555725 |

## Promoted bundle (no-train eval)
- corr(σ_π, log_loss): pearson=0.16291199411647408, spearman=0.08498023715415019
- per-pair: σ_std=0.0014138101718190635, |r| median=0.07496288418769836, p95 |r/σ|=2.8392201423644985
