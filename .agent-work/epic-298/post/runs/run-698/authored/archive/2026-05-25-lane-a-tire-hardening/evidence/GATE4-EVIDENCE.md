# Gate 4 — Evidence (CLOSED)

**Branch:** claude/lane-a-pipeline-cleanup

## Files changed vs main
- `scripts/fit_compound_prior.py` — `fit_compound_prior_artifacts()` accepts `source_season`/`artifact_id` kwargs; `_infer_season_from_races()` added; module docstring marks exploratory
- `scripts/build_rolling_compound_priors.py` — `_patch_summary_json` deleted; `effect_space`/`normalize_residuals` params removed; passes explicit `source_season=target_year` and `artifact_id`
- `docs/architecture/packets/compound_prior.md` — 6-step canonical path; exploratory note; Known Limits gold regen entry
- `tests/unit/compound_prior/test_fit_compound_prior_cli.py` — 2 new param tests
- `tests/unit/compound_prior/test_build_rolling_priors.py` (new) — oracle round-trip + no-patch assertion

## Test result
162 passed in 35s (158 pre-existing + 4 new, zero regressions)

## Key confirmations
- `_patch_summary_json` confirmed absent from build script
- `artifact_id = f"rolling-{target_year}-before-r{round_num}"` preserved
- `source_season = target_year` explicit (not inferred from mixed race IDs)
- Oracle `load_compound_prior_artifact` passes on rolling prior output
- `src/compound_prior/`, `params/gold/`, `promote_runtime_artifact.py` untouched

## Reviewer: APPROVED
