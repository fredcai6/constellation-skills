# REVIEW_RESULT — G2 BUILD (issue #375): conditioned net + offline measurement

## Assigned Gate
`g2 BUILD — WIN/NULL verdict for ConditionedOrderingHead on race`

## Result
**BLOCK**

---

## Handoff compliance
**FAIL.** All code artifacts were delivered (ConditionedOrderingHead, ConditionedUncertaintyHead,
encode_prior_pos_delta, g2_conditioned_net.py, 19 unit tests, evidence JSON). The blocker is the
win_null verdict logic in `run_g2_task` (line 451): it applies **criterion 2 only**
(`gap >= 0.00364 AND CI_lo > 0`). The handoff's FROZEN SUCCESS BAR requires a **two-part
criterion**: criterion 1 (sign-accuracy CI vs Model1 AND Spearman CI vs Model1 both excluding 0)
is decisive; an LL win without an ordering win is a NULL. The evidence JSON records `"WIN"`;
the correctly-applied verdict is **NULL**.

## Scope drift
**PASS.** Excluded files untouched (git diff empty for `quali_pace_anchor.py`,
`sampled_runtime.py`, `prediction_ceiling_and_priorities.md`). `race_start` ordering correctly
excluded from the ordering head scope. `g1_ordering_reconcile.py` analysis behaviour unchanged.
Records not regenerated.

## Evidence verdict
**FAIL.** `g2_conditioned_net.json` is present and contains the LL gap, bootstrap CI (criterion 2),
and point estimates for Spearman/rank-MAE. **Missing:** sign-accuracy delta vs Model1 and its CI;
Spearman delta CI vs Model1. The ordering-metric bootstrap CIs required to apply criterion 1 were
never computed and are absent from the evidence.

## Code/doc quality
**PASS.** `ConditionedOrderingHead.forward` returns `g(x) − g(−x)` — antisymmetry exact by
construction, confirmed by 5 dedicated tests. Scale-only normalisation (divide by std, no centering)
preserves the odd-function property. `encode_prior_pos_delta` returns `(pj−pi)/max_pos` —
antisymmetric under swap by definition; tested (antisymmetry, normalization range, NaN propagation,
output shape). Head separation: separate module instances, no shared parameters, tested by id()
intersection and mutation test. `_fit_conditioned_ordering_head` uses a seeded shuffle generator
created before the epoch loop (correct — avoids the #374 in-run-fix bug). `simplification_limits`
passes on both touched files.

## Reconciliation check
**PASS.** New files land in correct locations. No production wiring added (G3 correctly excluded).
Architecture index may need updating for G2 deliverables — normal Commander housekeeping.

---

## INDEPENDENTLY RE-DERIVED NUMBERS (the load-bearing section)

**Setup:** B=1000, seed=0, 173 events, 30149 pairs (0 dropped — lap-3 covers all drivers).

| Metric | Model1 | G2 | Delta | 95% CI | CI excl 0? |
|---|---|---|---|---|---|
| Pairwise LL | 0.47736 | 0.47214 | +0.00497 | [+0.00203, +0.00775] | **YES** |
| Sign-accuracy | 0.78811 | 0.78952 | +0.00140 | [−0.00093, +0.00388] | **NO** |
| Spearman | 0.70568 | 0.70576 | +0.00008 | [−0.00263, +0.00304] | **NO** |
| Rank MAE | 2.90659 | 2.89502 | −0.01158 | (not a criterion) | — |

**Fair-ceiling check:** Reviewer LOSO reproduced Model1 = 0.47736 exactly (matches implementer).
Pair population: n_pairs_cond = n_pairs_total = 30149 (identical, fair comparison).
Spearman delta matches implementer's reported point estimate exactly (+0.0000840).

### Two-part criterion applied mechanically

- **Criterion 1** (ordering win, decisive): sign-acc CI [−0.00093, +0.00388] **includes 0**;
  Spearman CI [−0.00263, +0.00304] **includes 0**. → **FAILS**
- **Criterion 2** (LL bar): gap +0.00497 ≥ 0.00364, CI_lo +0.00203 > 0. → **PASSES**

> **CORRECT VERDICT: NULL (calibration-shaped, consistent with G1)**

The +0.00497pp pairwise-LL gain is real and CI-confirmed. It is **calibration-shaped**: the
conditioned net sharpens probabilities without materially reordering drivers vs the linear pool.
This is the exact same pattern G1 found for race: Model2b was flat vs Model1 on all three ordering
metrics (sign-acc delta −0.00037 CI [−0.00210, +0.00139]; Spearman delta −0.00024 CI [−0.00217,
+0.00150]). G2's conditioned net with the prior_pos_delta feature adds calibration but still does
not move ordering over Model1.

### Uncertainty head measurement
Honestly stated in the evidence as pending (#408 spread_target plumbing). This does not affect
the ordering-head verdict.

---

## Blockers
- **BLOCKER 1:** `win_null` in `g2_conditioned_net.py:run_g2_task` must be corrected to apply
  the two-part criterion. Current logic: `gap >= bar AND ci_lo > 0` (criterion 2 only). Required:
  also compute per-event sign-accuracy and Spearman CIs vs Model1 (reuse
  `_sign_acc_per_event` + `_bootstrap_delta_ci` + `_secondary_metrics_3way` from
  `g1_ordering_reconcile.py`), then set `win_null = "WIN"` only if BOTH criteria pass.
- **BLOCKER 2:** `evidence/g2_conditioned_net.json` must be regenerated after the above fix to
  record the correct verdict (NULL) and the ordering-metric CIs.
- **BLOCKER 3:** The PR must **not** say "Closes #375" and G3 production wiring must **not** ship.
  The correct framing: G2 measured a calibration-shaped gain; a bespoke ordering net does not add
  material ordering over the linear pool at the module-output layer with current features.

## Out-of-scope observations
- The calibration gain (+0.00497pp LL) is genuine and repeatable (seed-stable). If the project
  later pursues a calibration-only net for race (analogous to the race_start calibration head
  discussed in G1 scope notes), G2's measured numbers provide a solid baseline. Triage candidate
  for Commander.
- `g1_ordering_reconcile.py` already contains all helper functions needed to fix blocker 1
  (`_sign_acc_per_event`, `_bootstrap_delta_ci`, `_secondary_metrics_3way`). The fix is an
  import + ~15 lines in `run_g2_task`.

## Return status
`blocked`
