# Launch Order: `cmdr-601-483499 - issues #483/#499`

## Mission

Run a lower-effort sidecar discovery pass for #483 and #499 under `constellation-commander-delegated`. Determine whether current 2026 telemetry/DB channels expose an active-aero state that can replace the historic DRS-open/closed split, and report what code/interface work is actually grounded.

Primary output is a discovery verdict. Implement only small, clearly bounded docs/tests if they directly prevent silent misapplication. Do not perform a broad `AeroDragSet` refactor in this sidecar unless Admiral explicitly refreshes scope.

## Prior-Wave Verdicts (pasted)

No prior wave in this run. This sidecar runs in parallel with #560 and must not block the historical 2019-2025 proof path unless it finds an artifact-schema risk.

Current live #483 text, refreshed 2026-07-15:

- `RegulationEra` currently has coarse booleans: `drs_enabled` and `mguk_regen`.
- 2026 active aerodynamics replaces DRS with movable front/rear wings and X/Z modes; binary DRS-open/closed split no longer maps.
- New PU changes regen/power assumptions.
- Acceptance: distinguish 2026+ aero/PU from 2014-2025; route drag/power/braking fits correctly; no silent DRS-split fit on 2026+ data; document timeline.
- Comment 2026-07-12: #499 travels with #483; train-on-2026 vs recalibrate-on-2026 is decided by A/B, not assumption.

Current live #499 text, refreshed 2026-07-15:

- Current `LongitudinalParameters.theta_D`/`theta_D_open` is a one-off DRS split.
- Proposed generic interface: named `AeroDragEstimate` and `AeroDragSet` keyed by config names.
- Control alignment assigns config labels to samples; DragView groups by label and fits CdA.
- Acceptance: `PhysicsParameterSet` carries named aero configs; existing DRS closed primary works; 2026 active-aero state names can be added without code changes.
- Comment: deferred past #492 until 2026 active aero is actionable; sequence with #483.

Important prior observation from Admiral review:

- Raw TelemetryStore Parquet diagnostic over available 2026 FP/Q sessions saw `drs` rows all `0`, while 2025 had normal codes including open states.
- This does not prove aero never changes; it means the current telemetry channel may not expose the state.
- `control_alignment.py` decodes open only codes 10, 12, 14.
- `regulation_era.py` currently sets `drs_enabled = season >= 2011`.

## Pre-Rulings

- Start with source discovery. Prefer existing FastF1/DB signals if available, but analysis/model code may not call FastF1 directly.
- If active-aero state is not observable in the current DB telemetry channel, do not invent config labels. Recommend config-agnostic 2026 handling or ingestion work.
- Do not block #560/#513 historical proof on 2026 if 2026 state is unobservable.
- A small fail-fast guard preventing DRS-split misuse on 2026 may be in scope if easy and testable.
- A full generic `AeroDragSet` refactor is not in scope for this sidecar unless the discovery finds concrete observable state labels and Admiral refreshes scope.

## Honest-Null Clause

A measured null is successful: "current DB telemetry does not expose active-aero state; #483/#499 should begin with ingestion/source discovery or 2026 guardrails, not named multi-state fitting" is complete if evidenced.

## Inherited Latitude

Delegated: read-only DB/code diagnostics; small tests/docs/guardrails in physics if they prevent silent wrongness; issue comment draft; local verification.

Must float to Admiral: full aero data model refactor, production default changes, non-DB analysis path, broad store/schema migration, merge, issue close/reopen, long detached compute.

## File Ownership

Own only #483/#499 discovery artifacts and small files under `src/physics/**`, `tests/unit/physics/**`, and relevant docs if required. Do not touch #560 files unless only reading. Stage Commander feedback locally under `.agent-work/staged-feedback/cmdr-601-483499/` in your worktree if fenced.

## Workspace

Absolute worktree path: `C:\tmp\f1brainz-601-483499`

Branch: `admiral-601-physics-483499`

Base commit: `5e8e92d7db79c0d29b6833008aece195128d0ac3`

Created by:

```powershell
git worktree add C:\tmp\f1brainz-601-483499 -b admiral-601-physics-483499 5e8e92d7db79c0d29b6833008aece195128d0ac3
```

First step before any git operation:

```powershell
C:/Programs/f1Brainz/.venv/Scripts/python.exe C:/Users/fredc/.codex/skills/constellation-admiral/scripts/verify_worktree_isolation.py --here C:\tmp\f1brainz-601-483499
```

Paste its output into your return report.

## Inherited Context

Repo constraints:

- DB is canonical for analysis. No direct FastF1 calls from analysis/model/adapter code.
- Physics may read existing DB/TelemetryStore artifacts; ingestion changes must be surfaced.
- Physics must not import evo.
- Use `C:/Programs/f1Brainz/.venv/Scripts/python.exe` if `py` is unavailable.

Relevant files to inspect:

- `src/physics/regulation_era.py`
- `src/physics/control_alignment.py`
- `src/physics/longitudinal_fit.py`
- `src/physics/physics_data_models.py`
- `src/data/telemetry_store.py`
- local telemetry artifacts under `C:\Programs\f1Brainz\data\telemetry_store_parquet\`

## Pre-empted Steps

The Admiral has already selected the sidecar role, confirmed latitude, refreshed issue text for #483/#499, and provisioned the worktree.

## Data Locations

Use the main checkout for untracked/local data artifacts if absent from the worktree:

- Main checkout: `C:\Programs\f1Brainz`
- Telemetry store: `C:\Programs\f1Brainz\data\telemetry_store.db` and `C:\Programs\f1Brainz\data\telemetry_store_parquet\`
- Season DBs: `C:\Programs\f1Brainz\data\f1_data_2025.db`, `C:\Programs\f1Brainz\data\f1_data_2026.db`

Do not modify main-checkout data files from this worktree.

## Budget

- Model tier: lower/default effort sidecar.
- Compute/time: quick source/code/DB discovery. No multi-hour batch.

## Stop Conditions

Stop and query Admiral if a source is outside current DB artifacts, if a full `AeroDragSet` refactor seems required, or if the only path forward requires schema/ingestion work.

## Return Shape

Return:

- observed 2026 aero-state availability verdict
- exact diagnostics run and key counts
- whether code/docs/tests changed
- recommended next issue comment text for #483/#499
- whether #560/#513 are affected
- staged feedback path
- isolation verifier output

Write a local result artifact at `.agent-work/cmdr-601-483499/RESULT.md` in your worktree before final response.
