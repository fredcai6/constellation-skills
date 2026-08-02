# Launch Order: `cmdr-601-fastf1-aero-schema - #483/#499`

## Mission
Start below the persisted DB null and resolve the raw-source question for the 2026 baseline.

The human rejected a state-agnostic 2026 baseline. Your mission is therefore:

1. Inspect raw FastF1/cache-facing telemetry surfaces for 2026 active-aero state, starting from the same ingestion layer F1Brainz already uses.
2. If a real active-aero state exists upstream, build the bounded DB schema/ingestion path to persist it in the telemetry store with strict tests and docs.
3. If no real upstream state exists, produce an evidence-backed blocker naming the exact FastF1/raw boundary checked and what external/source work is required next.

This wave serves epic #601 by making observations support modeling before predictions. Do not let downstream physics/evo infer active-aero state from heuristics.

## Prior-Wave Verdicts (pasted)
Wave 1 #483/#499 measured-null sidecar:

- Current DB-backed 2026 telemetry exposed only `drs`, with 2026 TelemetryStore aggregate at 35 car sessions / 16,453,184 rows / all `drs=0`.
- A 2025 comparison showed normal DRS activity, including 1,350,719 open-code rows.
- This was a scoped persisted-surface null, not proof that active aero does not exist anywhere upstream.

Wave 2 #483/#499 source-missing-guarded:

- Current persisted telemetry exposes only FastF1 `DRS` as an aero-like state channel (`src/data/schema.sql`, `collector.py`, `telemetry_store.py`, `telemetry_session.py`).
- Local parquet probe: 2025 has 120 sessions / 50,598,282 rows / 1,350,719 DRS open-code rows / 34,523,911 nonzero DRS rows.
- Local parquet probe: 2026 has 35 sessions / 16,453,184 rows / 0 DRS open-code rows / 0 nonzero DRS rows.
- Season SQLite snapshots and `telemetry_store.db` do not provide another active-aero state column.
- Local commit `370704442f67af2c93a4bbb0ff43d68d85f18288` pins all-zero DRS as `no_drs_lever` in longitudinal fitting and documents that 2026 all-zero persisted `drs` is missing observed-state evidence, not a usable active-aero lever.
- The human rejected the fallback "state-agnostic 2026 baseline" as not acceptable.

## Pre-Rulings
Ruled in advance, overridable only with evidence:

- Raw FastF1/cache inspection is allowed in this wave for source discovery and ingestion implementation.
- Production analysis/model/predictor code still must not call FastF1 directly. If a signal exists, persist it through `src/data` DB/parquet ingestion first.
- Do not invent active-aero labels from speed/throttle/brake/gear/DRS heuristics.
- If FastF1 exposes only `DRS` and no other active-aero state, report the blocker plainly; do not add a fake schema column.
- If FastF1 exposes a real observed column/field/state, build the narrow schema path rather than a broad physics refactor:
  - add explicit DB/parquet column(s) with nullable/unknown-safe semantics;
  - update collector/session reconstruction/store interfaces;
  - add unit tests for old data without the field and new data with the field;
  - document the field meaning, unit/type, producer, store, and downstream availability.
- Avoid generated DB/parquet artifact commits. Schema/code/tests/docs are in scope; data refresh is not.
- Broad `AeroDragSet` or active-aero physics fitting refactor is out of scope unless you return a plan and ask the Admiral.

## Honest-Null Clause
A measured negative at the raw FastF1/cache layer is still a complete deliverable, but it must be stronger than the persisted DB null: name the raw objects/methods/files inspected, show observed columns/keys for at least one 2026 session if available, compare with a 2025 DRS-positive session where useful, and state whether the blocker is FastF1-source absence, local-cache absence, or access/network absence.

## Inherited Latitude
Delegated:

- Raw FastF1/cache/source discovery through repo ingestion paths.
- Bounded schema/ingestion/test/docs changes that persist a real observed active-aero state.
- Issue comments with measured findings if credentials permit.
- Local commits in your isolated worktree.

Surface to Admiral:

