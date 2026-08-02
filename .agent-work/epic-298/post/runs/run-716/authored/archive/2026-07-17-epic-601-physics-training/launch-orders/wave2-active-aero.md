# Launch Order: `cmdr-601-active-aero - #483/#499`

## Mission
Resolve the active-aero observability blocker for a trustworthy 2026 baseline.

The deliverable is not "fit active aero at all costs." The deliverable is a bottom-up verdict:

1. Observation: determine whether the current DB-backed telemetry path exposes any 2026 active-aero state beyond the stored `drs` channel.
2. Modeling: if no real state exists, add or specify fail-fast guardrails so 2026 physics fitting cannot silently treat all-zero `drs` as a usable DRS/open-aero lever. If a real state exists, route it through the data/ingestion boundary rather than inventing labels in physics/model code.
3. Prediction readiness: state whether a 2026 baseline can proceed now, is blocked pending ingestion/schema work, or can proceed only as an explicitly state-agnostic baseline with trust/missingness metadata.

Primary issues: #483 and #499. This wave exists because the human refreshed latitude on 2026-07-15: the 2026 baseline is the next priority, and it is not trustworthy without active-aero observability.

## Prior-Wave Verdicts (pasted)
Wave 1 #483/#499 measured-null sidecar:

- Current DB-backed 2026 telemetry does not expose active-aero state labels.
- The only aero-like field found in persisted car telemetry was `drs`.
- In the 2026 TelemetryStore aggregate, the sidecar measured 35 car sessions / 16,453,184 rows, all with `drs=0`.
- A 2025 comparison showed normal DRS activity, including 1,350,719 open-code rows.
- The sidecar posted issue comments to #483 and #499 with the scoped negative.
- This was not proof that active aero does not exist anywhere upstream. It was proof that the current stored telemetry surface used by DB-backed analysis/model code does not expose it.

Relevant current source evidence visible in the main checkout before this launch:

- `src/data/schema.sql` stores `drs INTEGER`.
- `src/data/telemetry_session.py` maps FastF1 `"DRS"` to `drs`.
- `src/data/collector.py` ingests `point.get("DRS")` into `drs`.
- `src/data/telemetry_store.py` documents and stores car stream columns including Speed, Throttle, Brake, Gear, and DRS; no active-aero wing/mode fields were visible in the quick pass.
- `src/physics/control_alignment.py` aligns `drs`; `_drs_is_open` treats FastF1 DRS codes 10/12/14 as open and 0/1/8 as closed/inactive.
- `src/physics/physics_data_models.py` has `ControlState.drs: bool = False` and `LongitudinalParameters.spec_drag_open_m2_kg` for DRS-open drag.
- `src/physics/physics_simulator.py` uses a `drs_open` track-profile column and falls back to all false.
- `src/physics/fit_store.py` stores `spec_drag_open_m2_kg`, `theta_D_source`, and `aero_identifiable`.

Wave 1 #560 trust-support result:

- Additive support/trust metadata was implemented in the isolated #560 branch for Layer 2 `EstimateStore.session_estimates`, not for ephemeris or telemetry.
- Trust labels apply to session-level capability estimate rows in `data/physics_estimates.db` table `session_estimates`, via fields such as `support_trust`, `support_reasons`, `support_min_samples`, and `support_min_neff`.
- That work remains isolated on branch `admiral-601-physics-560`; do not depend on it being in main.

## Pre-Rulings
Ruled in advance, overridable only with evidence:

- Do not invent 2026 active-aero labels such as `x_mode`, `z_mode`, `high_downforce`, or `low_drag` from speed/throttle heuristics and then train as though they were observed.
- No direct FastF1 calls from analysis, model, adapter, or predictor code. Source discovery may inspect collectors/loaders and local stored artifacts, but any production path must route through `src/data` ingestion/schema or mark missingness.
- A measured negative is success if it includes a clear source-boundary statement and guardrail/test recommendation or implementation.
- Prefer a narrow guardrail over a broad `AeroDragSet` refactor in this wave. A broad active-aero data model/schema migration must be surfaced to the Admiral before implementation.
- Do not change production/gold defaults or commit generated DB/parquet artifacts.
- If current code already fails closed for 2026 all-zero `drs`, make that explicit with tests/docs and improve the failure reason if it is ambiguous.
- If a real upstream state source is found but is not persisted, stop with an ingestion/schema plan rather than wiring a non-DB analysis shortcut.

## Honest-Null Clause
A measured negative on active-aero observability is a complete, successful deliverable if it proves the current path cannot support a 2026 active-aero baseline and prevents silent misuse. The desired bottom-up outcome is honesty: observations support modeling, and missing observations block or degrade predictions explicitly.

## Inherited Latitude
Delegated:

