# Leakage-free, pre-quali fantasy — model vs human (2022-2025)

**The leakage-free model LOSES to the human in all four seasons (by 92-331 pts).**

F1 fantasy season score (sum of |pred_pos-actual| over top-10 picks + bingo bonuses); LOWER is better

| Season | Model | Human | Gap (model-human) | Model/race | Human/race |
|---|--:|--:|--:|--:|--:|
| 2022 | 831 | 739 | **+92** | 37.77 | 33.59 |
| 2023 | 963 | 632 | **+331** | 43.77 | 28.73 |
| 2024 | 835 | 615 | **+220** | 34.79 | 25.62 |
| 2025 | 849 | 711 | **+138** | 35.38 | 29.62 |

Totals — model **3478** vs human **2697** (lower is better).

## Leakage controls

- 2025 model = gold cycle trained on 2018-2024 only (eval 2025 held out); pipeline_validation green.
- 2022-2024 models = leave-one-season-out folds, each EXCLUDES its eval season from training (manifest provenance verified).
- Predictions are pre-quali (sampled_state): practice-only ordering; oracle/actual-grid modes refused by the scorer.
- Compound prior is time-safe (season < eval year).
- The prior '707 beats human 711' figure was LEAKED (a March train-evo-pipeline trained on 2025) and is retracted.

## Caveats

- LOSO folds train on seasons AFTER the eval season too (e.g. heldout_2022 saw 2023-24) — a mild edge the human lacked; the model still loses, so the gap is conservative.
- Gold static fusion was trained on LOSO OOF spanning all years and structurally saw each held-out year's OOF metrics; follow-up: strict per-season-holdout fusion.
- sampled_state uses the actual-Q roster (who started, not their order) — the project's established pre-quali design, not positional leakage.
