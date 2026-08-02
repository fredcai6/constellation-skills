---
evidence_type: review-result
verdict: APPROVE
gate: g1
task: g1-review
reviewer: constellation-reviewer
date: 2026-06-06
---

# REVIEW_RESULT — G1: meta-learner data-builder

## Verdict: APPROVE

All 7 close criteria independently verified. No blockers. One out-of-scope observation.

---

## Per-Check Findings

### C1 — Harness reuse, no reimplementation: PASS
Read `metalearner.py` in full (208 lines). Imports confirmed:
```python
from scripts.fusion_replay.scorecard import (
    _align_driver_pi, _build_module_field_results, _load_module_events,
    _module_meta_for_task, _preprocess_events, canonicalize_and_join,
)
from src.evo_predictor.constructor_projection import project_constructor_field_to_drivers
from src.evo_predictor.fusion_training._calibration import module_names_for_task
```
All 6 required functions are both imported and called in `build_pairwise_dataset`. No reimplementation of canonical join, constructor-lineage normaliser, constructor→driver projection, or driver pi alignment was found.

### C2 — Alignment mirrors `_compute_event_residuals`: PASS
The metalearner uses `break` + `skip_event = True` when any column fails (whole-event skip), while `_compute_event_residuals` uses `continue` per module. The spec explicitly requires whole-event skip for the M-matrix use case ("if ANY column returns None / raises ValueError, the WHOLE event is skipped"). The guard `if skip_event or len(cols) != 4` correctly catches both conditions. On real data: 0 alignment skips (173/173 prepped events used), confirming harness lineage/projection is working correctly.

### C3 — Pairwise label + antisymmetry: PASS
Independent verification on event `2018:10:Great Britain:quali` (20 drivers):
- `triu_indices(20, k=1)` produces 190 pairs; all satisfy i<j. ✓
- y independently computed as `(pos_i < pos_j)` — matches builder output. ✓
- Antisymmetry: constructed mirror row (j,i) for pair (0,1): `X_delta_mirror = M[j]-M[i] = -X_delta_ij` confirmed to 1e-9; `dev_delta_mirror = -dev_delta_ij` confirmed to 1e-9; `y_mirror = 1 - y_ij` confirmed. ✓
- Exactly one of each unordered pair emitted (no duplicate pairs possible by `triu_indices` construction). ✓

### C4 — Deviation feature = weekend − recent per scope: PASS
Independent recompute for event `2018:10:Great Britain:quali`, pair (driver_idx=0, driver_idx=1):
- `ctor_dev = M[:,2] - M[:,0]` = constructor_weekend − constructor_recent
- `drv_dev = M[:,3] - M[:,1]` = driver_weekend − driver_recent
- `ctor_dev_delta` = 0.477867290378; builder `dev_delta[0,0]` = 0.477867290378 — match to 1e-9. ✓
- `drv_dev_delta` = 0.138070788234; builder `dev_delta[0,1]` = 0.138070788234 — match to 1e-9. ✓

### C5 — Season groups present and correct: PASS
Checked all 31,926 rows. `seasons` vs year-prefix of `event_ids`: 0 mismatches.

### C6 — Coverage on quali ≈ 173 events: PASS
**Builder result**: `n_events_used=173`, `n_pairs=31926`, `n_events_skipped_alignment=0`, `n_events_skipped_no_valid_pairs=0`. Per-season: {2018:21, 2019:21, 2020:17, 2021:22, 2022:22, 2023:22, 2024:24, 2025:24}.

**Independent re-derive**: loaded 4 quali modules via `_load_module_events`, joined via `canonicalize_and_join` (0 join skips), preprocessed via `_preprocess_events` → **173 prepped events** (0 skipped_lt3_drivers). Reconstructed from builder: 173+0+0=173. ✓ The builder's n_events_used matches the prepped count exactly, confirming 0 alignment skips and no pair-filter dropouts.

### C7 — Tests green on real records: PASS
```
py -m pytest tests/unit/evo_predictor/test_metalearner.py -q
12 passed, 1 skipped in 1.01s
```
All 11 TestQualiDataset tests pass. `race_start` now also passes (all 4 modules generated since the implement run). `race` is still skipped — the skip is data-driven by `_has_all_modules(task)` checking actual file presence in the records directory, not an unconditional `@pytest.mark.skip`. ✓

---

## Blockers
None.

---

## Out-of-Scope Observations

**OBS-1 (Triage candidate)**: Test count advanced from implementer's 11/2 to 12/1 because `race_start` module files finished generating between implement and review. No concern — the skip guard is correctly data-driven. The G2 step should expect `race_start` data to be available.

**OBS-2 (Triage candidate)**: `len(cols) != 4` in the skip guard (`if skip_event or len(cols) != 4`) is redundant given that `skip_event = True` is always set before `break`. Harmless defense-in-depth.

---

## Scope Verification
- `git status --short`: only `scripts/fusion_replay/metalearner.py` and `tests/unit/evo_predictor/test_metalearner.py` are untracked (new). No `src/evo_predictor/` changes. ✓
- No sklearn, torch, scipy.optimize, LOSO, or bootstrap code in `metalearner.py`. Data-builder only. ✓
