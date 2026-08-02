# Crew Handoff

## Role
implementer

## Assigned Gate
Gate 4 — A3b: Pipeline Cleanup

## Suggested Model Tier
stronger broad/ambiguous — `build_rolling_compound_priors.py` is a complex orchestration script; must not break its output contract

## Test Mode
TDD where surface exists; inspection-only for doc changes

## Task
Three parts:

**Part 1:** Extend `fit_compound_prior_artifacts()` in `scripts/fit_compound_prior.py` to accept `source_season` and `artifact_id` params, threading them to `_summary_payload`. Mark the module as exploratory.

**Part 2:** Update `build_rolling_compound_priors.py` to pass `source_season` and `artifact_id` explicitly; remove `_patch_summary_json` entirely.

**Part 3:** Update `docs/architecture/packets/compound_prior.md` — add `promote_runtime_artifact` to the canonical path; note `fit_compound_prior.py` is exploratory.

## Intent Protected
- `build_rolling_compound_priors.py` must produce the same `compound_prior_summary.json` contract as before (just without the patch hack)
- Artifact naming must be preserved: `artifact_id = f"rolling-{target_year}-before-r{round_num}"`, `source_season = target_year`
- `load_compound_prior_artifact()` must succeed on the output of the updated rolling builder
- All 176 tests must stay green (this branch is off main, not the Gate 2 branch)

## Close Criteria
- `_patch_summary_json` function is gone from `build_rolling_compound_priors.py`
- `fit_compound_prior_artifacts()` accepts `source_season` and `artifact_id` kwargs
- `fit_compound_prior.py` module docstring says it is exploratory/debug, not canonical
- Architecture packet updated with promote step in canonical path
- `py -m pytest tests/unit/compound_prior/ -q --tb=no` — 176+ passed, zero regressions

## Authority
- Full solver swap (fit_tire_wear_model) for rolling builder is OUT OF SCOPE: it uses baselined parquets, not raw observations — different input format. User confirmed clean fix is sufficient.
- `_patch_summary_json` removal: user decision
- Artifact naming preserved (`rolling-{year}-before-r{N}`): Pilot decision
- Source season = target_year for rolling priors: Pilot decision (mixed historical+current race IDs make inferred year unreliable)

## Allowed Scope
- `scripts/fit_compound_prior.py` — add `source_season`/`artifact_id` params to `fit_compound_prior_artifacts()` and update docstring to say exploratory
- `scripts/build_rolling_compound_priors.py` — remove `_patch_summary_json`, pass explicit params
- `docs/architecture/packets/compound_prior.md` — update canonical path + exploratory note
- `tests/unit/compound_prior/test_fit_compound_prior_cli.py` — if new params need testing (likely yes)

## Specific Exclusions
- `src/compound_prior/` — DO NOT TOUCH (no src changes in this gate)
- `params/gold/` — DO NOT TOUCH
- `scripts/promote_runtime_artifact.py` — DO NOT TOUCH
- `tests/integration/` — DO NOT TOUCH

## Part 1 — extend `fit_compound_prior_artifacts()`

In `scripts/fit_compound_prior.py`, change:

```python
def fit_compound_prior_artifacts(
    paths: list[Path],
    *,
    output_root: Path,
    config: CompoundPriorFitConfig,
    compare_unweighted: bool = False,
) -> Path:
```

to:

```python
def fit_compound_prior_artifacts(
    paths: list[Path],
    *,
    output_root: Path,
    config: CompoundPriorFitConfig,
    compare_unweighted: bool = False,
    source_season: int | None = None,
    artifact_id: str | None = None,
) -> Path:
```

And update the `_summary_payload` call:

```python
summary_payload = _summary_payload(
    result, config,
    source_season=source_season if source_season is not None else _infer_season_from_races(result.selected_source_races),
    artifact_id=artifact_id,
)
```

Also update the module docstring at the top to say:
```
Exploratory/debug script for the compound prior (absolute C-number basis).
NOT the canonical production path — use scripts/fit_tire_wear_model.py + scripts/promote_runtime_artifact.py instead.
```

## Part 2 — update `build_rolling_compound_priors.py`

