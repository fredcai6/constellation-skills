# Gate 3 — Evidence (CLOSED)

**Branch:** claude/lane-a-promote-bridge (commit a9a22fd)

## Files changed vs main
- `scripts/fit_compound_prior.py` — `_summary_payload()` emits runtime fields natively; `_infer_season_from_races()` added; call site updated
- `scripts/promote_runtime_artifact.py` (new) — self-verifying promote CLI
- `tests/unit/compound_prior/test_fit_compound_prior_cli.py` — 5 new field tests + oracle round-trip test (10 total)
- `tests/unit/compound_prior/test_promote_artifact.py` (new) — 12 tests

## Blocking findings resolved
1. `source_season: null` → fixed via `_infer_season_from_races()`, passes oracle
2. Oracle round-trip test added: `load_compound_prior_artifact` succeeds on CLI output
3. Redundant `unlink` in `except` block removed

## Test result
176 passed in 39.36s (158 pre-existing + 18 new, zero regressions)

## Reviewer: APPROVED
