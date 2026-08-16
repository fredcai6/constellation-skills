# Mission Frame

Map orientation returned DEGRADED-UNPARSEABLE (`.agent-work/cleanup-c-liveness-rail/map-orientation.json`): `map/ids.jsonl` is empty repo-wide at baseline `a69bbac4` (confirmed by rebuilding the map locally — `python -m scripts.code_map build` produced byte-identical output, `ids: 0`), so there are zero authored anchor ids anywhere in this corpus to cite. This frame is built from the launch order's own file:line citations plus a direct read of the cited files (the substitutes hash-pinned at orient time), not from a map, per the Honest-Null Clause and the DEGRADED-mode contract.

## Intent
Two liveness/attribution fixes, both diagnosis-only-need-implementation per the launch order's Pre-empted Steps:

1. **#599** — `active_duplicate()` (`scripts/run_crew.py:253`) currently blocks/frees a launch off a raw `status` string with no PID or heartbeat corroboration. Replace the boolean read with a three-state corroborated liveness query (`active` / `stale` / `unknown`, per **three-states-not-two** (pre-ruling)) that fails toward `active` when it cannot corroborate (**fail-toward-active** (pre-ruling)), using the existing `process_alive()` seam (`scripts/run_crew.py:864`) for PID-bearing entries and a bounded heartbeat-age window for PID-less `external` entries (**pidless-means-heartbeat** (pre-ruling)).
2. **#549** — `decide_stop` (`scripts/hooks/spine_rail.py:1351`), via `session_view` (`:515`) and `_entry_mid_flight_view`/`_foreign_worktree` (`:1323`/`:640`), renders a subordinate's own next imperative into an orchestrator's Stop-block reason whenever the orchestrator's cwd happens to equal that subordinate's recorded worktree — because `session_view` merges every per-agent-keyed (`sid#agent_id`) entry into the same dict as the bare-`sid` entries, discarding which key sourced each one. Keep the block (safe half); change the rendered reason for an entry reachable only through a per-agent key to name the owning session instead of relaying its imperative (**keep-the-block-drop-the-imperative** (pre-ruling)).

## Affected Capabilities
- **Crew launch-refusal / duplicate guard** (`scripts/run_crew.py`) — the predicate a fresh `launch` call and a human/Commander reading `recover_crews` output both rely on to know whether a gate/role/worktree slot is already held.
- **Recovery classification** (`scripts/recover_crews.py`, read-only this lane) — `classify_entry` already does PID+result liveness classification for its own 7-state read; it is the working reference shape for "classify from status + pid + result" existing at all, not itself in scope (not in File Ownership). Its pid=None handling (`alive(None)` is always `False` → routes to `RESUMABLE`/`NEEDS_ABANDON`, never `ACTIVE`) is the OPPOSITE of **fail-toward-active** (pre-ruling) and must NOT be ported for the pid-less case — confirmed by cold critic review (see `PLAN_CONVERGENCE.md`). #599's pid-less/external branch is a deliberate divergence from this precedent, not a reuse of it.
- **Stop-hook mid-flight block** (`scripts/hooks/spine_rail.py`, `decide_stop`) — the rail that refuses a dishonest turn-end while a spine gate is still open; must keep refusing exactly as often, only the rendered reason for a subordinate-owned entry changes.

## Examples / Events
- The two phantom-registry incidents quoted verbatim in the launch order (`epic-568-441` reading a stale `external` entry with `pid: null`, `status: running`, `last_heartbeat == started_at`; `tc1-windows-path-form` reading a vanished-PID entry with no registry row at all) are the concrete #599 failure shapes to reproduce and fix, sourced from `.agent-work/archive/2026-08-15-triage-candidates/auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md`.
- The `crew-verdict-and-door` observation in the same document — the defect does not fire on short (foreground-returning) dispatches, only long ones — sets the corroboration window's floor: it must not fire on the normal duration of a healthy long-running crew.

## Structural Anchors
- `scripts/run_crew.py` — `active_duplicate()` (`:253`), `process_alive()` (`:864`), `ACTIVE_STATUSES` (`:47`), the external-backend PID-less entry construction (`:1393`), the one launch-refusal call site (`:1800`).
- `scripts/recover_crews.py` — `classify_entry()` (`:51`), read for precedent only; not owned this lane.
- `scripts/hooks/spine_rail.py` — `session_view()` (`:515`), `_foreign_worktree()` (`:640`), `_entry_mid_flight_view()` (`:1323`), `_mid_flight_reason()` (`:1303`), `decide_stop()` (`:1351`), `binding_key()` (`:467`, the write-side per-agent key composer — read-only reference for what `session_view` must un-merge).
- `tests/test_crew_launcher.py`, `tests/test_spine_rail.py` — existing coverage to extend, not replace.