1. Delete `_patch_summary_json` function (lines 78–95 in current main)
2. Remove the `effect_space` and `normalize_residuals` parameters from `build_rolling_prior_for_round` (they were only used by `_patch_summary_json`)
3. Remove `import json` if it becomes unused (check — it may still be used for `gold_summary` loading in `main()`)
4. In `build_rolling_prior_for_round`, replace the `fit_compound_prior_artifacts` call + patch block with:

```python
artifact_id = f"rolling-{target_year}-before-r{round_num}"
summary_path = fit_compound_prior_artifacts(
    [tmp_path],
    output_root=round_output,
    config=config,
    source_season=target_year,
    artifact_id=artifact_id,
)
```

5. Remove the now-dead `artifact_id = f"rolling-..."` and `_patch_summary_json(...)` lines
6. Remove `effect_space` and `normalize_residuals` from `main()` call to `build_rolling_prior_for_round`

NOTE: `import tempfile` is still needed (used in the temp parquet logic). Keep it.
NOTE: `import json` is still needed for `gold_summary = json.loads(...)` in `main()`. Keep it.

## Part 3 — update `docs/architecture/packets/compound_prior.md`

In the **Canonical Execution Path** section, add step 4.5:

```
4. write_tire_wear_run_bundle  →  full run bundle (run_summary.json, compound_parameters.json, parquets)
5. promote_runtime_artifact    →  compact runtime prior artifact (compound_prior_summary.json per season)
6. runtime_normalization       →  CompoundNormalizer (consumed by evo data_adapter)
```

(Renumber old step 4 → steps 4+5, old CLI note stays.)

In the **Key Modules** or a new **Scripts** section, add a note:
> `scripts/fit_compound_prior.py` — exploratory/debug only. Fits compound prior from pre-baselined observations. Not the canonical production path.

In the **Known Limits** section, add:
> Gold artifacts in `params/gold/compound_prior/` (2022–2025) were produced via the old `fit_compound_prior` path. Regen from the unified solver path (2018–2026) is planned.

## Unit Tests

Add tests to `tests/unit/compound_prior/test_fit_compound_prior_cli.py`:
- `test_fit_compound_prior_artifacts_accepts_explicit_source_season` — pass `source_season=2023`, assert JSON has `"source_season": 2023`
- `test_fit_compound_prior_artifacts_accepts_explicit_artifact_id` — pass `artifact_id="my-test-artifact"`, assert JSON has `"artifact_id": "my-test-artifact"`

Add a test (or extend existing) in a new `tests/unit/compound_prior/test_build_rolling_priors.py`:
- `test_build_rolling_prior_output_is_loadable_by_oracle` — mock/stub the data loading, call `build_rolling_prior_for_round` with synthetic parquets, assert `load_compound_prior_artifact` succeeds on output
- `test_patch_summary_json_no_longer_exists` — assert `_patch_summary_json` is not importable from the module

## Relevant Project Rules For This Gate
- Python invoked as `py`
- Tests run via `py -m pytest tests/...`
- Branch off `main` for this gate: `claude/lane-a-pipeline-cleanup`

## Project Mechanics For This Gate
Branch: `claude/lane-a-pipeline-cleanup` off `main`. Commit when tests pass.

## Required Evidence
1. `py -m pytest tests/unit/compound_prior/test_fit_compound_prior_cli.py -q` — new params tests pass
2. `py -m pytest tests/unit/compound_prior/ -q --tb=no` — 176+ passed, zero regressions

## Required Verification Commands
```
py -m pytest tests/unit/compound_prior/test_fit_compound_prior_cli.py -q
py -m pytest tests/unit/compound_prior/ -q --tb=no
```

## Stop Conditions
- `_patch_summary_json` removal breaks a test that actually checks for it → find the test, assess, report to Pilot
- `build_rolling_compound_priors.py` has other uses of `effect_space`/`normalize_residuals` beyond the patch call → report before removing
- `import json` removal would break `gold_summary` loading → keep it

## Return Format
Diff summary (which functions removed/added), both pytest outputs, assumptions used, any blockers.
