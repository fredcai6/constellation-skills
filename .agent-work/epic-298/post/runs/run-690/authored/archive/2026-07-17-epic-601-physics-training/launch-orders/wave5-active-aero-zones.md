# Launch Order: `cmdr-601-active-aero-zones - #483/#499`

## Mission
Build the reference layer for when 2026 Driver Adjustable Bodywork modes are allowed.

The human rejected a state-agnostic 2026 baseline but identified a different observable: FIA/F1 published mode-allowance zones. Your mission is to create the bottom-up reference surface for these zones:

1. Find the best published source(s) for 2026 Driver Adjustable Bodywork Activation Zones, Low Grip Activation Zones, Detection Line, Activation Line, and related mode-allowance limits.
2. Build a bounded DB-backed or artifact-backed reference representation with provenance and trust.
3. Add focused tests/docs so later physics/CdA identification can consume “allowed-zone windows” without confusing them with per-car observed state.

This is not a per-car telemetry task. It creates the track/session/event opportunity map.

## Prior-Wave Verdicts (pasted)
Wave 2:

- Persisted DB/parquet telemetry exposes only `drs`.
- 2026 parquet evidence: 35 sessions / 16,453,184 rows / 0 DRS open-code rows / 0 nonzero DRS rows.
- Local commit `370704442f67af2c93a4bbb0ff43d68d85f18288` pins all-zero DRS as `no_drs_lever` and documents missing-state interpretation.

Wave 3:

- FastF1 offline `session.car_data`, `session.pos_data`, `session.laps`, and `lap.get_telemetry()` for 2026 Miami Q and 2026 Canada Q expose only `DRS` as aero-like state, all sampled `0`.
- 2025 Bahrain Q comparator exposes nonzero DRS codes on the same surfaces.

Wave 4:

- Raw `.ff1pkl` payload internals and local FastF1 3.8.3 parser/API source were audited for 2026 Miami Q, 2026 Canada Q, and 2025 Bahrain Q.
- Candidate broad hits were existing `DRS`, `Status`, `Position`, config/cache/source mechanics.
- Zero active-like fields for wing/flap/drag/deployment/active/xmode/zmode or equivalent.
- No observed per-car active-aero state source exists in current local FastF1/cache evidence.

Regulatory evidence checked by Admiral:

- FIA 2026 Sporting Regulations B7.1.1 define Driver Adjustable Bodywork deactivated/fully activated/partially activated states.
- B7.1.1(e) says the FIA provides competitors with relevant information regarding Activation Zones for each circuit, including full-activation zones and Low Grip Activation Zones, no less than four weeks before the Competition.
- B7.1.1(f) says the start of each defined Activation Zone is marked by signage.
- B7.2.1(b) says the FIA provides competition-specific Detection Gap, Detection Line, Activation Line, and related energy-deployment limitations.

## Pre-Rulings
- Treat `allowed zone` as observed/published track/session/event reference data, not per-car mode state.
- Do not call this `aero_state_observed`; name it as eligibility/opportunity/allowed-zone data.
- Preferred field concepts:
  - `mode_family`: driver_adjustable_bodywork
  - `allowance_type`: full_activation, partial_low_grip_activation, overtake_activation, detection_line, activation_line
  - `distance_start_m`, `distance_end_m`, nullable when only a line is represented
  - `lap_distance_m` for lines
  - `session_scope`: all, LTCS, TTCS, qualifying, race, low_grip, etc. as source supports
  - `source_url`, `source_title`, `source_date`, `source_section`, `trust`
- If event-specific activation-zone documents are not publicly available, still build the reference interface and document the source gap. Seed only from source-backed facts, not guesses.
- Existing DRS-zone code may be useful structurally but do not reuse `drs_open` semantics for active aero without an explicit adapter boundary.
- Do not commit generated DBs/parquet. Source/docs/tests/code are allowed. Small checked-in fixture/reference examples are allowed if source-backed and reviewed.

