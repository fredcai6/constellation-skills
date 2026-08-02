# Crew Handoff

## Role
implementer

## Assigned Gate
Gate 2 — A2: Real-Race Validation Harness

## Suggested Model Tier
simple bounded — one new script with clear acceptance criteria

## Test Mode
TDD — write `tests/unit/compound_prior/test_validate_harness.py` first (report schema and exit-code logic), then implement `scripts/validate_tire_wear_fit.py` to pass it.

## Task
Write `scripts/validate_tire_wear_fit.py` — a DB-backed CLI script that runs `fit_tire_wear_model` over one or more seasons, saves a compact validation report per season, and exits non-zero when required diagnostics are missing or convergence fails.

## Intent Protected
DB is the source of truth. The harness is a human-facing traceability tool, not a CI gate. It must be deterministic given the same DB. No changes to any existing source or test files.

## Close Criteria
- `scripts/validate_tire_wear_fit.py` runs to completion
- Report written to `outputs/validation/validate_<season>.json` per season
- Exit code non-zero when required diagnostic missing (unit tested)
- `py -m pytest tests/unit/compound_prior/test_validate_harness.py -q` passes
- `py -m pytest tests/unit/compound_prior/ -q --tb=no` still shows 158+ passed

## Authority
- H1 (script-only, no CI): user decision
- DB-backed: user decision
- Accepted compounds configurable via CLI flag (reasonable default: C1–C5): Pilot assumption

## Allowed Scope
- `scripts/validate_tire_wear_fit.py` (new)
- `tests/unit/compound_prior/test_validate_harness.py` (new)

## Specific Exclusions
- `src/compound_prior/` — no source changes
- All existing test files — do not modify
- `tests/integration/` — no integration test

## Relevant Project Rules For This Gate
- Python invoked as `py`, not `python`
- Tests run via `py -m pytest tests/...`
- DB is the single source of data — no direct FastF1 calls
- `RaceSegmentExtractor` is the canonical extraction path (takes a `db` object)

## Required Context
- `src/compound_prior/extractor.py` — `RaceSegmentExtractor.extract_race(year, round_num)`
- `src/compound_prior/solver.py` — `fit_tire_wear_model(obs_df, *, baseline_config, compound_config, iteration_config)`; returns `TireWearFitResult`
- `src/compound_prior/__init__.py` — canonical exports
- `src/data/database.py` — `DatabaseManager` constructor signature
- `src/compound_prior/compounds.yaml` — compound lists by year

## CLI Specification
```
py -m scripts.validate_tire_wear_fit \
    --db <path-to-sqlite> \
    --seasons 2023 2024 \
    [--accepted-compounds C1 C2 C3 C4 C5] \
    [--reference-compound C3] \
    [--output-dir outputs/validation]
```

## Report Schema (per season, saved as `validate_<season>.json`)
```json
{
  "season": 2024,
  "generated_at": "<ISO timestamp>",
  "accepted_compounds": ["C1", "C2", "C3", "C4", "C5"],
  "race_count": 24,
  "converged": true,
  "passes_run": 3,
  "support_by_compound": {
    "C3": {"observation_count": 1200, "weighted_count": 980.5}
  },
  "dropped_compounds": [],
  "warnings": [],
  "slope_sensitivity_summary": {
    "C3": {"gamma_min": 0.0012, "gamma_max": 0.0018}
  }
}
```

## Exit Code Logic
Exit non-zero if ANY of:
- Required report field is missing
- `dropped_compounds` is non-empty (compounds were silently lost without a warning entry)
- `converged` is False (solver did not converge within max passes)

## Unit Test Guidance
Unit-test the report schema validation and exit-code logic in isolation (don't need a real DB):
- Use a synthetic `TireWearFitResult`-like dict or mock to test report generation
- Test that missing fields → non-zero exit
- Test that `dropped_compounds` non-empty → non-zero exit
- Test that `converged=False` → non-zero exit
- Test that valid complete report → zero exit

## Project Mechanics For This Gate
Branch: `claude/lane-a-validation-harness` off `main`. Commit when tests pass.

## Required Evidence
1. `py -m pytest tests/unit/compound_prior/test_validate_harness.py -q` — all pass
2. `py -m pytest tests/unit/compound_prior/ -q --tb=no` — 158+ passed (no regressions)

## Required Verification Commands
```
py -m pytest tests/unit/compound_prior/test_validate_harness.py -q
py -m pytest tests/unit/compound_prior/ -q --tb=no
```

## Stop Conditions
- `RaceSegmentExtractor.extract_race` raises for a season that has data → investigate and report, don't swallow
- `TireWearFitResult` attribute needed for report doesn't exist → check `solver.py` dataclass, report to Pilot
- DB unavailable in environment → unit tests must still pass; note in return that live DB test was skipped

## Return Format
Diff summary of new files, pytest output for both commands, any blockers or scope concerns, assumptions used.
