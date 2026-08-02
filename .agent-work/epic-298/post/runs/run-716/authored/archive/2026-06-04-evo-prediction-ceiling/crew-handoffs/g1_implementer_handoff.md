# Implementer Handoff

Concise fragments. Omit filler.

## Gate
`g1` — offline evidence harness (significance + coverage). Measurement only.

## Task
Build a torch-free offline harness at the EXACT path
`.agent-work/evo-prediction-ceiling/evidence/sigma_significance_probe.py`
(run with `py`) that reads
`reports/evo/gold_cycle_260603_173742_2018thru2024.details.json` and produces a
compact evidence table answering two questions:

**(a) Significance of race-start `sigma_corr`.** For each of the 4 race_start
modules (and, for context, all 12 modules), compute
`sigma_corr = pearson(sigma_pi_trace, rank_mae_vs_retro_bt)` over that module's
`event_level_metrics` rows (these are the 24 eval-year-2025 events). For each,
report: point estimate, a 95% CI (bootstrap percentile over events AND the
Fisher-z closed form — they should agree), the two-sided p-value vs H0: rho=0,
and a verdict `significant` / `indistinguishable-from-0`. Also compute and print
the **n-aware critical |r|** `r_crit(n, alpha=0.05)` (closed form via the t
distribution: `t_crit=ppf(0.975, n-2)`, `r_crit=t_crit/sqrt(n-2+t_crit^2)`). This
`r_crit(n)` is the deliverable that SPECS G2's honest threshold.

**(b) Race-start sigma level / coverage.** Operationalize the doc's claim that
race-start sigma is "too high / too flat":
- "too high": compare each module's calibrated-sigma level to its realized rank
  error level. Use the fitted `alpha,beta` for each module (from the top-level
  `task_calibration_diagnostics` / `evidence_source_calibration_diagnostics` /
  `entity_scope_calibration_diagnostics`, or the artifact at the top-level
  `uncertainty_calibration_path`), compute
  `calibrated_sigma = alpha*sigma_pi_trace + beta*effective_dof` per event
  (`effective_dof = max(entity_count-1,1)`; entity_count may be None -> fall back
  to 1, and SAY SO in output). Report a per-phase (quali / race / race_start)
  summary of `mean(calibrated_sigma)` vs `mean(realized error)` and their ratio.
- "too flat": report per-phase `CV(calibrated_sigma)` vs `CV(realized error)`.
- Verdict line: is race_start calibrated-sigma mis-leveled (too high and/or too
  flat) RELATIVE to quali/race — or is it already coverage-aligned? State which.

Emit a single compact stdout table + verdicts, and also write a machine-readable
copy to `.agent-work/evo-prediction-ceiling/evidence/g1_evidence.json`.

## Protected Intent
This gate only MEASURES. Its numbers set G2's threshold and decide whether G3 is a
real re-level or a confirm-only no-op. It must be statistically honest — do not
manufacture a "mis-level" verdict the numbers don't support.

## Test Mode
inspection-only — this is an analysis harness, not shipped src. A `--selftest`
flag that checks `r_crit`/Fisher-z on a known case is welcome but optional.

## Close Criteria
- `py .agent-work/evo-prediction-ceiling/evidence/sigma_significance_probe.py`
  exits 0 and prints the table + verdicts.
- Reports per race_start module: `sigma_corr`, 95% CI (bootstrap + Fisher-z),
  p-value, significance verdict.
- Prints `r_crit(n=24, alpha=0.05)` (expected ~0.40) as the proposed G2 threshold.
- Prints the per-phase level/flatness summary and an explicit race-start
  mis-level-vs-coverage-aligned verdict.
- `g1_evidence.json` written.

## Allowed Scope
- Create files ONLY under `.agent-work/evo-prediction-ceiling/evidence/`.
- Read-only: `reports/evo/*.json`, and the calibration artifact path it names.

## Specific Exclusions
- NO changes under `src/` or `tests/` or `docs/`.
- No torch, no FastF1/live calls, no gold cycle, no DB writes.

## Constraints
- `py` for python (Windows launcher).
- Statistically defensible: a correlation CI at n=24 via bootstrap AND Fisher-z;
  do not hand-wave significance.
- Pure stdlib + numpy/scipy if available; degrade gracefully (Fisher-z needs only
  math; bootstrap needs only random+statistics) — do NOT add new deps.
- Deterministic bootstrap (seed it) so the harness re-runs identically.

## Required Evidence
Paste into IMPLEMENTER_RESULT: the full stdout table, the `r_crit(n)` value, the
four race_start `sigma_corr` CIs + verdicts, and the race-start level verdict.

## Verification Commands
```bash
py .agent-work/evo-prediction-ceiling/evidence/sigma_significance_probe.py
```

## Suggested Model Tier
stronger — reason: statistical-methodology correctness (small-n correlation CI,
coverage definition) is the whole value of this gate.

## Authority
Decided already (by the human): Path 1 (level + honest flag), offline done-bar.
You must NOT: redefine the bounded issue, touch src/tests/docs, or assert a
mis-level the data doesn't show. If the data says race-start level is fine, REPORT
THAT — it is a valid, expected outcome.

## Stop Conditions
Stop and return if: the details.json lacks the needed fields, the calibration
artifact can't be located for the level computation, allowed scope must be
exceeded, or producing a defensible CI is not possible with available libs.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files created, evidence (full table +
the four CIs + r_crit + level verdict), assumptions (e.g., entity_count=None
fallback), stop conditions hit, out-of-scope observations.
