# Crew Handoff

## Role
implementer

## Assigned Gate
Gate 3 — A3a: Promote Bridge

## Suggested Model Tier
simple bounded — well-defined JSON field additions and one new script

## Test Mode
TDD — write tests first, then implement

## Task
Two parts (implement both):

**Part 1:** Fix `_summary_payload()` in `scripts/fit_compound_prior.py` to emit all runtime artifact fields natively — so its output is directly loadable by `load_compound_prior_artifact()` without patching.

**Part 2:** Write `scripts/promote_runtime_artifact.py` — reads a `compound_parameters.json` from a `fit_tire_wear_model` run bundle, constructs and validates a `compound_prior_summary.json`, and writes it to `<dest>/<season>/`.

## Intent Protected
- `load_compound_prior_artifact()` in `src/compound_prior/runtime_normalization.py` is the validation oracle — never bypass it
- `src/compound_prior/diagnostics.py` must NOT be touched (`write_tire_wear_run_bundle` stays as-is)
- `src/compound_prior/runtime_normalization.py` must NOT be touched
- All 182 tests must stay green

## Close Criteria
- `load_compound_prior_artifact(path)` succeeds on a summary produced by the fixed `fit_compound_prior_artifacts()`
- `load_compound_prior_artifact(path)` succeeds on a summary produced by `promote_runtime_artifact.py`
- `py -m pytest tests/unit/compound_prior/test_fit_compound_prior_cli.py -q` passes
- `py -m pytest tests/unit/compound_prior/test_promote_artifact.py -q` passes (new file)
- `py -m pytest tests/unit/compound_prior/ -q --tb=no` — 182+ passed, zero regressions

## Authority
- Separate promote step (E2): user decision
- `_summary_payload` gets runtime fields natively: user decision
- `accepted_compounds` derived from `parameter_means` keys (`beta_C#` pattern): Pilot decision
- Default `artifact_id`: `f"compound-prior-{source_season}"` when not supplied by caller: Pilot assumption

## Allowed Scope
- `scripts/fit_compound_prior.py` — modify `_summary_payload()` and its call site in `fit_compound_prior_artifacts()` only
- `scripts/promote_runtime_artifact.py` (new)
- `tests/unit/compound_prior/test_fit_compound_prior_cli.py` — extend existing tests for new fields
- `tests/unit/compound_prior/test_promote_artifact.py` (new)

## Specific Exclusions
- `src/compound_prior/diagnostics.py` — DO NOT TOUCH
- `src/compound_prior/runtime_normalization.py` — DO NOT TOUCH
- `src/compound_prior/solver.py` — DO NOT TOUCH
- Any existing test files other than `test_fit_compound_prior_cli.py`

## Relevant Project Rules For This Gate
- Python invoked as `py`
- `load_compound_prior_artifact()` is the validation oracle — use it in the promote script to self-verify before writing
- Runtime artifact required fields: `artifact_id`, `source_season`, `effect_space="normalized_fractional"`, `normalize_residuals=True`, `accepted_compounds`, `reference_compound`, `parameter_means`, `parameter_sigmas`, `observation_counts_by_compound`, `weighted_counts_by_compound`, `selected_source_races`, `solver_status`, `warnings`

## Required Context

### `CompoundPriorFitResult` fields (from `src/compound_prior/solver.py`)
Does NOT have `accepted_compounds`. Does have: `reference_compound`, `parameter_means`, `parameter_sigmas`, `observation_counts_by_compound`, `weighted_counts_by_compound`, `selected_source_races`, `solver_status`, `warnings`.

### `CompoundPriorFitConfig` fields (from `src/compound_prior/solver.py`)
Has `accepted_compounds: tuple[str, ...]` and `reference_compound: str`.

### `fit_compound_prior_artifacts()` signature (in `scripts/fit_compound_prior.py`)
```python
def fit_compound_prior_artifacts(
    paths: list[Path],
    *,
    output_root: Path,
    config: CompoundPriorFitConfig,
    compare_unweighted: bool = False,
) -> Path:
```
`config` is already available — pass it to `_summary_payload`.

### `_summary_payload()` current signature
```python
def _summary_payload(result: CompoundPriorFitResult) -> dict:
```
Change to accept `config` as second arg: `_summary_payload(result, config)`.

### `compound_parameters.json` fields (written by `write_tire_wear_run_bundle`)
Contains: `solver_status`, `warnings`, `selected_source_races`, `parameter_means`, `parameter_sigmas`, `observation_counts_by_compound`, `weighted_counts_by_compound`, `reference_compound`, plus many others. Does NOT contain: `artifact_id`, `source_season`, `accepted_compounds`, `effect_space`, `normalize_residuals`.

