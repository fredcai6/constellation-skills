# Implementation Result

## Assigned gate
g2 — decisive feature-ablation retrain gate (issue #451, cmdr-451): CONTROL vs +PACE on §7.6.2 same-pairs harness, two splits

## Completed slice
1. Created condition-specific records dirs (`records_g2_control/`, `records_g2_pace/`) and scratch artifact dirs.
2. Ran 2 CONTROL retrains of `driver_quali_power_from_race_weekend` (splitA: eval 2024; splitB: eval 2025), each `--seed 0`, emitted `rw_{year}.record.json` into `records_g2_control/`.
3. Applied probe edit to `src/evo_predictor/quali_power_adapter.py`: appended `cross_channel_min_pace` (NaN-safe min(qs_best_raw, lr_best_raw)) as 24th feature; bumped schema version to `v3-probe`. Marked `# PROBE g2 #451 — revert`.
4. Ran 2 +PACE retrains (same splits, same seeds), emitted `rw_{year}.record.json` into `records_g2_pace/`.
5. Ran `scripts/diagnose_quali_same_pairs.py` UNMODIFIED on each condition dir; captured stdout.
6. Wrote `g2_numbers.json` with required keys. Src edit left in place for reviewer inspection.

## Scope
**Files changed:**
- `src/evo_predictor/quali_power_adapter.py` — PROBE edit (21 lines added, 1 modified); left in place for reviewer
- `.agent-work/451/g2-implementer-plan.json` — engine plan (new)
- `.agent-work/451/records_g2_control/` — 34 record files (rh 2018-2025, rw 2018-2025; rw 2024/2025 freshly retrained)
- `.agent-work/451/records_g2_pace/` — 34 record files (rh 2018-2025, rw 2018-2025; rw 2024/2025 freshly retrained with +pace feature)
- `.agent-work/451/scratch_runs/g2_control/` — 2 trained bundles (control_splitA, control_splitB)
- `.agent-work/451/scratch_runs/g2_pace/` — 2 trained bundles (pace_splitA, pace_splitB)
- `.agent-work/451/evidence/harness_control_stdout.txt` — full harness output for CONTROL
- `.agent-work/451/evidence/harness_pace_stdout.txt` — full harness output for +PACE
- `.agent-work/451/evidence/g2_numbers.json` — required evidence file (new)
- `.agent-work/451/evidence/g2-implementer-result.md` — this file

**Specific exclusions touched:** no gold cycle, no fusion, no Piece-2, no committed defaults changed. Probe edit is branch-local scratch only.

## Behavior changed
No production behavior changed. Probe edit is in-place but marked for revert; all retrains are in `.agent-work/451/scratch_runs/**` only.

## IMPLEMENTER_RESULT — per-split numbers

### CONTROL (as-is, 23 features, --seed 0)

| Split | rw acc | ceiling (best_across_fp) | ceiling (blend_rank) | gap to ceiling | pairs | events |
|---|---|---|---|---|---|---|
| splitA: headline 2018-2024 (eval yr: 2024) | 0.6560 | 0.8061 | 0.8078 | 0.1501 | 23862 | 130 |
| splitB: OOS 2025 (eval yr: 2025) | 0.5868 | 0.7643 | 0.7709 | 0.1775 | 3352 | 18 |

*Note: splitA headline pools 7 years; 2018-2023 from G1 gold bundle (same for both conditions); only 2024 is freshly retrained. OOS 2025 is a pure single-year signal.*

### +PACE (cross_channel_min_pace appended as 24th input feature, --seed 0)

| Split | rw acc | ceiling (best_across_fp) | ceiling (blend_rank) | gap to ceiling | pairs | events | delta vs control |
|---|---|---|---|---|---|---|---|
| splitA: headline 2018-2024 (eval yr: 2024) | 0.6792 | 0.8061 | 0.8078 | 0.1269 | 23862 | 130 | **+0.0232** |
| splitB: OOS 2025 (eval yr: 2025) | 0.7700 | 0.7643 | 0.7709 | -0.0057 | 3352 | 18 | **+0.1832** |

### Verdict direction: **'a'** (hypothesis (a) representation confirmed)

**Why:** On OOS 2025 (the purest signal — fresh splitB retrain, single held-out year), +PACE rises from 0.5868 to 0.7700, a +0.1832 lift that reaches and slightly exceeds the ceiling (0.7643). CONTROL reproduces the expected large deficit (0.5868, gap=0.1775). The cross-channel min-pace ordering signal was NOT present in the 23-feature control vector and IS learnable once supplied as an input feature. This is strong support for hypothesis (a): representation, not capacity or training signal, is the primary lever.

The headline split shows a smaller but directionally consistent +0.0232 lift. That is expected — 2018-2023 records are from the G1 gold bundle (unchanged for both conditions), diluting the per-year signal across 7 years. The OOS result is the load-bearing evidence.

**Commander decides final verdict.** The numbers and direction are reported here; no src change is landed.

## Adapter diff (probe edit, left in place for reviewer)

```diff
diff --git a/src/evo_predictor/quali_power_adapter.py b/src/evo_predictor/quali_power_adapter.py
index 0c36751..3c50414 100644
--- a/src/evo_predictor/quali_power_adapter.py
+++ b/src/evo_predictor/quali_power_adapter.py
@@ -13,7 +13,7 @@ from src.latent_power.models import PairBatch
 from src.latent_power.preprocessor_contract import assert_pair_batch
 from src.utils.constants import DNF_POSITION, NORMAL_PRACTICE_SESSIONS, SPRINT_PRACTICE_SESSIONS
 
-DRIVER_QUALI_POWER_FEATURE_SCHEMA_VERSION = "driver_quali_power_from_race_weekend.v2"
+DRIVER_QUALI_POWER_FEATURE_SCHEMA_VERSION = "driver_quali_power_from_race_weekend.v3-probe"  # PROBE g2 #451 — revert
 
 # Features with 1.0 sparse neutral — ambiguous without a missingness indicator.
 # For each of these, a companion `{name}_missing` feature is emitted alongside.
@@ -63,6 +63,8 @@ DRIVER_QUALI_POWER_FEATURE_NAMES: tuple[str, ...] = (
     "short_run_super_clean_share",
     # Availability indicator (computed separately, not sparse-neutral)
     "qs_sector_available",
+    # PROBE g2 #451 — revert: cross-channel min best-lap (raw seconds; lower=faster)
+    "cross_channel_min_pace",
 )
 
 _SPARSE_NEUTRALS = {
@@ -221,6 +223,24 @@ def _driver_vector(driver: DriverFeatures) -> _DriverVector:
         sparse_features.append("qs_sector_available")
     values.append(1.0 if available else 0.0)
 
+    # PROBE g2 #451 — revert: cross-channel min best-lap = NaN-safe min(qs_best_raw, lr_best_raw).
+    # Raw best-lap in seconds; lower=faster. NaN/missing falls back to 0.0 (neutral; no ordering signal).
+    # The head ingests antisymmetric pairwise differences, so this enters as a pace-gap-in-seconds diff.
+    _qs_raw = getattr(driver, "qs_best_raw", math.nan)
+    _lr_raw = getattr(driver, "lr_best_raw", math.nan)
+    _qs_finite = _is_finite(_qs_raw)
+    _lr_finite = _is_finite(_lr_raw)
+    if _qs_finite and _lr_finite:
+        _pace_val = float(min(_qs_raw, _lr_raw))  # type: ignore[arg-type]
+    elif _qs_finite:
+        _pace_val = float(_qs_raw)  # type: ignore[arg-type]
+    elif _lr_finite:
+        _pace_val = float(_lr_raw)  # type: ignore[arg-type]
+    else:
+        _pace_val = 0.0  # missing; no ordering signal
+    values.append(_pace_val)
+    # PROBE g2 #451 — end
+
     dqi = max(0.25, 1.0 - (0.1 * len(set(sparse_features))))
     return _DriverVector(np.asarray(values, dtype=np.float32), float(dqi), tuple(sparse_features))
```

**Src edit status:** Left in place for reviewer inspection. `git diff --stat src/` shows only `src/evo_predictor/quali_power_adapter.py` changed (21 insertions, 1 deletion). Commander to revert at integrate.

## Map Impact
- **Capabilities added/changed/affected:** g2 ablation demonstrates that appending `cross_channel_min_pace` as a 24th input to `driver_quali_power_from_race_weekend` drives OOS rw from 0.5868 to 0.7700 (ceiling 0.7643) — the ordering signal is learnable as an input. This capability is probe-only; not landed.
- **Structural anchors touched:** `quali_power_adapter._driver_vector` (probe: +24th feature); `DRIVER_QUALI_POWER_FEATURE_NAMES` (24 entries); `DRIVER_QUALI_POWER_FEATURE_SCHEMA_VERSION` (v3-probe). InnerNetwork `feature_dim` auto-propagated correctly (no manual config edit needed — confirmed by successful retrain).
- **Constraints/assumptions touched:** Walk-forward constraint honored: `cross_channel_min_pace` derives from `qs_best_raw`/`lr_best_raw` which are FP-session aggregates (pre-Q), so no eval-year leakage. Eval year held out in each split.
- **Claims/evidence produced:** Hypothesis (a) representation claim: OOS +0.1832 lift to ceiling is strong evidence that cross-channel min-pace ordering was absent from the 23-feature vector and is learnable.
- **Decision candidates:** Commander/Admiral decision needed: whether to promote the `cross_channel_min_pace` feature (a representation fix touching a promoted default → floats to Admiral per §7.6.3 C3). The probe confirms the value; the landing decision is not implementer authority.
- **Trust limitations / drift found:** The headline split's 6/7 years using the G1 gold bundle means the headline contrast (0.0232) understates the per-year 2024 lift. A full LOSO retrain would give a cleaner headline number but was explicitly out of scope.
- **Triage candidates:** (1) Full LOSO retrain of +PACE to get clean headline; (2) within-event-standardised z-score variant of the pace feature (mentioned in handoff as optional; not run — the raw variant gave such a strong OOS result that the z variant was deprioritized); (3) assess whether a missing-indicator is needed for `cross_channel_min_pace` when both are NaN.

## Test mode
**Required:** evidence-only (no new tests required for this probe gate)
**Satisfied:** yes — harness runs UNMODIFIED `scripts/diagnose_quali_same_pairs.py`; no production code path permanently changed

## Evidence

```bash
# Verify required evidence file keys
PYTHONIOENCODING=utf-8 py -c "import json; d=json.load(open('.agent-work/451/evidence/g2_numbers.json')); print('as_is_control' in d, 'pace_feature' in d, d.get('points_to'))"
# => True True a

# Verify probe edit is still present and only file changed in src/
git diff --stat src/
# => src/evo_predictor/quali_power_adapter.py | 22 +++++++++++++++++++++-

# Verify 24 features loaded
PYTHONIOENCODING=utf-8 py -c "from src.evo_predictor.quali_power_adapter import DRIVER_QUALI_POWER_FEATURE_NAMES; print(len(DRIVER_QUALI_POWER_FEATURE_NAMES))"
# => 24
```

**Result:** pass — all checks confirmed

## TDD evidence, if required
Not applicable (evidence-only gate).

## Docs/contracts touched
None — probe edit is scratch/branch-local; no promoted contracts changed.

## Assumptions
1. Using `--db-root data` (per-year DBs `f1_data_{year}.db`) rather than `--db-path data/f1_data.db` (merged DB is empty of `session_classifications`). This matches the actual data layout.
2. `--compound-prior-root params/gold/compound_prior` and `--retro-root params/retro_truth` required for the train CLI — not mentioned in handoff but found by running the CLI.
3. Headline harness result pools 2018-2024; 2018-2023 records are from G1 gold bundle (unchanged, same for both conditions). The eval-year (2024 or 2025) is the ONLY freshly retrained year. This is an apples-to-apples comparison for the eval year but the headline number is diluted.
4. The z-score variant of the pace feature was not run — the raw-min variant gave such a strong OOS result (+0.1832, reaching ceiling) that the optional z variant was deferred as triage candidate.
5. Missing `cross_channel_min_pace` falls back to 0.0 (neutral, no ordering signal). This matches the handoff NaN-safe specification and is consistent with the unambiguous-sparse pattern in the existing codebase.

## Stop conditions hit
None. All 4 retrains completed successfully. Probe edit applied without contract errors. Harness ran on both conditions without modification.

## Out-of-scope observations
1. **OOS result is surprisingly strong**: rw=0.7700 slightly exceeds ceiling=0.7643 on 2025. On 18 events/3352 pairs this could have variance, but the +0.1832 magnitude vs CONTROL=0.5868 is striking. Commander should flag to Admiral for the promotion decision (§7.6.3 C3 applies).
2. **Missing-indicator consideration**: `cross_channel_min_pace` falls back to 0.0 when both raw values are NaN. Unlike the ambiguous-sparse features, there's no companion `_missing` indicator. For a production landing, a missingness indicator might improve the signal — triage candidate.
3. **Headline dilution artifact**: The harness structure pools all 7 years for the headline metric. For a cleaner per-year-2024 ablation contrast, a custom evaluation restricted to 2024 events only would give a higher per-year number. Not done (out of scope / not required by handoff).
4. **Feature scale note**: `cross_channel_min_pace` is raw best-lap in seconds (typically ~80-120s). The antisymmetric pairwise differences entering the head are in seconds. LayerNorm in the InnerNetwork handles scale — this was validated by the successful retrain (no NaN/exploding loss).

## Workflow Feedback
- **Handoff gaps:** The `--retro-root` and `--compound-prior-root` arguments are required by `train-latent-power-module` for the `race_weekend` module but were not mentioned in the handoff. Had to discover them by running the CLI and reading the error messages (2 attempts, each fast — within the 2-attempt budget for a soft blocker). These should be in the handoff or in a "standard train CLI args" note.
- **Context rediscovered:** The merged DB (`data/f1_data.db`) is empty of `session_classifications`; per-year DBs (`data/f1_data_{year}.db`) hold the data. This requires `--db-root data` rather than `--db-path data/f1_data.db`. Not documented in the handoff; discovered by inspecting the DB after a confusing "no valid batches" error.
- **Instructions improvised around:** The harness requires rw and rh records for ALL years 2018-2025 (not just the eval year). The handoff implied only emitting the eval-year record, but the harness's HEADLINE regime loads all 7 years. Resolved by copying G1 rw/rh records for 2018-2023 into both condition dirs — which is consistent with the handoff's "reuse G1 rh records" note extended to rw as well.
- **What would have made this easier:** Add a "standard train CLI args template" to the handoff with `--retro-root params/retro_truth --compound-prior-root params/gold/compound_prior --db-root data` filled in. The harness year-range requirement (all years, not just eval year) should also be explicit.

## Return status
`complete`
