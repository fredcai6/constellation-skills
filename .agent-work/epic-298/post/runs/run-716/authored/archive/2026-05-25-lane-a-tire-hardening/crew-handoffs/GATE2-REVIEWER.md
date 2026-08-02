# Crew Handoff

## Role
reviewer

## Assigned Gate
Gate 2 — A2: Real-Race Validation Harness

## Suggested Model Tier
simple bounded

## Test Mode
inspection + test verification

## Task
Review `scripts/validate_tire_wear_fit.py` and `tests/unit/compound_prior/test_validate_harness.py` on branch `claude/lane-a-validation-harness`. Confirm the implementation is correct, safe, and matches the gate spec. Do NOT implement new code — raise findings only.

## Intent Protected
- DB is source of truth; no direct FastF1 calls
- Exit-code logic is correct for all three failure conditions
- Report schema matches spec exactly
- No existing files were modified

## Close Criteria
- Report schema matches spec (all required fields present)
- Exit-code logic: non-zero for missing field, dropped_compounds non-empty, converged=False
- No DB imports at module level (unit tests must work without DB)
- Test coverage is meaningful — not just shape-checking
- No existing files modified
- `py -m pytest tests/unit/compound_prior/ -q --tb=no` still 179 passed

## Authority
Reviewer may not change scope. Flag findings; do not fix them inline unless trivially one-line.

## Allowed Scope
Read-only review of:
- `scripts/validate_tire_wear_fit.py`
- `tests/unit/compound_prior/test_validate_harness.py`

## Specific Exclusions
Do not touch any other file.

## Relevant Project Rules For This Gate
- Python invoked as `py`
- DB is the single source of data
- `RaceSegmentExtractor` is the canonical extraction path

## Required Context
- `scripts/validate_tire_wear_fit.py` (on branch)
- `tests/unit/compound_prior/test_validate_harness.py` (on branch)
- Gate 2 spec (in GATED_PLAN.md: report schema, exit code logic, CLI spec)

## Project Mechanics For This Gate
Read-only. Do not commit.

## Required Evidence
1. Confirm `py -m pytest tests/unit/compound_prior/ -q --tb=no` — 179 passed
2. List any correctness concerns, schema mismatches, or missing test cases
3. Explicit sign-off or list of blocking findings

## Required Verification Commands
```
cd C:\Programs\f1Brainz\.claude\worktrees\vigilant-mcclintock-596957
git checkout claude/lane-a-validation-harness
py -m pytest tests/unit/compound_prior/ -q --tb=no
```

## Stop Conditions
Exit-code logic is wrong or inverted → blocking finding. Report schema missing a field → blocking finding.

## Return Format
Test output, list of findings (blocking / advisory), explicit sign-off or block decision.
