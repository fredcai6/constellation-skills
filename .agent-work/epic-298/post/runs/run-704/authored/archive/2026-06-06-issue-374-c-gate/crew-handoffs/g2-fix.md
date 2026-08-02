# Implementer Handoff — G2 FIX: two failing tests in metalearner.py

## Gate
`g2` (rework of an existing, unreviewed G2 implementation)

## Context
`scripts/fusion_replay/metalearner.py` (818 lines) already implements G1 (data-builder, APPROVED) and G2 (Model1, Model2a, Model2b, LOSO, bootstrap, #140 probe, CLI). G1 is verified. The G2 layer is UNREVIEWED and has **exactly 2 failing unit tests**. Your job: fix BOTH so the whole file is green, WITHOUT weakening the tests and WITHOUT changing the decision-rule semantics. Do NOT touch the data-builder or `src/evo_predictor/`.

Current state:
```
py -m pytest tests/unit/evo_predictor/test_metalearner.py -q
26 passed, 2 failed
FAILED ...::TestAntisymmetry::test_model2b_antisymmetry
FAILED ...::TestBootstrapCi::test_bootstrap_resamples_events_not_pairs
```

## Test Mode
The failing tests ARE the spec. Make them pass by fixing the implementation, not by editing the tests. (You MAY only touch a test if you find it is provably wrong — if so, STOP and explain in your return; do not silently weaken it.)

## BUG 1 — Model2b antisymmetry broken by mean-subtraction standardization
`_OddMLP.forward` = `g(x) − g(−x)` is mathematically odd, so `logit(−x) = −logit(x)` and `P(i>j)+P(j>i)=1` MUST hold exactly. But `_fit_mlp`/`_predict_mlp` standardize inputs with **mean subtraction**: `Xn = (X − x_mean) / x_std`. That shift is NOT odd: `predict(-x)` feeds `(−x − mean)/std`, while `−predict(x)` needs `−(x − mean)/std = (−x + mean)/std`. The `2·mean/std` discrepancy breaks oddness (observed atol ~0.005, test wants 1e-5).

**Root-cause fix (Commander-decided):** use **scale-only** standardization for the odd MLP — divide by `x_std`, do NOT subtract a mean. Rationale: Δpi is intrinsically centered at zero (a pair and its mirror are ±Δpi; the population mean over symmetric pairs is 0). Subtracting the i<j-only empirical mean is exactly what injects the antisymmetry-breaking shift. Scale-only normalization preserves oddness (`(−x)/std = −(x/std)`) AND keeps training stable. Apply consistently in both `_fit_mlp` (store only `x_std`, set mean to 0 or drop it) and `_predict_mlp`. Update the docstring to state scale-only is required for odd-construction integrity.

After the fix, `test_model2b_antisymmetry` must pass to atol=1e-5 (it will actually be ~machine-precision since oddness becomes exact up to float32). Verify the MLP still trains (loss decreases) on the fixture.

## BUG 2 — Event-bootstrap does not capture between-event variance
`test_bootstrap_resamples_events_not_pairs` builds data where inter-event gap variance dominates (event_gap ~ N(0,2), within-event noise ~0.05) and asserts the **5-event** CI is WIDER than the **100-event** CI (both have 500 pairs). It currently fails (~equal widths: 0.052 vs 0.054).

Root cause: `_bootstrap_gap_ci` pools all pairs from resampled events and takes `np.mean(gap_per_pair[all_idx])` — a **pair-count-weighted** mean. When every event has many pairs (100 each in the 5-event case), averaging within each resampled event collapses that event's contribution toward its event-mean, and the pooled mean over a pair-weighted concatenation does not reflect event-resampling variance as cleanly as it should; with equal pairs-per-event the between-event signal is diluted.

**Root-cause fix (Commander-decided):** make the bootstrap statistic the **mean of per-event mean-gaps** (equal weight per event), computed on the RESAMPLED multiset of events. Concretely: precompute `event_mean_gap[ev] = mean(gap_per_pair over that event's pairs)`; on each draw, sample `n_events` events with replacement and take `boot_gap = mean(event_mean_gap[sampled])`. This is the standard cluster/event bootstrap for a per-event metric: each resampled event contributes its event-level mean once, so CI width scales correctly with the NUMBER of events (5 events → few distinct cluster means per draw → high variance → wide CI; 100 events → low variance → narrow CI). 
- The POINT estimate Δ_gap reported elsewhere should remain consistent with how the gate defines it. Check whether the point estimate is the pair-weighted pooled mean or the event-mean-of-means; the CI should be computed around the SAME statistic it brackets. If the rest of the code reports pair-pooled Δ_gap as the point estimate, switch the point estimate to the event-mean-of-means too (so `test_ci_brackets_point_estimate` still holds and the reported gap and its CI are the same quantity). Document the chosen statistic in the docstring and in the JSON `meta`.
- `test_ci_brackets_point_estimate` must STILL pass after the change (it computes its own pair-pooled gap_point with B=500 — verify the CI still brackets it; if you move to event-mean-of-means and that test's hardcoded pair-pooled gap_point falls outside, the test itself encodes the pair-pooled definition: in that case keep BOTH — report event-mean-of-means CI for the gate, but ensure the bracketing invariant holds; the cleanest path is event-mean-of-means for BOTH point and CI and confirm `test_ci_brackets_point_estimate`'s gap_point (which for ~equal pairs-per-event ≈ event-mean) still lands inside. RUN it and confirm.)

If reconciling the two bootstrap tests forces a genuine definitional choice, PREFER the event-mean-of-means (statistically correct cluster bootstrap), confirm both tests pass, and document it. If one test cannot pass without weakening it, STOP and surface the tension — do not weaken silently.

## Close Criteria
- `py -m pytest tests/unit/evo_predictor/test_metalearner.py -q` → **ALL GREEN** (28 passed, 0 failed), output pasted.
- Both fixes are root-cause (scale-only standardization; event-mean-of-means bootstrap), documented in code docstrings.
- The CLI still runs end-to-end on one task with `--bootstrap 50` (paste the JSON shape).
- No changes to the data-builder, the decision-rule thresholds, or `src/evo_predictor/`.

## Allowed Scope
- EDIT: `scripts/fusion_replay/metalearner.py`
- EDIT: `tests/unit/evo_predictor/test_metalearner.py` ONLY if a test is provably wrong (STOP + explain first).

## Specific Exclusions
- NO `src/evo_predictor/` changes. NO sklearn. NO new record generation.
- Do NOT change Model1/Model2a definitions, LOSO grouping, target, or decision-rule thresholds.
- Do NOT weaken either failing test to make it pass.

## Constraints
- `py` not `python`; tests `py -m pytest`.
- `$env:PYTHONIOENCODING='utf-8'` (PowerShell) before any captured python subprocess.
- torch CPU; keep MLP seeded/reproducible.
- DB read-only at `C:/Programs/f1Brainz/data`. Records at `outputs/evo_runs/issue-374-records`.

## Required Evidence
- Full `py -m pytest tests/unit/evo_predictor/test_metalearner.py -q` output (must show 28 passed).
- A diff summary (which functions changed) and the updated docstrings for the two fixed areas.
- A `--bootstrap 50` smoke run on one task showing the JSON is produced.

## Verification Commands (PowerShell)
```powershell
Set-Location C:/Programs/f1Brainz/.claude/worktrees/agent-ade67b306f11aa4fb
$env:PYTHONIOENCODING='utf-8'
py -m pytest tests/unit/evo_predictor/test_metalearner.py -q
py -m scripts.fusion_replay.metalearner --records-dir outputs/evo_runs/issue-374-records --out outputs/evo_runs/_smoke.json --bootstrap 50 --seed 0
```

## Suggested Model Tier
strongest — both fixes touch the statistical correctness of the gate (antisymmetry of a core model; the CI that the τ_signif decision rule depends on). A wrong fix produces a wrong epic verdict.

## Authority
- The two root-cause diagnoses above are the Commander's; implement them. You decide exact code structure.
- If a diagnosis is wrong on inspection, STOP and explain — do not silently substitute a different approach that weakens a test.

## Stop Conditions
Stop and return if: a fix requires touching `src/evo_predictor/`; the two bootstrap tests encode mutually contradictory definitions that cannot both hold; or making a test pass would require weakening it.

## Return Format
Return IMPLEMENTER_RESULT: what changed (functions + docstrings), full green test output, smoke-run JSON shape, assumptions, any stop conditions hit, out-of-scope observations.