- Any production physics/evo model refactor beyond exposing persisted state.
- Any direct FastF1 dependency outside ingestion/source-discovery code.
- Generated artifact/DB commits, data refresh jobs, production default flips, issue closure, merge, or PR publication.
- Any broad source/vendor decision if FastF1 lacks the signal.

## File Ownership
Sole writer for this wave:

- `.agent-work/cmdr-601-fastf1-aero-schema/RESULT.md`
- `.agent-work/cmdr-601-fastf1-aero-schema/NOTES.md` if needed
- Bounded source/docs/tests for FastF1 active-aero schema/ingestion in your isolated worktree.

Do not edit the Admiral files under `.agent-work/epic-601-physics-training/`.

## Workspace
Worktree: `C:\tmp\f1brainz-601-fastf1-aero`

Branch: `admiral-601-fastf1-aero-schema`

Base commit intended by Admiral: `370704442f67af2c93a4bbb0ff43d68d85f18288` from Wave 2, so this wave inherits the missing-state guardrail.

Add command intended by Admiral:

```powershell
git worktree add C:\tmp\f1brainz-601-fastf1-aero -b admiral-601-fastf1-aero-schema 370704442f67af2c93a4bbb0ff43d68d85f18288
```

First step, before any git operation inside the worktree:

```powershell
C:\Programs\f1Brainz\.venv\Scripts\python.exe C:\Users\fredc\.codex\skills\constellation-admiral\scripts\verify_worktree_isolation.py --here C:\tmp\f1brainz-601-fastf1-aero
```

Paste the matched worktree path in your return report.

## Inherited Context
Read before changing code:

- `docs/AGENT_GUIDE.md`
- `README.md`
- `TESTING.md`
- `docs/architecture/index.md`
- `docs/DOCUMENTATION.md`
- `docs/architecture/reference/physics-unit-conventions.md` if any telemetry/state parameter or store column is added/renamed/repurposed.

Project constraints:

- DB-backed persistence is the boundary for analysis/model code.
- Backwards compatibility is not a major concern, but old data without the active-aero field must fail clearly or load as unknown, not mislabel state.
- Strict input requirements and fail-fast behavior are preferred.
- Main checkout is dirty; do not clean it. Work only in your isolated worktree.

## Pre-empted Steps
Admiral has already established epic intent, accepted Wave 2, obtained human rejection of state-agnostic baseline, refreshed latitude for raw FastF1/schema work, and provisioned this launch order. Do not re-ask the human.

## Data Locations
Read-only local inputs from the main checkout:

- `C:\Programs\f1Brainz\data\telemetry_store.db`
- `C:\Programs\f1Brainz\data\telemetry_store_parquet\`
- `C:\Programs\f1Brainz\data\f1_data_2026.db`
- `C:\Programs\f1Brainz\data\f1_data_2025.db`
- Local FastF1 cache/config locations discoverable through existing repo loaders/config. If network/cache access is missing, report that precisely.

## Budget
- **Model tier (required):** default/lower effort is acceptable initially; escalate only if raw FastF1 API/source interpretation is ambiguous.
- **Compute/time, session-window:** bounded source probes and unit tests. No long data collection, full-season refresh, training, or generated artifact commits.

## Stop Conditions
Stop and return when one of these is true:

- You implement and commit a bounded DB schema/ingestion path for a real active-aero state with tests/docs.
- You prove FastF1/raw cache exposes no real active-aero state and produce a blocker strong enough to route externally/upstream.
- You need network/data collection permission to answer the raw-source question.
- You need a decision outside inherited latitude.

## Return Shape
Write `.agent-work/cmdr-601-fastf1-aero-schema/RESULT.md` before going idle.

Return:

- Verdict: `source-found-schema-built`, `raw-source-missing`, `blocked-needs-data-access`, or `blocked-needs-decision`.
- Raw source evidence: exact FastF1 objects/methods/cache files inspected; observed columns/keys; session(s) checked.
- Schema/ingestion impact: changed paths, semantics of new fields, migration/backfill behavior, old-data behavior.
- Tests/checks run with outcomes.
- Prediction-readiness impact: whether a non-state-agnostic 2026 baseline is now possible.
- Commit hash if committed.
- Map/docs impact and triage candidates.
- Isolation verifier output.
