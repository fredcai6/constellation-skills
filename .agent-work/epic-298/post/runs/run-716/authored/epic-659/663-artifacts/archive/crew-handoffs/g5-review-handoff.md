# Reviewer Handoff

## Gate
g5-implement (reviewing for g5-review) — GATING acceptance gate, issue #663, SECOND of two

## Context
g4 (already APPROVED) found a real-data measured negative: G's curve fit is structurally unidentified on 2023 FP data. g5 tests the same identifiability question synthetically with known ground truth and found a SPLIT result: parameter recovery PASSES (94.4% >= 90%), but SEPARABILITY FAILS (31.9% << 90%, median |correlation|=0.835, and even the estimator's cleanest tested regime — high SNR, full curve bend — only reaches median |corr|=0.939). This independently confirms g4's diagnosis with a controlled experiment. Both GATING gates for issue #663 now point at the same defect: G's saturating-curve parameterization aliases offset against asymptote on realistic F1 session shapes.

## What Was Implemented
`tests/unit/physics/layer2/test_grip_synthetic_recovery.py`: 72 replicates over a 6-cell SNR x curve-bend factorial, injecting known curve+offset into synthetic field-pooled pace, calling `fit_grip_baseline_from_laps` (g2's real function) directly, scoring recovery (predictive_t 2-sigma coverage) and separability (`|curve_offset_correlation| < 0.8`).

## How to Inspect the Diff
```bash
cd /c/Programs/f1brainz-wt/epic659-663
git status --porcelain
```
New file, untracked. Read directly.

## Task Statement
Build the synthetic-recovery GATING harness per the frozen decision. As with g4, this is NOT a rubber-stamp — verify the harness is sound before accepting either the PASS or the FAIL half of the split result.

## Close Criteria — scrutinize each
1. **Real fit genuinely called, not reimplemented:** grep for the import of `fit_grip_baseline_from_laps` and confirm it's called with synthetic data, not a hand-rolled fit routine standing in for it.
2. **Synthetic data realism:** the implementer used a 3-tier SNR sweep (5.0/1.0/0.14) claiming the lowest (0.14) matches real 2023 field-pooled residual scale (~15s) vs curve amplitude (~1.5s) — spot-check this claim by fitting ONE real 2023 session yourself and comparing residual scale to what the harness assumes. If the "realistic" SNR tier is actually unrealistic (too easy or too hard), the separability failure's real-world relevance is undermined either way — confirm it's calibrated honestly.
3. **`predictive_t` exact call:** verify the cited call (`predictive_t(mu_hat, sigma_reported, n_eff=n_stints_used, nu_loss=DEFAULT_NU_LOSS, rule=FormulaRule()).interval(0.9545)`) actually appears in the source and computes a genuine 2-sigma-equivalent interval — confirm `0.9545` is the correct two-sided coverage level for "2-sigma" (it is, for a normal — for a Student-t with the interval widened by `predictive_t`'s epistemic inflation, confirm this is still the intended reading, or if a different level should have been used, and whether that would move the reported 94.4% recovery rate materially).
4. **Recovery-passes-only-via-sigma-widening claim:** the implementer explicitly flags that recovery only clears 90% because low-SNR replicates get wide sigmas (trivial coverage), and that the ONE high-confidence regime (highSNR/modBend) drops to 66.7% — verify this by reading the per-regime table in the pasted evidence; if true, this materially qualifies what "recovery PASSES" actually means for a reviewer/commander deciding the overall verdict (a passing rate driven by honest uncertainty-inflation is a different finding than a passing rate driven by genuinely tight, accurate estimates).
5. **Honest-null operationalization:** read every `assert` in the test file, confirm NONE encodes `recovery_rate >= 0.90` or `separability_rate >= 0.90` as a pytest pass/fail condition — only harness-validity assertions (replicate count, finite values, regime variety, fraction of "ok"-status fits).
6. **The `decision:synthetic-criterion` "guess"-graded adjustment:** the implementer states they evaluated the frozen 0.8 threshold and judged it well-calibrated (kept unchanged, self-regraded to `settled/measured`) — confirm this reasoning is genuinely recorded (not just asserted) and is a defensible read of the data (does 0.8 actually look like a reasonable identifiability bar given where the correlation distribution sits?).
7. **Diagnostic depth:** confirm the per-regime breakdown and correlation histogram in the pasted evidence are real, reproducible outputs (re-run and compare), not hand-summarized after the fact.

## Allowed Scope
New file only.

## Specific Exclusions
Do not modify `grip_baseline.py` even if you believe the identifiability defect needs fixing — that decision belongs to the commander/g6, not this review.

## Constraints the Implementation Must Respect
Real-fit-not-reimplemented, honest-null operationalization, frozen replicate count/thresholds (or a recorded, defensible adjustment).

## Map Anchors (inbound)
`decision:synthetic-identifiability` @grade: settled/human; `decision:synthetic-criterion` @grade: guess (implementer proposes regrading to settled/measured — confirm or contest this).

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/663-grip-g/crew-handoffs/g5-implement-result.md`, results artifact at `.agent-work/663-grip-g/g5-synthetic-results.json`. Use `"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe"` for every command, `-q -s` to see diagnostics.

## Suggested Model Tier
Stronger — reason: second GATING gate, confirms a significant cross-gate finding, requires judging both a harness's soundness AND a scientific-calibration claim (the SNR realism check).

## Stop Conditions
Stop and return BLOCK if: the fit is reimplemented rather than reused, the harness's "realistic SNR" claim doesn't survive a real-session spot-check, any assertion secretly encodes a rate threshold, or the diagnostic numbers don't reproduce.

## Return Format
Return REVIEW_RESULT (write to `.agent-work/663-grip-g/crew-handoffs/g5-review-result.md`, and return as final message text): verdict (APPROVE or BLOCK), per-check findings for each of the 7 close criteria, your independent read on whether this split result (recovery-passes-hollowly / separability-fails) is a sound, real finding, blockers, out-of-scope observations, workflow feedback.