### Deriving `accepted_compounds` from `parameter_means`
`accepted_compounds` = sorted list of `C#` values where `beta_C#` key exists in `parameter_means`, sorted by C-number. Pattern: `name.startswith("beta_") and name[5:].startswith("C") and name[6:].isdigit()`.

### `load_compound_prior_artifact()` location
`src/compound_prior/runtime_normalization.py` — import and call it to validate before writing.

## Part 1 — fix `_summary_payload()`

Add to the returned dict:
```python
"artifact_id": config_artifact_id,      # see below
"source_season": source_season,         # int, caller-supplied via new kwarg
"accepted_compounds": list(config.accepted_compounds),
"reference_compound": config.reference_compound,
"effect_space": "normalized_fractional",
"normalize_residuals": True,
```

Updated signature:
```python
def _summary_payload(
    result: CompoundPriorFitResult,
    config: CompoundPriorFitConfig,
    *,
    source_season: int | None = None,
    artifact_id: str | None = None,
) -> dict:
```
- `artifact_id` default: `f"compound-prior-{source_season}"` if `source_season` is not None, else `"compound-prior-unknown"`
- `source_season` default: `None` (int or None in output — `null` JSON is acceptable for exploratory use; the loader will fail if you try to load it without a season, which is correct)

In `fit_compound_prior_artifacts()`, update the call:
```python
summary_payload = _summary_payload(result, config)
```
No `source_season` needed here — this path is exploratory; the caller can patch via `promote_runtime_artifact.py` if they want a loadable artifact.

**Actually — simpler:** just always emit the fields from config, and leave `source_season=None` and auto-generate `artifact_id`. The existing gold summaries already have these fields (they were patched in); adding them natively doesn't break anything.

## Part 2 — `scripts/promote_runtime_artifact.py`

CLI:
```
py -m scripts.promote_runtime_artifact \
    --bundle-dir <path>          # directory containing compound_parameters.json \
    --season <year>              # int, source season \
    --dest <root>                # output root; writes to <root>/<season>/compound_prior_summary.json \
    [--artifact-id <id>]         # default: "compound-prior-{season}"
```

Logic:
1. Read `<bundle_dir>/compound_parameters.json`
2. Derive `accepted_compounds` from `parameter_means` keys
3. Build `compound_prior_summary.json` payload with all required fields
4. Write to a temp file, call `load_compound_prior_artifact(temp_path)` — if it raises, print the error and exit non-zero (self-verifying)
5. Write to `<dest>/<season>/compound_prior_summary.json` (create dirs)
6. Print field summary (season, accepted_compounds, solver_status, warning count)
7. Exit 0

## Unit Tests — `test_promote_artifact.py`
- Test: valid `compound_parameters.json` → `promote` → `load_compound_prior_artifact` succeeds
- Test: missing required field in compound_parameters → exit non-zero
- Test: `accepted_compounds` correctly derived from `parameter_means` keys
- Test: output written to correct path `<dest>/<season>/compound_prior_summary.json`
- Test: `--artifact-id` override respected
- Test: default `artifact_id` is `f"compound-prior-{season}"`

## Unit Tests — `test_fit_compound_prior_cli.py` (extend)
Add tests asserting the fixed `_summary_payload` includes:
- `effect_space == "normalized_fractional"`
- `normalize_residuals is True`
- `accepted_compounds` matches `config.accepted_compounds`
- `reference_compound` matches `config.reference_compound`
- `artifact_id` is a non-empty string

## Project Mechanics For This Gate
Branch: `claude/lane-a-promote-bridge` off `main`. Commit when tests pass.

## Required Evidence
1. `py -m pytest tests/unit/compound_prior/test_promote_artifact.py -q` — all pass
2. `py -m pytest tests/unit/compound_prior/test_fit_compound_prior_cli.py -q` — all pass
3. `py -m pytest tests/unit/compound_prior/ -q --tb=no` — 182+ passed, zero regressions

## Required Verification Commands
```
py -m pytest tests/unit/compound_prior/test_promote_artifact.py -q
py -m pytest tests/unit/compound_prior/test_fit_compound_prior_cli.py -q
py -m pytest tests/unit/compound_prior/ -q --tb=no
```

## Stop Conditions
- `load_compound_prior_artifact` raises on a field you thought was present → check field name carefully against `runtime_normalization.py` lines 76–95 (required fields list)
- `compound_parameters.json` missing a field needed for runtime artifact → report to Pilot; do not invent values

## Return Format
Diff summary of changed/new files, all three pytest outputs, assumptions used, any blockers.
