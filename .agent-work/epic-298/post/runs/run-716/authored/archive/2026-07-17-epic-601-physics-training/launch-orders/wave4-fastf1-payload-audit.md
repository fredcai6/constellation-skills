# Launch Order: `cmdr-601-fastf1-payload-audit - #483/#499`

## Mission
Audit the raw FastF1/cache payload boundary more exhaustively before the Admiral declares active-aero source absence.

Wave 3 checked standard FastF1 session objects and `aero`/`drs`-named surfaces. That is useful but not broad enough for a final blocker because an observed active-aero state could theoretically be named `mode`, `flap`, `wing`, `state`, `drag`, `deployment`, or live in lower-level cache payload internals before FastF1 exposes it as `session.car_data`.

Your mission:

1. Inspect all cached FastF1 payload structures for at least the same 2026 sessions and the 2025 comparator used in Wave 3.
2. Inspect local FastF1 package/parser/source surfaces available in the venv for car-data, timing, timing app, session status, and cache payload parsing.
3. Produce either a real observed active-aero source candidate with exact path/key/semantics, or a stronger `raw-payload-source-missing` blocker that names every payload/API surface checked.

Do not add schema unless you find a real observed active-aero field. If found, stop with a schema design sketch unless it is clearly bounded and safe to implement inside the wave.

## Prior-Wave Verdicts (pasted)
Wave 2:

- Persisted DB/parquet telemetry exposes only `drs`; 2026 parquet has 35 sessions / 16,453,184 rows / 0 DRS open-code rows / 0 nonzero DRS rows.
- Commit `370704442f67af2c93a4bbb0ff43d68d85f18288` pins all-zero DRS as `no_drs_lever` and documents 2026 missing-state interpretation.
- The human rejected a state-agnostic 2026 baseline.

Wave 3:

- FastF1 offline `session.car_data`, `session.pos_data`, `session.laps`, and `lap.get_telemetry()` were probed for 2026 Miami Q, 2026 Canada Q, and 2025 Bahrain Q.
- 2026 Miami Q and Canada Q exposed only `DRS` as an aero-like state, sampled all `0`.
- 2025 Bahrain Q exposed the same surface but with nonzero DRS codes (`0`, `8`, `9`, `10`, `12`, `14`), proving the probe sees DRS when upstream carries it.
- Cached payload names included `car_data.ff1pkl`, `driver_info.ff1pkl`, `position_data.ff1pkl`, `session_info.ff1pkl`, `session_status_data.ff1pkl`, `timing_app_data.ff1pkl`, `track_status_data.ff1pkl`, `weather_data.ff1pkl`, and `_extended_timing_data.ff1pkl`.
- Limitation: the probe did not exhaustively inspect every raw `.ff1pkl` payload's nested keys/columns/strings, and searched primarily `aero`/`drs` names.

## Pre-Rulings
- Search broader candidate names: `aero`, `drs`, `wing`, `flap`, `mode`, `state`, `drag`, `deployment`, `active`, `xmode`, `zmode`, `config`, `position`, and any obvious FastF1/live-timing state names found during inspection.
- Do not infer labels from speed/throttle/brake/gear. Only observed fields count.
- Production model/predictor code must not depend on FastF1 directly.
- Do not add placeholder columns for missing sources.
- No generated data commits, production defaults, issue closure, merge, or PR publication.

## Honest-Null Clause
A stronger null is successful if it exhaustively states: local FastF1 version/source surfaces checked, payload files inspected, nested keys/columns enumerated or summarized, matching candidate fields found/not found, and remaining uncertainty.

## Inherited Latitude
Delegated:

- Local FastF1 package/source inspection.
- Read-only cache payload inspection and temporary worktree-local probe scripts.
- Local docs/tests/schema sketch if a real source is found.
- Issue comments with measured findings if credentials permit, but do not close issues.

Surface to Admiral:

- Any source requiring network fetch or external vendor data.
- Any schema implementation with ambiguous semantics.
- Any direct FastF1 dependency outside ingestion.

## File Ownership
Sole writer:

- `.agent-work/cmdr-601-fastf1-payload-audit/RESULT.md`
- `.agent-work/cmdr-601-fastf1-payload-audit/payload-audit.json`
- Worktree-local probe scripts under `.agent-work/cmdr-601-fastf1-payload-audit/`

Do not edit Admiral files.

## Workspace
Worktree: `C:\tmp\f1brainz-601-fastf1-payload-audit`

Branch: `admiral-601-fastf1-payload-audit`

Base commit: `370704442f67af2c93a4bbb0ff43d68d85f18288`

Intended add command:

```powershell
git worktree add C:\tmp\f1brainz-601-fastf1-payload-audit -b admiral-601-fastf1-payload-audit 370704442f67af2c93a4bbb0ff43d68d85f18288
```

First step:

```powershell
C:\Programs\f1Brainz\.venv\Scripts\python.exe C:\Users\fredc\.codex\skills\constellation-admiral\scripts\verify_worktree_isolation.py --here C:\tmp\f1brainz-601-fastf1-payload-audit
```

## Inherited Context
Read:

- `docs/AGENT_GUIDE.md`
- `README.md`
- `TESTING.md`
- `docs/architecture/index.md`
- `docs/DOCUMENTATION.md`

Use `C:\Programs\f1Brainz\.venv\Scripts\python.exe` for Python if needed.

## Pre-empted Steps
Admiral already established intent, accepted Wave 2 guardrail, received Wave 3 session-object null, and narrowed this wave to payload/source audit. Do not ask the human.

## Data Locations
Read-only local cache and data inputs:

- `C:\Programs\f1Brainz\data\telemetry\`
- `C:\Programs\f1Brainz\data\telemetry_store_parquet\`
- `C:\Programs\f1Brainz\data\telemetry_store.db`
- `C:\Programs\f1Brainz\data\f1_data_2026.db`
- `C:\Programs\f1Brainz\data\f1_data_2025.db`

Sessions to include at minimum:

- 2026 Miami Q
- 2026 Canada Q
- 2025 Bahrain Q comparator

## Budget
- **Model tier (required):** lower/default effort.
- **Compute/time:** bounded local read-only probes. No network unless you stop and request it.

## Stop Conditions
Stop when:

- You find a real observed active-aero candidate field and can name path/key/type/semantics.
- You complete exhaustive local payload/source audit and find none.
- You need network/external source access.

## Return Shape
Write `.agent-work/cmdr-601-fastf1-payload-audit/RESULT.md`.

Return:

- Verdict: `raw-payload-source-found`, `raw-payload-source-missing`, or `blocked-needs-network-external-source`.
- Payload/API/source evidence.
- Candidate field table, even if empty.
- Exact residual uncertainty.
- Whether DB schema work is justified.
- Tests/probes run.
- Isolation verifier output.
