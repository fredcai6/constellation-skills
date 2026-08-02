# Excursion Brief: `x5-sprint-sq-evidence-verify`

## The one named question

On sprint weekends, does the live practice preprocessor / quali-evidence path actually use SQ (and sprint-race) sessions as quali evidence — or does it drop them, as `docs/evo/quali_evidence_findings.md` §B suspects ("if the preprocessor currently feeds only FP1 on sprint weekends, that is the single highest-value fix")?

## Type

research

**Why this type:** code-truth verification of a doc-flagged suspicion; nothing to build.

## What "answered" looks like

A definitive trace (file:line) of what `_load_weekend_classifications` / `practice_preprocessor` / `build_race_features` feed into quali-relevant features on a sprint weekend: which sessions (FP1/SQ/S) reach `qs_*` fields and the anchor. Verdict: USED / PARTIALLY USED / DROPPED, with the exact seam where a fix would go and a size estimate. Cross-check against one real sprint weekend's data in the per-year DB if quick.

## Budget / stop conditions

- Read-only. ~20–30 min.
- Do not fix anything; locate and size only.
- **Scoped nulls:** verdict covers the LIVE path (current main), not historical gold bundles.

## Research excursion

- **Sources:** `src/evo_predictor/data_adapter/_build.py` (`_load_weekend_classifications`, `build_race_features`), `src/evo_predictor/practice_preprocessor/`, `src/evo_predictor/models/_features.py`, `docs/evo/quali_evidence_findings.md` §B, one sprint weekend in `data/f1_data_2025.db` for a concrete check.
- **Findings format:** cited file:line trace + verdict.

## Return

Full findings → `.agent-work/explore-physics-evo-hookup/excursions/x5-sq-evidence-RESULT.md`. Final message = short summary + verdict.
