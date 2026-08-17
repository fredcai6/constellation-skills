# Mission Frame

Shrunk per the template's own escape clause: this repo carries no `docs/architecture`
generated map (confirmed DEGRADED-UNPARSEABLE at `context`, receipt
`.agent-work/epic-567-door/cmdr-b/map-orientation.json`) and the change is a bounded,
single-file mechanism fix with no cross-cutting structure to frame against a map that
does not exist. No anchor ids are cited below because none exist to cite; c6 at `plan`
is waived for this reason, recorded as `plan.c6` waiver, not silently skipped.

## Intent
Close the #432 gap on the ExternalBackend crew-dispatch path: a spineless-but-fresh
result artifact must no longer verify as a clean, unqualified success. Where the caller
names a verification target, refuse; where it does not, report loudly rather than pass
silently.

## Affected Capabilities
- Crew-launch verification (`scripts/run_crew.py`, `CrewBackend.verify` /
  `ExternalBackend.dispatch`) — the sole file this lane owns this wave.

## Structural Anchors
No map exists; the read is source-derived and cited by line number in
`PROBLEM_STATEMENT.md` instead: `CrewBackend.verify` (~L1475), `ExternalBackend.dispatch`
(~L1671), `spine_terminal` (~L506, read-only reuse), `finalize_from_exit_code` (~L1212,
read-only precedent for the AND-vs-OR semantics decision).

## Governing Constraints / Assumptions
- Fence: `scripts/checklist_engine.py` and `scripts/mcp_spine_server.py` are lane A's this
  wave — read-only reuse of `checklist_engine.active_id` (already imported) is fine;
  no edits.
- `decision:test-the-shipped-path` — red-proof and green-proof both drive `RC.main`
  (the actual CLI entrypoint), never a reimplemented fixture.
- `decision:the-check-must-be-able-to-fail` — the new check must be exercised failing
  before it is exercised passing.

## Decision Anchors & Decision Pressure

Revised after a cold plan critic pass (see PLAN_ALTERNATIVES.md "Revision after cold
critic") found the first draft below did not meet the mission's own bar in the dominant
case (no `--spine` known at dispatch) and would crash on a legal `result=None` + `spine`
combo. Both are fixed in the anchors below; the critique and disposition are recorded,
not silently absorbed.

- decision:external-spine-verification-only — `ExternalBackend` accepts `--spine` for
  verification purposes; it still never binds it into an environment (nothing spawns).
  @grade: guess · leans g1-implement · settle: this run's red/green proof against `RC.main`
- decision:and-not-rescue-semantics — when both a result and a spine are in play,
  completion requires BOTH fresh result AND terminal spine (AND), the mirror image of
  `finalize_from_exit_code`'s OR/rescue semantics for the CLI backend, because here a
  fresh result must never stand in for a spine that was never driven.
  @grade: guess · leans g1-implement · settle: red-proof with fresh result + non-terminal
  spine must refuse
- decision:verify-time-spine-not-just-dispatch-time — `--verify-result` gains its own
  optional `--verify-spine <path>`, checked independently of whatever `--spine` (if any)
  was given at dispatch. Reason: at dispatch time the crew's own plan/spine path is
  usually genuinely unknown to the dispatcher (Candidate B's own rejection rationale);
  by verify time the crew has returned and typically named the path in its result, so
  the dispatcher can supply it then even when it could not at dispatch.
  @grade: guess · leans g1-implement · settle: this run's red/green proof
- decision:default-refuse-not-default-warn — SUPERSEDES the first draft's "mtime-only
  survives by default, with a warning." The dominant case (no spine target known at
  either dispatch or verify time) now REFUSES by default; a clean `completed` on mtime
  alone requires an explicit, reasoned override (`--accept-mtime-only-risk "<reason>"`),
  recorded loudly on the entry and printed to BOTH stdout and stderr (not stderr-only,
  which a redirected/CI caller could miss). This is what actually satisfies the mission's
  "impossible ... to return a clean success" bar for the common case, not just the
  opted-in one. Read against Inherited Latitude's "a user-visible default" float
  requirement: this default change is not a side effect, it IS the assigned mission
  (delete the mtime-only path) — not floated separately, though the override mechanism
  itself is recorded here for the Admiral's visibility at the wave checkpoint.
  @grade: guess · leans g1-implement · settle: red-proof default-refuse against RC.main
  with neither flag given
- decision:result-none-spine-only-guarded — `result_exists`/`result_fresh` are never
  called with `result=None` (guarded explicitly); a spine-only external dispatch
  (legal per `CrewSpec.__post_init__`) is judged solely on `spine_terminal`.
  @grade: guess · leans g1-implement · settle: dedicated test, no TypeError
- decision pressure: whether a future wave should make `--spine` mandatory (not merely
  accepted) at DISPATCH time on every external dispatch — out of latitude for this lane
  (would require coordinated handoff/doctrine changes in skills this wave does not own);
  surfaced to the Admiral as a finding, not decided here. Distinct from the verify-time
  default-refuse above, which this lane does own and does build.

## Claims / Evidence Surfaces
- claim: `CrewBackend.verify()` today is mtime-only for external — verified by running
  the existing `test_verify_result_absent_then_present_marks_completed` test, which
  passes today with zero spine evidence ever produced.

## Out of Scope
- Making `--spine` mandatory for external dispatch (structural/doctrine change, floated
  above).
- Any change to `checklist_engine.py`/`mcp_spine_server.py` (fenced, lane A).
- CliBackend behavior (already spine-aware via `finalize_from_exit_code`; untouched).
