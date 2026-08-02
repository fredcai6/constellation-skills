# Issue #374 — The Step-3 Gate: interaction-headroom measurement (problem statement + pre-stated decision rule)

**Role:** Commander, wave 2 of fleet for epic #372. This is a MEASUREMENT/DECISION, not a build.
**Branch:** `constellation/issue-374-c-gate`. **Closes #374.** Feeds #375 (greenlight/defer the context-conditioned net) and the #372 Step-4 gate.

---

## The question (one line)

Do **interactions over the four module outputs** carry **ordering** signal that the **best possible linear opinion pool** leaves behind? If yes at the module-output level → greenlight #375; if flat → defer #375 (conservative gate, NOT exoneration — it's a lower bound).

## Why this framing (reconciled against wave-1 verdicts)

- **#373 (merged):** correlated-covariance fusion moves CALIBRATION, not ORDERING (173 events, 3 tasks; correlation component flat-to-negative on rank MAE / Spearman; correlations 0.71–0.89). ⇒ **Redundancy is eliminated as the ordering bottleneck.** My gate now carries the whole "where is the remaining ordering headroom?" question at the module-output level.
- **#414 (merged):** for quali, the race_weekend head is missing INFORMATION; a plain cross-channel practice-pace anchor recovers ~68% overall / ~72% EASY of its ~19pp gap (0.6153→0.7452 vs 0.8061 ceiling) at α=0.5; magnitude-only recalibration is an exact no-op. Verdict BOTH-STAGED: a cheap anchor banks the majority; the ~30% remainder is per-context (what a conditioned net would learn). The anchor's win happened BELOW the module-output layer. ⇒ (a) contextualize my quali gap against that banked result; (b) the under-counting my lower-bound caveat prices in is real and demonstrated — say so.

## Data substrate (reuse the existing harness — do NOT rediscover the constructor mismatch)

`scripts/fusion_replay/scorecard.py::_preprocess_events` already yields, per (task, event):
- `driver_ids` (common across driver modules, team-validated via DB `get_race_driver_teams`, lineage-remapped via the collision-guarded normalizer, ≥3 drivers)
- `event_arrays` (the four module records), `constructor_by_driver` (remapped)
- `actual_positions`, `target_mu` aligned to `driver_ids` (NaN for missing)

My data-builder adds ONE faithful step (already done inside `run_event_variants`): align each module's `pi` to `driver_ids` — driver modules via `_align_driver_pi`, constructor modules via `project_constructor_field_to_drivers`. Result per event: `X_event` shape `(n_drivers, 4)` of module pi + `actual_positions` `(n_drivers,)`. Records regenerated into the **gitignored** `outputs/evo_runs/` (NOT `.agent-work/`, which is tracked).

The four module columns per task (canonical `module_names_for_task` order):
`[constructor_*_from_recent_history, driver_*_from_recent_history, constructor_*_from_race_weekend, driver_*_from_race_weekend]`.

## Target / objective (ONE primary, justified in two sentences)

**Primary: pairwise outcome from `actual_positions`, scored by pairwise log-loss.** This IS the harness's centerpiece ordering metric (`scoring.pairwise_log_loss`: for each pair, p = sigmoid(piᵢ−piⱼ), y = 1 if i finishes ahead) used across all of #373, so Model1/Model2 numbers are directly comparable to the established ceilings; and the fusion question is fundamentally "which pi-ordering best predicts who-beats-whom," which is the pairwise structure itself.
**Secondary (cheap, same arrays): rank MAE and Spearman** of the predicted pi vs actual. `target_mu` (retro-BT) is calibration-flavored and is reported only as a robustness check, not the gate metric.

## Models (the gate is Model2 − Model1)

