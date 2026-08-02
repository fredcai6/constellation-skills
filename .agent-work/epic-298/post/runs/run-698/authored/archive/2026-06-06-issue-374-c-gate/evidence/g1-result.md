## G1 Implementer Evidence — metalearner.py data-builder

### Test run (py -m pytest tests/unit/evo_predictor/test_metalearner.py -q)

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1Brainz\.claude\worktrees\agent-ade67b306f11aa4fb
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, mock-3.15.1
collected 13 items

tests/unit/evo_predictor/test_metalearner.py ...........ss               [100%]

======================== 11 passed, 2 skipped in 0.59s ========================
```

- 11 TestQualiDataset tests PASSED (real records, real DB)
- 2 race_start/race tests SKIPPED — not all 4 modules generated yet (expected)

### Coverage summary

#### quali (fully generated — Commander baseline)
```
n_events_used: 173
n_pairs: 31926
n_events_skipped_alignment: 0
n_events_skipped_no_valid_pairs: 0
per_season_event_counts: {2018: 21, 2019: 21, 2020: 17, 2021: 22, 2022: 22, 2023: 22, 2024: 24, 2025: 24}
X_delta shape: (31926, 4)
y mean (frac i ahead): 0.4847
```
n_events_used=173 exactly matches Commander-verified #373 baseline. 0 alignment skips.

#### race_start (still generating — driver_race_start_power_from_race_weekend has 1 of 8 seasons)
Test skipped: not all 4 modules generated yet.

#### race (still generating — 0 season files for all 4 modules)
Test skipped: not all 4 modules generated yet.

### Files created
- scripts/fusion_replay/metalearner.py (new)
- tests/unit/evo_predictor/test_metalearner.py (new)

### Reuse evidence
- `_module_meta_for_task`, `_load_module_events`, `canonicalize_and_join`,
  `_preprocess_events`, `_build_module_field_results`, `_align_driver_pi` all
  imported from scripts.fusion_replay.scorecard — no reimplementation
- `project_constructor_field_to_drivers` from src.evo_predictor.constructor_projection
- `module_names_for_task` from src.evo_predictor.fusion_training._calibration
- No src/evo_predictor/ changes (frozen)
- No sklearn
