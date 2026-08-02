## What this answers (plain English)

Step 2 of epic #372. The question this PR settles: **when we stop pretending our four expert
models are independent and correctly account for how much they overlap, does that make the
predictions rank drivers better, or does it just make the confidence numbers more honest?**

Today's fusion multiplies the four module fields (constructor/driver × recent-form/race-weekend)
together as if they were independent measurements. They are not — they look at overlapping evidence
and agree with each other far more than chance. We measured that overlap directly and it is large:
cross-module correlations of **0.71–0.89**, highest exactly where expected (the constructor signal
projected onto drivers vs the driver signal). Treating overlapping experts as independent
double-counts their shared signal and makes the fused answer over-confident.

We built an offline replay harness and a fusion variant ("A") that carries that overlap as a proper
correlation and combines the experts jointly so the shared part is discounted instead of
double-counted. We scored it against today's fusion on **all three tasks** (qualifying, race start,
race) over **173 races (2018–2025)** with four metrics: ordering log-loss, rank error, rank
correlation, and how often the truth lands inside the predicted error bars (calibration).

### The verdict

**Correctly handling the redundancy moves CALIBRATION, not ORDERING.** It makes the error bars more
honest (coverage moves toward where it should be, ordering log-loss improves a little) but it does
**not** improve the order drivers are predicted in — on rank error and rank correlation the
correlation correction is flat-to-slightly-negative on every task.

The clincher is a decomposition. Variant A bundles two changes vs today's fusion: a per-entity
*reformulation*, and the *correlation* itself. Only the second is what this issue is about. Isolating
it (via the R=I ablation), the **correlation component is flat-to-negative on ordering** (rank-error
delta +0.20 / +0.05 / +0.27; rank-correlation delta −0.033 / −0.004 / −0.049 for quali / race-start /
race) and **positive on calibration** (80% coverage delta +0.015 / +0.018 / +0.037). The eye-catching
race-start ranking gain comes almost entirely from the reformulation, not the correlation; and
cheap-B (correcting only the single worst overlap block) shows the same pattern — so this is not an
artefact of estimating a full 4×4 matrix.

**Consequence for the epic:** the remaining ordering headroom is in module *interactions* (#374), not
in redundancy discounting (this issue, #373). A correlated-covariance update is still worth adopting
later as a *calibration* fix (e.g. for a Monte-Carlo race sim) — but that is a separate decision and
should not be expected to improve finishing-order accuracy.

The full numbers, tables, and reproduction steps are in `docs/evo/fusion_rework_findings.md`.

## What changed (technical)

Production fusion behaviour is **unchanged**: everything here is opt-in / offline. There are no
production or runtime call-site changes.

- **`src/evo_predictor/fusion.py`** — new pure function `fuse_module_fields_correlated`: per-entity
  GLS fusion with a k×k cross-module error correlation R (`Σ_i = D_i R D_i`). At R=I it reduces
  exactly (≤1e-9) to a per-entity diagonalized baseline (the documented identity anchor, since R is
  cross-*module* not cross-*entity*). `fuse_module_fields_ordered` is byte-for-byte untouched.
- **`src/evo_predictor/fusion_training/_correlation.py`** — `estimate_cross_module_correlation`
  (R from per-(event,module) standardized residuals `module_π − target_μ`, pooled over common
  entities, Ledoit-Wolf-style shrink toward I, explicit skip accounting) and
  `mask_correlation_to_block` (cheap-B constructor↔driver block mask).
- **`scripts/fusion_replay/`** — offline numpy-only harness: `records.py`, `baseline.py` (reproduces
  production fusion to ≤1e-9), `scoring.py` (pairwise log-loss / rank MAE / spearman / coverage),
  `variants.py`, `generate_records.py` (backtest-only record generation), `scorecard.py` (loads real
  per-event #371 module records, canonical `year:round:gp` join, DB-sourced constructor↔driver
  mapping with a collision-guarded lineage normaliser, estimates R, scores baseline vs A vs cheap-B
  + ablations on all 3 tasks at 173/173 events each).
- **`docs/evo/fusion_rework_findings.md`** — the measurement + verdict.
- **`tests/unit/evo_predictor/test_fusion_correlated.py`**, **`test_fusion_scorecard.py`** — synthetic
  unit tests (R=I identity multi-seed, planted-correlation recovery, shrinkage/conditioning, cheap-B
  masking, production-unchanged, scorecard wiring + canonical join + lineage normaliser + driver-drop).
- Architecture map reconciled (`docs/architecture/`); generated records are gitignored artifacts.

## Coverage & scope notes

- **173 / 173 joined races scored per task, seasons 2018–2025** (full available span).
- Measurement uses a **fixed unit-scale** fusion config so the A−baseline delta isolates R's effect;
  a trained-scale confirmation run is a noted follow-up (would not flip the verdict — delta is taken
  under one shared config).
- Absolute coverage is low under unit scales (under-dispersed posteriors); the measurement isolates
  the *direction* of R's effect, which is what the gate needs.
- Missingness is explicit and counted (never imputed), e.g. ~284 race-start driver-events dropped
  where the recent-history module legitimately omits low-evidence midfield constructors.

## Verification

- `py -m pytest tests/unit/evo_predictor/ -k "fusion or record" -q` → 296 passed.
- `py -m pytest tests/unit/evo_predictor/test_fusion_correlated.py tests/unit/evo_predictor/test_fusion_scorecard.py -q` → green.
- `py -m src.utils.simplification_limits` PASS on all new files (the one remaining flagged item,
  `fuse_module_fields_ordered`, is a pre-existing production violation, untouched here, logged as a
  follow-up).
- Each gate independently reviewed (G1, G2, G3 — all APPROVE) under the constellation workflow.

Closes #373

🤖 Generated with [Claude Code](https://claude.com/claude-code)