- Source discovery across local DB/parquet/cache-facing ingestion code.
- Local code/docs/tests for fail-fast 2026 guardrails inside `src/data`, `src/physics`, or tests if bounded and DB-respecting.
- Issue comments with measured findings, if credentials permit.
- Draft PR preparation is allowed only locally; publishing/pushing is not expected because the main checkout has unrelated ahead/behind state and `gh` auth was invalid in the prior checkpoint.

Surface to Admiral:

- Any non-DB analysis source proposal.
- Schema/ingestion migration that persists new active-aero fields.
- Broad active-aero model refactor, including replacing DRS-specific parameter surfaces with a generalized `AeroDragSet`.
- Production default flips, generated data commits, issue closure, or merge decisions.
- Any out-of-taxonomy decision.

## File Ownership
Sole writer for this wave:

- `.agent-work/cmdr-601-active-aero/RESULT.md`
- `.agent-work/cmdr-601-active-aero/NOTES.md` if needed
- Any code/docs/tests you change in your isolated worktree.

Do not edit the Admiral files under `.agent-work/epic-601-physics-training/`.

## Workspace
Worktree: `C:\tmp\f1brainz-601-active-aero`

Branch: `admiral-601-active-aero`

Base commit intended by Admiral: `5e8e92d7db79c0d29b6833008aece195128d0ac3`

Add command intended by Admiral:

```powershell
git worktree add C:\tmp\f1brainz-601-active-aero -b admiral-601-active-aero 5e8e92d7db79c0d29b6833008aece195128d0ac3
```

First step, before any git operation inside the worktree: run the Admiral isolation verifier against your worktree:

```powershell
C:\Programs\f1Brainz\.venv\Scripts\python.exe C:\Users\fredc\.codex\skills\constellation-admiral\scripts\verify_worktree_isolation.py --here C:\tmp\f1brainz-601-active-aero
```

Paste the matched worktree path in your return report.

## Inherited Context
Read before changing code:

- `docs/AGENT_GUIDE.md`
- `README.md`
- `TESTING.md`
- `docs/architecture/index.md`
- `docs/DOCUMENTATION.md`
- If physics parameters/store columns are added, renamed, or repurposed: `docs/architecture/reference/physics-unit-conventions.md`

Project constraints:

- The database is the single source for analysis/model code. No direct FastF1 calls from evo, analysis, scorers, adapters, or physics model consumers.
- Python is normally invoked as `py` on Windows, but the Admiral verified the venv path works: `C:\Programs\f1Brainz\.venv\Scripts\python.exe`.
- Main checkout is dirty with unrelated work. Do not use or clean it. Work only in your isolated worktree, reading untracked data artifacts from the main checkout paths listed below when needed.
- Backwards compatibility is not a major concern; prefer one clear fail-fast method over compatibility shims.
- Strict input requirements are preferred. Failure modes should be clear and tested.

## Pre-empted Steps
Admiral has already established the epic intent, refreshed latitude, selected #483/#499 as Wave 2, and provisioned the launch order. Do not re-ask the human. Cite this launch order for delegated decisions.

## Data Locations
Worktrees may not contain untracked local DB/parquet artifacts. Use these read-only inputs from the main checkout:

- `C:\Programs\f1Brainz\data\telemetry_store.db`
- `C:\Programs\f1Brainz\data\telemetry_store_parquet\`
- `C:\Programs\f1Brainz\data\f1_data_2026.db`
- `C:\Programs\f1Brainz\data\f1_data_2025.db`
- Any local FastF1 cache-facing code must be inspected through repo loaders/collectors, not used as a production model dependency.

## Budget
- **Model tier (required):** default/lower effort is acceptable for source discovery plus bounded guardrails; escalate only if the active-aero source surface is ambiguous after local evidence.
- **Compute/time, session-window:** keep diagnostics read-only and bounded. Avoid long retraining, data collection, or generated artifact updates. Focused tests first; broader physics/data tests only if touched interfaces justify it.

## Stop Conditions
Stop and return when one of these is true:

- You have a code/test/doc commit or patch that prevents silent 2026 active-aero misuse and a clear verdict.
- You prove a real active-aero source exists but requires schema/ingestion migration.
- You prove no current local source exists and can state the exact boundary where the signal disappears.
- You need a decision outside inherited latitude.
- A required data artifact is missing or unreadable and no local substitute can answer the mission.

## Return Shape
Write `.agent-work/cmdr-601-active-aero/RESULT.md` before going idle.

Return:

- Verdict: `source-found`, `source-missing-guarded`, or `blocked-needs-decision`.
- Observation evidence: exact tables/files/columns inspected and counts where relevant.
- Modeling impact: what code currently does for 2026 all-zero/unknown aero state, and what you changed or recommend.
- Prediction-readiness impact: whether a 2026 baseline can proceed, and under what trust/missingness label.
- Changed paths and commit hash if you commit locally.
- Tests/checks run with outcomes.
- Map/docs impact.
- Triage candidates, if any.
- Isolation verifier output.