- **Model 1 — best linear pool.** Logistic over **pairwise pi-differences**: for a pair (i,j), feature vector `Δpi = [pi^(m)_i − pi^(m)_j]` over the 4 modules; predict P(i beats j) = sigmoid(w·Δpi + b). Fit by minimizing pairwise log-loss (this is precisely the harness's scoring objective). This is the **ceiling of ANY precision-weighted fusion** (any per-module linear weight on pi reduces to a w on Δpi). Antisymmetry handled by construction: train on i<j pairs with the binary label, no bias term on the ordering (a pair and its mirror are symmetric) — documented in code.
- **Model 2 — interaction model.** Same inputs, adds interactions over Δpi: (a) explicit degree-2 product terms of the 4 Δpi components under the SAME logistic objective (numpy/scipy), AND (b) a small torch MLP on Δpi. Report both; the gap is `Model1_loss − Model2_loss` (positive = Model2 better = interaction headroom). **sklearn is ABSENT and intentionally NOT installed** (decision logged) — scipy.optimize + torch cover both Model2 forms.

## #140 deviation probe (the concrete hypothesis)

Construct, per entity per scope, **deviation = weekend_pi − recent_pi** (constructor-scope and driver-scope separately). As pairwise features these are differences of deviations. Test whether adding the deviation terms (and, for downstream tasks, prior-stage-order × deviation as a secondary probe) improves ordering prediction **beyond the four main pi effects** — i.e. nested-model gain. This operationalizes "upgrade / track-fit shows up as weekend-vs-form disagreement."

## Validation (mandatory minimum)

**Leave-one-season-out (LOSO) CV** over seasons 2018–2025 (8 folds): fit on 7 seasons' events, evaluate held-out season's pairwise log-loss; pool held-out predictions. CIs via **bootstrap over events** (resample held-out events, recompute the pooled gap). Report **per task, never averaged across tasks.** Within-fold standardization stats (if any) fit on train only — no leakage.

---

## DECISION RULE (STATED BEFORE MEASURING — applied mechanically)

The gate metric is the **LOSO pairwise-log-loss skill gap Δ_gap = Model1_loss − Model2_loss** (≥0 means interactions help), with a 95% bootstrap CI over events, **per task**.

**Scaling the threshold against known quantities.** The fusion-tuning ordering headroom already visible in #373 (baseline→best variant pairwise-LL) is ≈0.012–0.023 LL per task; #414 showed a single cheap cross-channel anchor explains the *majority* of quali's gap at the pre-fusion layer. So a *meaningful* interaction signal at the module-output level must be (i) statistically separable from zero AND (ii) of a magnitude comparable to the fusion-tuning lever it would compete with — not a rounding artifact. I therefore set:

- **τ_signif:** 95% bootstrap CI for Δ_gap **excludes 0** (lower bound > 0).
- **τ_mag:** point estimate Δ_gap **≥ 0.005 pairwise-LL** (≈ a third of the smallest #373 fusion lever; below this the interaction headroom is dominated by the linear/anchor levers already on the table and does not justify a bespoke conditioned net).

**Per-task verdict:**
- **GREENLIGHT** the task for #375 if `Δ_gap ≥ τ_mag AND CI excludes 0`.
- **DEFER** the task otherwise (either CI includes 0, or magnitude below τ_mag).

**#140 deviation sub-verdict (per task):** PRESENT if the nested gain from adding deviation terms to Model1 clears the same τ_signif AND τ_mag bars; otherwise ABSENT.

**Overall #375 recommendation:** scope = the set of GREENLIGHT tasks (e.g. "greenlight quali-only" if only quali clears). If NO task clears, recommend DEFER #375 with the explicit lower-bound caveat (the meta-learner sees only module outputs; #414 proved feature-level info the head distills badly, which this measurement under-counts).

**Honesty clause (from the brief):** a measured "no interaction headroom at the module-output level" is a COMPLETE, SUCCESSFUL deliverable. The gate's value is in trusting a flat result; I will not stretch to manufacture a signal. Compute budget ≤ ~2.5h.

---

## Pre-rulings honored

Scripts+tests only (no `src/evo_predictor/` changes); new code `scripts/fusion_replay/metalearner.py`, tests `tests/unit/evo_predictor/`. LOSO mandatory; bootstrap CIs over events; per-task. I am SOLE writer of `docs/evo/fusion_rework_findings.md` (append a new section); I do NOT touch `prediction_ceiling_and_priorities.md` or create `fusion_task_generalization.md`.

## Assumptions (surfaced; cannot ask the user)

1. **Primary target = pairwise outcome / pairwise-LL** (justified above) — the brief pre-ruling #2 says pick ONE consistent with the harness's pairwise scoring; this is the harness's scoring.
2. **τ_mag = 0.005 LL** chosen by scaling against #373's 0.012–0.023 fusion levers; surfaced as the load-bearing judgment. If the human wants a stricter/looser bar, the raw Δ_gap + CIs are reported so the verdict can be re-derived without re-running.
3. **Deviation probe** uses weekend−recent per scope (the #140 text). Prior-stage-order×deviation for race_start/race is a SECONDARY probe where records make it cheap (sister commander #377 owns the full stage-specific hypothesis doc; I don't block on her).
