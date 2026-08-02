# Reviewer Handoff

## Gate
g4 — A/B evidence (issue #369, work area `.agent-work/issue-369-pace-gap-form/`)

## What Was Implemented
Evaluation run, no code changes: 4 bundles (driver/constructor quali RH × fresh-v1/treatment-v2) trained on the canonical split (2018–2024 train, 2025 eval, seed 0, gold-default params) and backtested on 2025; promoted gold report extracted as primary control; deliverable `.agent-work/issue-369-pace-gap-form/evidence/ab_comparison.md` (≈21 KB, 5 sections) plus `compute_metrics.py` (analysis script importing existing code) and `metrics_all_arms.json` in the same evidence dir. Training artifacts under `outputs/evo_runs/{treatment_v2,fresh_v1}_{driver,constructor}_quali_rh/` (untracked, per artifact policy).

## How to Inspect the Diff
No repo diff expected: `git -C C:\Programs\f1Brainz status --short` must show ONLY `.agent-work/issue-369-pace-gap-form/` (untracked) — anything else is scope drift. Review materials:
- `.agent-work/issue-369-pace-gap-form/evidence/ab_comparison.md` (the deliverable)
- `.agent-work/issue-369-pace-gap-form/evidence/compute_metrics.py` + `metrics_all_arms.json`
- `outputs/evo_runs/<the four run dirs>/` (bundle manifests, backtest outputs)
- Control sources: `reports/evo/gold_cycle_260530_152746_2018thru2024.{summary,details}.json`, `reports/evo/unc_diag_260530_152746_2018thru2024.json`, `params/gold/uncertainty_calibration/unc_cal_260530_152746_2018thru2024.json`

## Task Statement
Full implementer handoff: `.agent-work/issue-369-pace-gap-form/crew-handoffs/G4_IMPLEMENTER_HANDOFF.md`. Issue #369's acceptance: evaluate variance/uncertainty channel + calibration, NOT mean rank; confirm no regression on quali rank_mae / sign-accuracy; the σ-enrichment claim was explicitly UNTESTED and this A/B is its test.

## Close Criteria
**Arm comparability (honesty of the comparison):**
- Same split/seed/params across fresh-v1 and treatment-v2 — verify from the run dirs' recorded configs (only the encoding flag may differ).
- Param replication vs promoted run_config: the doc must name each param's source and any mismatch. The implementer ASSUMED `solve_sigma_floor=0.05` / `student_t_nu_sigma=None` (not recorded in promoted run_config) — check this assumption is stated in the doc, and spot-check it against `configs/evo/gold_defaults.toml` / CLI defaults.
- The promoted-vs-fresh caveats (149-event gold context vs 24-event standalone; post-hoc sigma calibration absent in standalone) must be stated where the numbers are compared, so a reader cannot mistake promoted↔treatment for apples-to-apples. The clean comparison is fresh-v1 ↔ treatment-v2 — confirm the verdict reasons from THAT pair primarily.

**Metric provenance:** every number in every table traceable to a named file (spot-check at least 4 numbers — e.g. one promoted control value against the actual report JSON, one treatment value against the run output, one correlation against `metrics_all_arms.json`). Verify `compute_metrics.py` IMPORTS existing functions for the correlation math rather than reimplementing it; if it computes Pearson r directly, confirm it does so on the same quantities the gold path correlates (per-event sigma_pi_trace vs per-event rank MAE / NLL) and that the NLL sign-convention bridge (`pairwise_nll` = −`pairwise_log_loss`) is handled and documented, not fudged.

**No overselling (the key review axis):**
- Ordering: doc must report rank_mae/sign-accuracy as ~flat (they are) without claiming improvement from noise-level deltas.
- Variance channel: results are MIXED (driver σ↔rank-MAE got WORSE 0.534→0.420; constructor better 0.427→0.494; σ↔NLL roughly flat-to-slightly-better both). The verdict must say "mixed/inconclusive" honestly, state n=24 and significance limits, and NOT recommend a default flip.
- The `pairwise_nll_skill` REGRESSION (driver 0.453→0.343, constructor 0.519→0.390) must be prominent in the verdict — fusion covariance weighting consumes `exp(-skill)`, so this finding matters downstream. If the doc buries or omits it → BLOCK.

**Completeness:** all five required sections present (arms tables incl. all five metrics + availability comparison; comparability note; availability/missingness; verdict; provenance appendix). Treatment bundles' `feature_schema_version` strings (`...v2`) confirmed and stated.

## Allowed Scope
Work-area evidence dir + `outputs/evo_runs/` artifacts. No repo file edits.

## Specific Exclusions
Any modification under `src/`, `tests/`, `configs/`, `docs/`, `scripts/`, `params/`, `reports/`. Flag if git status shows anything beyond the work area.

## Constraints the Implementation Must Respect
- Evidence not promotion: no params/gold or manifest changes, no default flip language.
- Generated artifacts stay untracked.
- `py` not `python`.

## Evidence Produced
From IMPLEMENTER_RESULT: all four runs completed (seconds each); verification commands pass (doc exists >500 bytes; git clean apart from work area); headline numbers as summarized above; v2 schema recorded in treatment bundles. Re-run the two verification commands and spot-check numbers yourself.

## Suggested Model Tier
simple bounded — careful reading + spot-check arithmetic; no design.

## Stop Conditions
Stop and return BLOCK if: the evidence files cannot be accessed, any number fails its provenance spot-check, the comparison misleads (overselling, buried regression, promoted↔treatment passed off as apples-to-apples), or git status shows repo drift.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope observations.
