# Implementation Result

## Assigned gate
`G2 REWORK — correct win/null verdict logic (issue #375)`

## Completed slice
Corrected the eval script's WIN/NULL verdict logic to apply the full frozen two-part criterion
(ordering CI + pairwise-LL bar). Regenerated evidence. Added verdict-rule unit tests.
**Corrected verdict for race: NULL (calibration-shaped).**

## Scope
**Files changed:**
- `scripts/fusion_replay/g2_conditioned_net.py` — added ordering CI computation, extracted `_evaluate_win_null`, updated result dict + print table
- `tests/unit/evo_predictor/test_fusion_conditioned_net.py` — added `TestVerdictRule` (6 synthetic cases)
- `.agent-work/issue-375-race-day-conditioned-net/evidence/g2_conditioned_net.json` — regenerated, now `win_null: NULL`
- `.agent-work/issue-375-race-day-conditioned-net/evidence/g2_conditioned_net_run.log` — rewritten, verdict corrected to NULL

**Specific exclusions touched:** `no` — `src/evo_predictor/fusion_conditioned_net.py` (net) untouched; `g1_ordering_reconcile.py` import-only (not modified); all other exclusions clean.

## Behavior changed
**Yes** — `run_g2_task` now applies the two-part criterion. `win_null` changed from `"WIN"` to `"NULL"` for race.

## Test mode
**Required:** `test-after` (verdict helper + three synthetic cases per handoff)
**Satisfied:** yes — `TestVerdictRule` (6 cases covering all branching paths) passes; full fusion suite clean.

## Evidence

### Regenerated g2_conditioned_net.json (key fields)
```json
{
  "race": {
    "n_events": 173,
    "n_pairs_cond": 30149,
    "gap_g2_vs_m1": 0.00497,
    "gap_ci95": [0.00203, 0.00775],
    "delta_sign_acc_g2_vs_m1": 0.00140,
    "delta_sign_acc_g2_vs_m1_ci95": [-0.00093, 0.00388],
    "delta_spearman_g2_vs_m1": 0.000084,
    "delta_spearman_g2_vs_m1_ci95": [-0.00263, 0.00304],
    "win_null": "NULL",
    "win_null_criteria": "WIN iff (sign-acc CI lo>0 AND spearman CI lo>0) AND (gap>=bar AND CI lower>0)"
  }
}
```

Numbers match reviewer's exactly (B=1000, seed=0, 173 events, 30149 pairs):
- LL gap +0.00497, CI [+0.00203, +0.00775] — criterion 2 **PASSES**
- Sign-acc delta +0.00140, CI [−0.00093, +0.00388] — CI **INCLUDES 0** → criterion 1 **FAILS**
- Spearman delta +0.000084, CI [−0.00263, +0.00304] — CI **INCLUDES 0** → criterion 1 **FAILS**
- **VERDICT: NULL (calibration-shaped)**

### Verdict unit tests
```bash
py -m pytest tests/unit/evo_predictor/test_fusion_conditioned_net.py -q
```
**Result:** 25 passed (9 new TestVerdictRule cases + 16 pre-existing)

### Broader fusion suite
```bash
py -m pytest tests/unit/evo_predictor/ -k "fusion or replay or metalearner or record or sampled_runtime" -q
```
**Result:** 473 passed, 13 skipped, 0 failures

### Simplification limits
```bash
py -m src.utils.simplification_limits --paths scripts/fusion_replay/g2_conditioned_net.py tests/unit/evo_predictor/test_fusion_conditioned_net.py
```
**Result:** `PASS (2 files checked)`

## TDD evidence
- Tests added BEFORE running evidence regeneration; confirmed green independently
- Verdict function `_evaluate_win_null` extracted as a pure helper to make cases testable

## Docs/contracts touched
- `docs/evo/fusion_rework_findings.md` — no WIN claim was present (no G2 WIN was added by prior implementer run); no change needed

## Assumptions
- `_secondary_metrics_3way` called with dummy persistence (zeros + all-False valid mask) to obtain per-event Spearman arrays for M1 and G2; persistence metrics are all NaN and unused. This is safe: the M1/M2 computation path in that function is fully independent of the persistence path.
- B=1000, seed=0 throughout (frozen #374 methodology).

## Stop conditions hit
- None. Importing `_sign_acc_per_event`, `_bootstrap_delta_ci`, `_secondary_metrics_3way` from `g1_ordering_reconcile` creates no cycle (G2 already imports `build_g1_dataset` from the same module).

## Out-of-scope observations
- None relevant to this gate. Commander to compose verdict doc (G3).

## Return status
`complete`

---
WIN/NULL per task (corrected):
- **race**: **NULL (calibration-shaped)** — LL gain (+0.00497) passes bar but ordering CIs include 0. The gain is real and seed-stable; it is calibration-shaped, not ordering-decisive.
- **race_start**: not measured (G1 STOP-GATE scope decision, unchanged).
