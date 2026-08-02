# Crew Handoff

## Role
implementer

## Assigned Gate
Gate 1 — Artifact naming cleanup (#275)

## Suggested Model Tier
simple bounded — well-specified mechanical rename with clear acceptance criteria

## Test Mode
TDD required — update test fixtures to match new naming convention; confirm all pass before returning

## Task
Standardise all gold-cycle artifact filenames to `<artifact_id>_<YYMMDD_HHMMSS>_<short_descriptor>` by:
1. Creating a `make_artifact_slug` utility in a new `src/evo_predictor/gold_cycle/slug.py`
2. Updating all slug-generation callsites to use it
3. Renaming committed params artifacts via `git mv`
4. Updating all test fixtures that hardcode old-convention stems

## Intent Protected
All gold-cycle artifact types produce consistent, scannable filenames. No hardcoded old-convention stems remain in source or tests after this gate. Existing tests continue to pass.

## Close Criteria
- `make_artifact_slug(artifact_id, run_start_dt, descriptor) -> str` exists in `src/evo_predictor/gold_cycle/slug.py` and is the only slug-generation callsite
- All 5 artifact types produce `<artifact_id>_<YYMMDD_HHMMSS>_<short_descriptor>` filenames
- Committed params artifacts renamed via `git mv` (3 fusion files, 5 uncertainty_calibration files)
- All hardcoded old stems updated in the 4 test files
- `py -m pytest tests/unit/evo_predictor/ -v` passes with zero failures

## Authority
- User decision: #275 goes in before the training run
- Clean break on filenames — no backward-compat aliases
- Do NOT change JSON payload field names (train_years, eval_year, etc.)
- Do NOT rename gitignored outputs/ or reports/evo/ files

## Allowed Scope
- `src/evo_predictor/gold_cycle/slug.py` — create new file
- `src/evo_predictor/gold_cycle/runner.py` lines 171–172 (slug) and 288–289 (diagnostics_slug)
- `src/evo_predictor/fusion_training.py` lines 457–458 (stem)
- `scripts/assemble_trained_sampled_runtime_manifest.py` (4 path-builder functions)
- `scripts/materialize_runtime_bundles.py` (docstring only)
- `src/evo_predictor/runtime_bundle_materializer.py:50` (comment only)
- `params/gold/fusion/` — git mv 3 files
- `params/gold/uncertainty_calibration/` — git mv 5 files
- `tests/unit/evo_predictor/test_pipeline_validation.py` (15+ stem refs)
- `tests/unit/evo_predictor/test_runtime_bundle_materialization.py` (2 path refs)
- `tests/unit/evo_predictor/test_gold_runtime_bundle_schema_alignment.py` (1 path ref)
- `tests/unit/evo_predictor/test_sampled_runtime_comparison_manifest_resolution.py` (1 stem ref)

## Specific Exclusions
- Do NOT touch gold_defaults.toml
- Do NOT change any JSON payload schemas or internal field names
- Do NOT rename outputs/ or reports/evo/ artifacts (gitignored, transient)
- Do NOT touch any files outside the allowed scope above

## Relevant Project Rules For This Gate
- Python invoked as `py` (not python) on this machine
- Tests run via `py -m pytest tests/...`
- Commit message must end with: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`

## Required Context
- Read `src/evo_predictor/gold_cycle/runner.py` lines 160–200 and 280–300 to see current slug/diagnostics_slug generation
- Read `src/evo_predictor/fusion_training.py` lines 450–465 to see current stem generation
- Read `scripts/assemble_trained_sampled_runtime_manifest.py` fully — 4 path-builder functions
- Read `tests/unit/evo_predictor/test_pipeline_validation.py` fully — locate all hardcoded stems
- Run `git ls-files params/gold/fusion/ params/gold/uncertainty_calibration/` to get exact current filenames before renaming
- The proposed artifact_id mapping from issue #275:
  | Current prefix | artifact_id |
  |---|---|
  | `gold_module_training_cycle` | `gold_cycle` |
  | `static_hierarchical_fusion` | `fusion` |
  | `module_uncertainty_calibration` | `unc_cal` |
  | `module_uncertainty_diagnostics` | `unc_diag` |
  | `sampled_runtime_comparison` | `rt_comparison` |
- `run_start_dt` for committed artifacts: parse the existing filename's date component or use the `created_at` field inside the JSON
- For committed artifacts being git mv'd: the new name should use the timestamp from the `created_at` field inside the JSON payload. Read each JSON to extract it.

## Project Mechanics For This Gate
- Work on the branch that already exists for this worktree; do not create a new branch
- Commit all changes (source + git mv + test updates) in a single logical commit
- PR to main after all tests pass

## Required Evidence
- `py -m pytest tests/unit/evo_predictor/ -v` — full output, zero failures
- `git diff --stat HEAD` or `git show --stat` showing renamed params files and updated source/test stems
- Confirmation that no old-convention stem strings remain in any tracked file: `grep -r "gold_module_training_cycle\|static_hierarchical_fusion\|module_uncertainty_calibration\|module_uncertainty_diagnostics" src/ scripts/ tests/ params/` returns no matches (or only in gitignored files)

## Required Verification Commands
```
py -m pytest tests/unit/evo_predictor/ -v
grep -r "gold_module_training_cycle\|static_hierarchical_fusion\|module_uncertainty_calibration" src/ scripts/ tests/ params/gold/
git ls-files params/gold/fusion/ params/gold/uncertainty_calibration/
```

## No-Test-Surface Rationale
N/A — tests required

## Stop Conditions
- Any test failure that cannot be resolved by updating the fixture stem (indicates a deeper breakage — return to Pilot)
- Ambiguity about which committed artifact JSON maps to which new name
- Any source file outside allowed scope must be touched to make tests pass
- The `created_at` timestamp is missing from a committed artifact JSON (surface the filename and return)

## Return Format
- Summary of files changed
- New committed artifact names (old → new for each)
- `py -m pytest tests/unit/evo_predictor/ -v` output (pass/fail counts)
- Grep verification output confirming no old stems remain
- Any stop conditions encountered