## Honest-Null Clause
A measured negative is acceptable only if it leaves a usable interface/plan: e.g. “FIA rules require zone publication, but public event docs are not accessible; here is the schema/loader and source-ingestion contract for when documents are available.”

## Inherited Latitude
Delegated:

- Public web/source discovery for FIA/F1 event documents.
- Bounded code/docs/tests for an active-aero allowed-zone reference layer.
- Local commits in the isolated worktree.
- Worktree-local prototype scripts.

Surface:

- Paid/private data source use.
- Generated DB/artifact commits.
- Production default flips.
- Broad physics fitting/model promotion.
- GitHub issue publication.

## File Ownership
Sole writer:

- `.agent-work/cmdr-601-active-aero-zones/RESULT.md`
- `.agent-work/cmdr-601-active-aero-zones/source-findings.md`
- Any bounded source/docs/tests for the reference layer.

Do not edit Admiral files.

## Workspace
Worktree: `C:\tmp\f1brainz-601-aero-zones`

Branch: `admiral-601-aero-zones`

Base commit: `370704442f67af2c93a4bbb0ff43d68d85f18288`

Intended add command:

```powershell
git worktree add C:\tmp\f1brainz-601-aero-zones -b admiral-601-aero-zones 370704442f67af2c93a4bbb0ff43d68d85f18288
```

First step:

```powershell
C:\Programs\f1Brainz\.venv\Scripts\python.exe C:\Users\fredc\.codex\skills\constellation-admiral\scripts\verify_worktree_isolation.py --here C:\tmp\f1brainz-601-aero-zones
```

## Inherited Context
Read:

- `docs/AGENT_GUIDE.md`
- `README.md`
- `TESTING.md`
- `docs/architecture/index.md`
- `docs/DOCUMENTATION.md`
- Relevant physics docs: `docs/physics/overview.md`, `docs/physics/measurement_model.md`, `docs/architecture/reference/physics-unit-conventions.md`

Useful local seams to inspect:

- `src/physics/ribbon.py` and `docs/architecture/decisions/ideal-lap-sim-two-sided-evaluator.md` for existing DRS-zone mask design.
- `src/physics/physics_simulator.py` for track-profile `drs_open` consumption.
- `src/data/schema.sql` and `src/data/database/` if you choose DB-backed persistence.
- `docs/architecture/packets/data.md` and `docs/architecture/packets/physics.md` for map wording.

## Pre-empted Steps
Admiral already established the source distinction: per-car state is missing, but published activation-zone eligibility is valid reference data. Do not re-ask the human.

## Data Locations
Read-only local:

- `C:\Programs\f1Brainz\data\telemetry_store_parquet\`
- `C:\Programs\f1Brainz\data\telemetry_store.db`
- `C:\Programs\f1Brainz\data\f1_data_2026.db`
- `C:\Programs\f1Brainz\data\telemetry\`

Primary web sources to start with:

- FIA 2026 Sporting Regulations Section B, B7.1/B7.2: `https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_b_sporting_-_iss_06_-_2026-04-28.pdf`
- FIA 2026 Technical Regulations Section C for Front Wing/Rear Wing mode definitions.
- FIA/F1 race director/event notes, circuit maps, or official competition documents for event-specific activation zones.

## Budget
- **Model tier (required):** lower/default effort.
- **Compute/time:** overnight local/web research plus focused tests. No full pipeline, training, or data refresh.

## Stop Conditions
Stop when:

- You produce a tested reference layer and source-backed seed data or fixtures.
- You prove event-zone documents are not publicly accessible enough and produce an interface/contract plus source-findings.
- You need paid/private source access.
- You need a decision outside inherited latitude.

## Return Shape
Write `.agent-work/cmdr-601-active-aero-zones/RESULT.md`.

Return:

- Verdict: `reference-built`, `reference-interface-built-source-gap`, or `blocked-needs-source-access`.
- Sources found and rejected/accepted.
- Changed paths and commit hash if any.
- Tests/checks run.
- Exact semantics of the reference layer.
- Guidance for the next CdA-identification Commander.
- Isolation verifier output.