## Governing Constraints / Assumptions
- **Fenced, do not touch:** `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/mcp_spine_server.py`, `.mcp.json` (lane A/B ownership).
- **`decide_stop` must refuse exactly the same stops it refuses today** — #549 changes rendered text only, never gating outcome (float any change that would let a currently-blocked stop through).
- **No auto-reaping or auto-abandonment** — **no-abandonment-by-inference** (pre-ruling); a `stale` verdict is reported, never acted on by this lane.
- **`os.kill(pid, 0)` is POSIX-only**; `process_alive()`'s injectable seam must not be broken, and Windows behavior must be stated even though CI (a single `windows-latest` job, red at baseline) cannot confirm it locally.
- **Clear `__pycache__` before every measurement** (#597); suite command is `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT py -m pytest -q`.

## Decision Anchors & Decision Pressure
Pre-ruled by the launch order (not this lane's to regrade downward, only to apply):
- **fail-toward-active** (pre-ruling) — uncorroborated liveness reports `active`, never free.
  `@grade: settled/human · leans g1-implement`
- **three-states-not-two** (pre-ruling) — the query returns `active` / `stale` / `unknown`, never a collapsed boolean.
  `@grade: settled/measured · leans g1-implement`
- **pidless-means-heartbeat** (pre-ruling) — an `external` entry's corroboration is heartbeat age against a bound window; the window's number is this lane's to pick and justify.
  `@grade: guess · leans g1-implement · settle: pick the window from the two observed phantoms (last_heartbeat == started_at, hours/days stale) and the one healthy long-running crew's observed heartbeat cadence; state the chosen number and why`
- **keep-the-block-drop-the-imperative** (pre-ruling) — #549 changes the rendered reason only, never the gating outcome.
  `@grade: settled/human · leans g2-implement`
- **no-abandonment-by-inference** (pre-ruling) — reporting `stale` is the deliverable; reaping is out of scope (#552).
  `@grade: settled/human · leans g1-implement`

New decision pressure this run must still resolve (not pre-ruled):
- `decision pressure: the exact heartbeat-window number for pidless corroboration` — the `settle:` experiment above; resolved during g1-implement from the registry evidence in `.agent-work/archive/*/crew-runs*.json` and the phantom-signature document, then graded `settled/measured` and recorded in code + evidence, not floated (within inherited latitude: "the corroboration window for pid-less entries" is explicitly listed under Inherited Latitude).
- `decision pressure: whether the new three-state query becomes a new function alongside `active_duplicate()` or replaces its internals` — resolved during g1-implement plan-alternatives (below); within inherited latitude ("the shape of the three-state result").
- `decision pressure: how session_view's provenance is carried into decide_stop without changing session_view's existing return contract` (two existing callers, one of which — `decide_session_start` — is out of scope for #549's fix) — resolved during g2-implement plan-alternatives; within inherited latitude ("how provenance travels out of session_view").

## Claims / Evidence Surfaces
- `tests/test_crew_launcher.py::test_active_duplicate_...` (new) — both #599 directions: a dead-PID entry that stops reading as active, and a live crew that keeps reading as active, using the real `crew-runs.json` shape (per Return Shape item 1).
- `tests/test_spine_rail.py::test_session_view_merges_...` (existing, `:493`) — must keep passing unchanged (session_view's existing dict-shape contract for `decide_session_start`); new test(s) alongside it for the orchestrator-in-subordinate-worktree #549 scenario, asserting both that the stop is still blocked AND that the reason names the owning session (per Return Shape item 2).
- Full clean-env, cache-cleared suite at this lane's published head, plus a `main` baseline re-measured at gate time (Return Shape item 3) — the merge-gate evidence shape from Inherited Context.

## Map Confidence / Staleness / Disputes
- The full architecture map is DEGRADED-UNPARSEABLE repo-wide (0 authored anchors; see Intent). This is a corpus-wide state, not specific to `run_crew.py` or `spine_rail.py`, and predates this lane (confirmed identical before/after a local rebuild). Altering the plan for it: none needed — the launch order already supplies file:line mechanism citations in place of map anchors, and this frame cites the substitute files directly instead of anchor ids, per the DEGRADED-mode contract. Recorded as a triage candidate at the triage step (map anchor authoring is corpus-wide work, clearly out of this lane's two-file scope) rather than escalated to the Admiral now.

## Out of Scope
- `scripts/checklist_engine.py`, `scripts/gauge_reader.py`, `scripts/hooks/gauge_writer_hook.py`, `scripts/mcp_spine_server.py`, `.mcp.json` — fenced to lanes A/B.
- Auto-reaping, auto-abandonment, or any change that would make `decide_stop` allow a stop it currently blocks — must float, not implement.
- `decide_session_start`'s own use of `session_view` (`spine_rail.py:1444`) — same merge mechanism, but the launch order's #549 citation and mission are specifically about the Stop hook; changing `decide_session_start`'s rendering too is a wider blast radius than named. Left unchanged; noted as a triage candidate if the #549 fix's provenance mechanism turns out to compose cleanly with it.
- Publication (merge) — park at `archive`; the Admiral merges.
- Corpus-wide map-anchor authoring (see Map Confidence above).
