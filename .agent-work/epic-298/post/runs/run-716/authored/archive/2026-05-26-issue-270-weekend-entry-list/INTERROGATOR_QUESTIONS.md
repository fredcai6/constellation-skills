# Interrogator Questions: issue-270-weekend-entry-list

## Source

Issue #270: "Fuller Q leakage fix: pass pre-weekend eligible_drivers list during training (Option B)"

## Queue

| Question | Status | Answer / evidence | Follow-up |
|---|---|---|---|
| Is the issue asking for a new data source at analysis time? | answered by docs/code | No. Orchestrator and Crew context require DB-only analysis. Any FastF1 access belongs in `src/data/collector.py`; evo must query `DatabaseManager`. | Keep ingestion and analysis separated. |
| Should historical missing entry lists fail training? | answered by issue | No. Acceptance explicitly requires graceful fallback to current Option A behavior when unavailable. | Fallback must be explicit and tested. |
| Does `eligible_drivers` already exist at the feature boundary? | answered by code | Yes. `build_race_features` and `_assemble_one_race_features` accept `eligible_drivers`; `build_all_race_features` currently derives it from actual results. | Replace derivation with DB entry list when present. |
| Is a schema change required? | answered by issue/code | Yes. There is no durable pre-weekend entry list table in `schema.sql` or `DatabaseManager`. | Add additive schema/migration plus query/upsert tests. |
| Is backfill in scope? | answered by issue | No. Issue notes say historical backfill is a non-goal. | Collector stores when sessions are collected; old DBs fall back. |

## Result

No blocking human question remains. Scope is clear enough for one implementation gate:
add a DB-owned weekend entry list contract, collect it from FastF1 session metadata at ingestion, and have evo training use it when present.
