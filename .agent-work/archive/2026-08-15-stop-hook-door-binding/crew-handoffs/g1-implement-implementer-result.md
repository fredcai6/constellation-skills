# Implementation Result

## Assigned gate
`g1` (execute.json: `g1-implement`) — door binding: record MCP door claim/release, narrow PostToolUse matcher, RED+CONTROL+fail-open tests

## Completed slice
`handle_post_tool_use` now recognizes a door-issued `mcp__spine__spine_lease` claim/release (dispatched to a new `_handle_door_lease` helper on `data.get("tool_name") == DOOR_LEASE_TOOL_NAME`, before the existing Bash command-extraction logic) and records/removes a session→spine binding equivalent in shape to the Bash-path entry, resolving the claimed spine from this process's own `SPINE_FILE`/`SPINE_SESSION` environment. A narrow `PostToolUse` matcher for `mcp__spine__spine_lease` was added to `.claude/settings.json` so the hook actually fires for a door call. `decide_stop`/`_mid_flight_reason` are unchanged — they now refuse a mid-flight door-claimed turn-end because a binding exists.

## Scope
**Files changed:**
- `scripts/hooks/spine_rail.py`
- `tests/test_spine_rail.py`
- `.claude/settings.json`

**Specific exclusions touched:** no — `scripts/checklist_engine.py`, `scripts/run_crew.py`, `scripts/apply_episode_delta.py`, `scripts/verify_episode_observations.py`, `scripts/hooks/gauge_writer_hook.py`, `.mcp.json` untouched; `_mid_flight_reason`/`decide_stop`/`decide_session_start` untouched; `Stop`/`SessionStart`/`gauge_writer_hook` entries of `.claude/settings.json` untouched.

## Behavior changed
yes — `handle_post_tool_use` gains a second, additive binding-writing source (the door). The Bash `checklist_engine.py` claim/release path is byte-for-byte unchanged in behavior (its code path is unreached for a door payload; existing tests pass with unmodified assertions).

