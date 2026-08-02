# Crew Handoff: Gate 1 Implementer

## Work

Implement issue #270: DB-backed weekend entry lists used by `build_all_race_features` when present, with fallback to current behavior when absent.

## Context

Read:
- `docs/agents/CREW_CONTEXT.md`
- `.agent-work/issue-270-weekend-entry-list/GATED_PLAN.md`
- Issue #270 text in `.agent-work/issue-270-weekend-entry-list/INTERROGATOR_QUESTIONS.md`

## Ownership

You own edits in:
- `src/data/schema.sql`
- `src/data/database.py`
- `src/data/collector.py`
- focused tests under `tests/unit/`
- `src/evo_predictor/data_adapter.py`

You are not alone in the codebase. Do not revert unrelated changes or untracked files. Keep the patch scoped to this gate.

## Required Behavior

- Add a durable weekend entry list table and additive migration for older DBs.
- Add strict `DatabaseManager` upsert/query methods. Query should return a `set[str]` when rows exist and `None` when unavailable.
- Store FastF1 `session.drivers` during collection when available.
- In `build_all_race_features`, use DB entry list as `eligible_drivers` when available; otherwise fall back to current actual-derived eligible set.
- Keep evo code DB-only; no FastF1 or external reads from evo.

## Tests First

Write failing tests before implementation:
- DB method tests for upsert/query/missing behavior.
- Collector test that stores session drivers.
- Evo training test that entry list excludes FP-only driver and fallback matches current actual-derived behavior.

## Verification

Run:
- `py -m pytest tests/unit/test_collector.py tests/unit/evo_predictor/test_data_adapter.py -v`

If time allows, also run:
- `py -m pytest tests/unit/evo_predictor -v`

## Final Report

Report changed files, tests run, results, and any blockers. Do not push or create PRs.
