# Gated Plan: issue 270 weekend entry list

## Problem Statement

`build_all_race_features` still chooses training `eligible_drivers` from actual session results. That avoids Q-only leakage but does not represent the pre-weekend entered race field. Issue #270 requires a DB-backed weekend entry list, training pass-through when available, and fallback to current behavior when unavailable.

## Intent Protected

Training must not learn from a post-hoc/session-derived driver field when a pre-weekend entry list exists, and evo analysis must continue reading only from SQLite.

## Scope

**Allowed regions/files:** `src/data/schema.sql`, `src/data/database.py`, `src/data/collector.py`, `src/evo_predictor/data_adapter.py`, focused unit tests under `tests/unit/`.  
**Not scope:** Historical backfill, sampled-runtime prediction behavior, broad collector redesign, changing race/quali actual target selection.  
**Specific exclusions:** Direct FastF1/API calls outside data ingestion; deleting or changing unrelated workflow/report artifacts.

## Structural Baseline

**Need:** no  
**Status:** established from current architecture map  
**Evidence:** `docs/architecture/index.md` says `src/data/` owns DB schema/ingestion and `src/evo_predictor/` depends on SQLite only.

## Authority / Assumptions

- Issue #270 acceptance criteria authorize schema/query/collector/training changes.
- Orchestrator context permits autonomous branch/edit/test/commit for non-trivial tasks; push/PR/merge require approval.
- Missing entry list rows fall back to current Option A behavior by issue requirement.

## Test Mode

**Plan default:** TDD for behavior changes; full affected region suites after implementation.  
**Inspection-only rationale:** not applicable.

## Project Mechanics Hooks

| Moment | Hook | Owner | Evidence |
|---|---|---|---|
| Before gate | branch | Pilot | `codex/issue-270-weekend-entry-list` |
| After gate evidence accepted | commit optional | Pilot | local only unless requested |
| Before closeout | archive workflow artifacts | Pilot | archive path |
| After archive | push/PR/close | user approval required | not authorized |

## Gates

### Gate 1: DB-backed weekend entry list for training

**Purpose:** Add one canonical DB contract for weekend entry lists and have `build_all_race_features` use it when present.  
**Crew cycle:** implementer Crew -> integrate evidence -> reviewer Crew -> integrate evidence -> gate close  
**Implementer handoff:** required  
**Reviewer handoff:** required  
**Suggested model tier:** default inherited; bounded but crosses data/evo regions.  
**Test mode:** TDD with focused tests first, then affected region suites.  
**Allowed scope:** same as plan.  
**Specific exclusions:** same as plan.

**Close criteria:**  
- [ ] DB schema includes a durable weekend entry-list table with additive migration for existing DBs.
- [ ] `DatabaseManager` exposes strict upsert/query methods for weekend entry lists.
- [ ] Collector stores `session.drivers` as the event entry list during ingestion when available.
- [ ] `build_all_race_features` passes DB entry list as `eligible_drivers` when present.
- [ ] Missing entry list falls back to current actual-derived behavior.
- [ ] Tests prove FP-only exclusion with entry list and fallback behavior without entry list.
- [ ] Data and evo region verification evidence is captured.

**Required evidence:**  
- Red/green focused pytest for data DB methods/collector.
- Red/green focused pytest for evo `build_all_race_features` eligible-driver behavior.
- `py -m pytest tests/unit/evo_predictor -v`
- `py -m pytest tests/unit/ -v`
- Reviewer Crew finding summary.

**Required verification commands:**
- `py -m pytest tests/unit/test_collector.py tests/unit/evo_predictor/test_data_adapter.py -v`
- `py -m pytest tests/unit/evo_predictor -v`
- `py -m pytest tests/unit/ -v`

**Stop conditions:** requirement conflicts with FastF1 availability, schema migration breaks existing DB creation, or evidence requires widening beyond data/evo.
**Next gate:** closeout.

## Triage Candidate Log

| Candidate | Reason | Anchor | Evidence | Status |
|---|---|---|---|---|
| none | none | none | none | none |

## Plan-Level Stop Conditions

- unresolved human decision affects scope, authority, or evidence
- required evidence cannot be produced
- scope expands beyond allowed regions/files
- direct FastF1 read is needed from evo/analysis code
- structural uncertainty affects ownership, dependency, scope, or evidence

## Final Completion Criteria

- [ ] all gates closed or remaining blockers listed
- [ ] each implementation gate completed its Crew cycle
- [ ] evidence satisfies close criteria
- [ ] assumptions still hold
- [ ] architecture reconciliation checked
- [ ] Triage candidates routed, dropped because reason, or none