## Map Impact
- **Structural anchors touched:** `scripts/hooks/spine_rail.py::handle_post_tool_use` — gained a dispatch to a new sibling helper `_handle_door_lease`; the Bash-path body below the dispatch is untouched. New module-level constants `DOOR_LEASE_TOOL_NAME` and `PATH_SOURCE_DOOR_ENV`. `.claude/settings.json` `PostToolUse` array gained one matcher entry.
- **Capabilities added/changed/affected:** session→spine binding store now has two recording sources (Bash command + MCP door claim/release), both feeding the same store `decide_stop` reads.
- **Constraints/assumptions touched:** fail-open contract honored (every new code path returns `{}`, wrapped in its own `try/except Exception: return {}`); no new subprocess; no new imports (reuses `os`, `Path` already imported).
- **Decision candidates / resolved decisions:** door-binding source of truth (resolve from this process's own `SPINE_FILE`/`SPINE_SESSION`, reusing `_is_valid_claim_target` unchanged) — confirmed against `scripts/mcp_spine_server.py`'s own `SPINE_FILE`/`SPINE_SESSION` read; matcher scope `mcp__spine__spine_lease` only — confirmed this repo's `.mcp.json` registers exactly one MCP server (`spine`); `mcp__spine-epic__spine_lease` is not reachable from this repo's own configuration, left as the recorded out-of-scope observation below.
- **Triage candidates:** `map/INDEX.md` is DEGRADED-UNPARSEABLE for this area (per-module pages absent) — already a recorded triage candidate, not something this gate fixes.

## Test mode
**Required:** `test-first`
**Satisfied:** yes — RED captured against the unmodified code, then the fix made it GREEN.

## Evidence

```bash
python -m pytest -q tests/test_spine_rail.py
```
**Result:** pass — `139 passed, 1 skipped in 1.27s` (pre-change baseline was `123 passed, 1 skipped`; +16 new door-path tests, no regressions, no existing assertion changed).

**New test names added (16), mapped to RED/GREEN/CONTROL/fail-open:**
- `test_stop_door_claimed_mid_flight_blocks` — RED (captured genuinely FAILING against pre-fix code) + GREEN (passes post-fix): the door-claimed mid-flight case is refused by `decide_stop`.
- `test_post_door_claim_writes_binding` — GREEN: binding shape (`spine`, `engine_session`, `worktree`, `claimed_at`, `path_source`) matches the Bash-path entry.
- `test_post_door_claim_records_absent_spine_session_as_is` — GREEN: `SPINE_SESSION` absent is recorded as `None`, never fabricated.
- `test_post_door_release_removes_binding_and_nudge` — GREEN: a door release removes the exact bound entry and resets the nudge ledger, mirroring the Bash release.
- `test_stop_door_claimed_terminal_released_lease_allows` — CONTROL: terminal spine + released lease, door-claimed, not refused.
- `test_stop_door_claimed_foreign_worktree_not_blocked` — CONTROL: door-claimed in a subagent's own worktree, parent stops from a different cwd, not refused.
- `test_stop_door_claimed_unreadable_spine_allows` — CONTROL: successfully door-claimed, spine then deleted, not refused.
- `test_stop_door_claimed_blocked_status_honest_stop_allows` — CONTROL: door-claimed spine with an honestly-blocked active gate, not refused.
- `test_post_door_claim_missing_tool_input_records_nothing` — fail-open: no `tool_input` key at all.
- `test_post_door_claim_non_dict_tool_input_records_nothing` — fail-open: `tool_input` is a string, not a dict.
- `test_post_door_claim_missing_action_records_nothing` — fail-open: `tool_input` present but no `action` key.
- `test_post_door_claim_unrecognized_action_records_nothing` — fail-open: `action == "heartbeat"` (a real door action this gate does not bind on).
- `test_post_door_claim_missing_spine_file_records_nothing` — fail-open: `SPINE_FILE` absent from the environment.
- `test_post_door_claim_non_checklist_spine_file_records_nothing` — fail-open: `SPINE_FILE` resolves to a real, readable JSON file with no `items` list.
- `test_post_door_claim_spine_file_outside_agent_work_records_nothing` — fail-open: `SPINE_FILE` resolves outside `.agent-work/<work-id>/` containment.
- `test_post_door_never_raises_on_junk` — fail-open (fuzz): 7 malformed/edge shapes, asserts `{}` and no raise for each, with and without `SPINE_FILE` set.

## TDD evidence, if required

- Failing test observed (RED, against unmodified `scripts/hooks/spine_rail.py`):
  ```
  $ python -m pytest -q -k test_stop_door_claimed_mid_flight_blocks
  F                                                                        [100%]
  =================================== FAILURES ===================================
  ___________________ test_stop_door_claimed_mid_flight_blocks ___________________
  ...
      out = sr.handle_post_tool_use(_door("claim", cwd=str(proj)), proj)
      assert out == {}
      result = sr.decide_stop({"session_id": "s1"}, proj)
  >       assert result.get("decision") == "block"
  E       AssertionError: assert None == 'block'
  E        +  where None = <built-in method get of dict object at ...>('decision')
  E        +    where <built-in method get of dict object at ...> = {}.get

  tests/test_spine_rail.py:2726: AssertionError
  =========================== short test summary info ============================
  FAILED tests/test_spine_rail.py::test_stop_door_claimed_mid_flight_blocks - A...
  1 failed, 3052 deselected in 0.69s
  ```
- Passing test observed (GREEN, after the fix):
  ```
  $ python -m pytest -q -k test_stop_door_claimed_mid_flight_blocks
  .                                                                        [100%]
  1 passed, 3052 deselected in 0.67s
  ```
- Refactor while green: no — the implementation was written once to the final shape; no post-green refactor pass was needed.

## Docs/contracts touched
- none — `scripts/mcp_spine_server.py`'s `SPINE_FILE`/`SPINE_SESSION` contract was read-only reference, not edited.

## Assumptions
- `os.environ.get("SPINE_FILE")` at hook-invocation time reliably carries the value the door process itself reads (`scripts/mcp_spine_server.py:146`, `SPINE = Path(os.environ["SPINE_FILE"]).resolve()`) — both processes share the harness-launched environment. Not independently re-verified against a live door invocation in this gate (out of reach of a unit test); flagged per the handoff's stop condition, but nothing observed contradicts it — this was a `@grade: settled/measured` decision already made at the anchors level, not re-opened here.
- A door `action` of `"heartbeat"` never needs a binding write (heartbeats only refresh the lease, they do not claim/release a spine) — treated identically to any other unrecognized action, i.e. `{}`, no binding.

## Stop conditions hit
- none — no need arose to edit `_mid_flight_reason`/`decide_stop`; no existing Bash-path test needed a changed assertion; no new subprocess was required; `SPINE_FILE`/`SPINE_SESSION` behaved as documented in `scripts/mcp_spine_server.py` throughout.

## Out-of-scope observations
- `map/INDEX.md` is DEGRADED-UNPARSEABLE for this area (per the handoff's own confidence flag) — recorded here again for Triage, not fixed by this gate.
- `mcp__spine-epic__spine_lease` is a distinct, unregistered-in-this-repo tool name (this repo's `.mcp.json` registers exactly one MCP server, `spine`) — confirmed not reachable from this repo's own configuration; per the handoff's decision anchor, out of scope this gate, `settle:` deferred to a later run that finds it reachable.

## Workflow Feedback
- **Handoff gaps:** none — confirmed after review: task, protected intent, test mode, close criteria, allowed scope, specific exclusions, constraints, map anchors, deliverable-path checks, required evidence, wiring grep, verification commands, authority, and stop conditions were all present and consistent with the source as read.
- **Context rediscovered:** the exact payload shape for a real PostToolUse MCP-tool call (top-level `tool_name` alongside `tool_input`) was not itself named in the handoff/anchors; confirmed by reading `tests/fixtures/probe_payloads.jsonl`'s captured Bash payload shape and `scripts/mcp_spine_server.py`'s tool schema (`args.get("action")`) rather than being told directly. Not a blocker, just the one lookup this run had to do that a payload-shape anchor could have skipped.
- **Instructions improvised around:** the handoff's "equivalent in shape" phrasing for the release path left open whether a door release should also reset the 3-strike nudge ledger the way the Bash release does (not explicitly required by the close criteria). Implemented it for symmetry with the existing release's documented nudge-reset behavior and covered it with `test_post_door_release_removes_binding_and_nudge`, since leaving it asymmetric seemed like a latent correctness gap the handoff's authors likely intended to be covered by "equivalent in shape."
- **What would have made this easier:** naming the exact real PostToolUse payload shape (top-level `tool_name` + `tool_input`) directly in the Map Anchors, alongside the `SPINE_FILE`/`SPINE_SESSION` contract that was already named — would have saved the one fixture lookup above.

## Return status
`complete`
