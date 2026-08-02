# Mission Frame — cmdr-603 (issue #603 data catch-up)

Shrunk frame: trivial/mechanical operational task, not a code change. No architecture map read
applies — this is a data-collection run against an already-shipped collector script
(`scripts/collect_evo_data.py`) writing to an already-shipped table
(`session_classifications` in `src/data/database.py`). No structure is being added, changed,
or extended; the map has nothing to say about "run the existing collector for two more rounds."

## Intent
Fill the R8 (Austria) and R9 (Great Britain, sprint weekend) gap in the canonical
`data/f1_data_2026.db` `session_classifications` table via the existing collector, verify
presence + correctness, and report — unblocking the Belgium R10 fantasy prediction (issue #601
Track 1).

## Affected Capabilities
- Data ingestion (`scripts/collect_evo_data.py` + `src/data/collector.py`
  `_extract_session_classification`) — invoked as-is, no code change.
- DB read API (`has_session_classification`, `get_session_classification`,
  `get_session_driver_info`) — used read-only for verification.

## Structural Anchors
- `scripts/collect_evo_data.py` — CLI entry, unmodified.
- `src/data/database.py` `session_classifications` table — write target via the collector,
  not touched directly.

## Governing Constraints / Assumptions
- Canonical-data constraint (ORCHESTRATOR_CONTEXT.md): DB is the sole source; collection via
  the standard collector is the one sanctioned live-API path.
- Launch-order pre-rulings: main checkout only (no worktree), no `data/*.db` commit, no
  `--include-telemetry`, OS-detached launch with STATE_NOTE discipline, no `--rounds` (use
  `--gp`), verify round mapping (2026 Bahrain/Saudi drop reindex).

## Decision Anchors & Decision Pressure
- No durable-structure decision pressure — this run makes no schema, adapter, or interface
  choice. Any discovered code defect (e.g. a round-mapping bug) is explicitly out of latitude
  per the launch order and floats to the Admiral rather than being decided here.

## Claims / Evidence Surfaces
- Claim: R1–R7 present, R8/R9 absent — reconfirmed live in the `understand` step
  (`session_classifications` distinct rounds = 1..7, Barcelona-Catalunya last).
- Each gate re-confirms `has_session_classification(2026, 8|9, <type>)` per session type
  collected, plus a podium spot-check against known 2026 results.

## Map Confidence / Staleness / Disputes
- None flagged — the collector and DB API are stable, exercised repeatedly by prior runs
  (LESSONS.md `lesson:worktree-untracked-data`, `lesson:py-launcher`).

## Out of Scope
- Any `data/*.db` commit, telemetry collection, Parquet mirror backfill (noted only, not run
  unless it demonstrably covers classifications/laps), and any code fix (round-mapping or
  otherwise) — all float to the Admiral per Inherited Latitude.
