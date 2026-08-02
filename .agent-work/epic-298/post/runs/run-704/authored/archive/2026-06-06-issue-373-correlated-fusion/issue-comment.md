## Verdict: correlated-covariance fusion moves CALIBRATION, not ORDERING

Done in PR #416. This is the measurement epic #372 gates on.

**Plain English.** Today's fusion multiplies the four expert modules (constructor/driver ×
recent-form/race-weekend) as if independent. They are not — measured cross-module correlations are
**0.71–0.89**, highest exactly where expected (constructor-projected-onto-drivers vs the driver
field). I built an offline replay harness + a fusion variant ("A") that carries that correlation as a
proper off-diagonal covariance and combines the experts jointly, plus the constructor↔driver cheap-B
special case and ablations. Scored baseline vs A vs cheap-B on **all 3 tasks over 173 races
(2018–2025)** with pairwise log-loss, rank MAE, spearman, and credible-interval coverage.

**Result: correctly discounting the redundancy tightens calibration but does not improve ordering.**
On rank MAE and spearman the correlation correction is flat-to-slightly-negative on every task; on
coverage and ordering log-loss it helps. The decisive evidence is the decomposition via the R=I
ablation — variant A bundles a per-entity *reformulation* and the *correlation*, and only the
correlation is what #373 tests:

| Task (n=173) | correlation Δ rank MAE | correlation Δ spearman | correlation Δ cov80 |
|---|---:|---:|---:|
| quali | +0.198 (worse) | −0.033 (worse) | +0.015 (better) |
| race_start | +0.048 (≈flat) | −0.004 (≈flat) | +0.018 (better) |
| race | +0.269 (worse) | −0.049 (worse) | +0.037 (better) |

Key per-task numbers (baseline → A):
- **quali**: pairwise-LL 0.649 → 0.635, rank MAE 3.33 → 3.35, spearman 0.685 → 0.679, cov80 0.042 → 0.069
- **race_start**: pairwise-LL 0.615 → 0.592, rank MAE 2.49 → 1.86, spearman 0.757 → 0.842, cov80 0.020 → 0.048
- **race**: pairwise-LL 0.640 → 0.628, rank MAE 3.33 → 3.17, spearman 0.639 → 0.655, cov80 0.036 → 0.076

(The eye-catching race_start rank-MAE drop is almost entirely the per-entity *reformulation*, not the
correlation — Δreform −0.68 vs Δcorr +0.05. cheap-B shows the same pattern, so it is not an artefact
of a full 4×4 R.)

**Consequence for #372:** ordering headroom is in module **interactions (#374)**, not redundancy
discounting (#373). A correlated-covariance update remains worthwhile **as a calibration fix** (e.g.
feeding a Monte-Carlo race sim) — a separate decision from this measurement.

**Coverage / caveats:** 173/173 joined races per task, full 2018–2025 span. Measured under a fixed
unit-scale config to isolate R's effect (a trained-scale confirmation run is a noted follow-up; it
would not flip the verdict). Absolute coverage is low under unit scales (under-dispersed posteriors);
the measurement isolates the *direction* of R's effect. Production fusion behaviour is unchanged
(variant A is opt-in/offline). Full numbers + reproduction in `docs/evo/fusion_rework_findings.md`.

**Follow-ups recorded** (not auto-filed): confirm under trained covariance scales; a shared
constructor-lineage canonical mapping (DB season names vs collapsed record lineages); adopt A as a
production calibration fix if calibrated uncertainty becomes a goal; refactor the pre-existing
`fuse_module_fields_ordered` simplification violation.
