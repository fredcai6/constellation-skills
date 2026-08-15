# Review Result

## Assigned Gate
`g1` (execute.json: `g1-review`)

## Result
`APPROVE`

## Handoff compliance
Fully satisfied. `_handle_door_lease` is dispatched from `handle_post_tool_use` before any Bash
command parsing, gated on `data.get("tool_name") == DOOR_LEASE_TOOL_NAME` (`"mcp__spine__spine_lease"`).
It resolves the claimed spine from this process's own `SPINE_FILE`/`SPINE_SESSION` environment
(never `tool_input`), reuses `_is_valid_claim_target` unchanged (confirmed byte-identical by hashing
the function body against `HEAD`), and writes a binding entry equivalent in shape to the Bash path
(`spine`, `engine_session`, `worktree`, `claimed_at`, `path_source=door_env`). A door release removes
exactly that entry and resets the nudge ledger on a top-level release (`key == sid`), mirroring the
Bash release path's symmetry. `_mid_flight_reason`, `decide_stop`, `decide_session_start` needed no
change and received none.

**RED, independently reproduced (not just read from pasted evidence):**
```
git stash push -- scripts/hooks/spine_rail.py
py -m pytest -q tests/test_spine_rail.py -k door
# 8 failed, 8 passed, 124 deselected
py -m pytest -q tests/test_spine_rail.py::test_stop_door_claimed_mid_flight_blocks
# FAILED: assert result.get("decision") == "block"
#   AssertionError: assert None == 'block'   (decide_stop returned {} pre-fix)
git stash pop
py -m pytest -q tests/test_spine_rail.py
# 139 passed, 1 skipped
```
This is exactly the gap the launch order named: a door-claimed mid-flight spine's turn-end was NOT
refused before this fix, and IS refused after it.

## Scope drift
None. `git status --porcelain` shows exactly the three claimed files modified (plus this review's own
untracked `.agent-work/` scratch). `git diff --stat` against all six specifically-excluded files
(`checklist_engine.py`, `run_crew.py`, `apply_episode_delta.py`, `verify_episode_observations.py`,
`gauge_writer_hook.py`, `.mcp.json`) is empty. `.claude/settings.json`'s `Stop`/`SessionStart` blocks and
the `gauge_writer_hook` `PostToolUse` entry are byte-for-byte identical to `HEAD` (verified by dict
equality, not just eyeballing the diff); exactly one new `PostToolUse` entry was added, matcher
`"mcp__spine__spine_lease"` (not the namespace, not `"*"`), identical command/shell/timeout shape to
the existing `Bash` entry. `.mcp.json` registers exactly one MCP server (`"spine"`), confirming the
handoff's matcher-scope decision anchor settle condition.

## Evidence verdict
- **RED:** reproduced independently (above), not merely read.
- **CONTROL (4/4):** all present as passing tests — terminal spine + released lease
  (`test_stop_door_claimed_terminal_released_lease_allows`), foreign worktree
  (`test_stop_door_claimed_foreign_worktree_not_blocked`), unreadable/malformed spine
  (`test_stop_door_claimed_unreadable_spine_allows`), honestly-blocked gate
  (`test_stop_door_claimed_blocked_status_honest_stop_allows`).
- **Fail-open:** 7 distinct malformed-shape tests (missing `tool_input`, non-dict `tool_input`, missing
  `action`, unrecognized `action`, missing `SPINE_FILE`, non-checklist `SPINE_FILE`, `SPINE_FILE`
  outside `.agent-work/`) plus one combined fuzz test (`test_post_door_never_raises_on_junk`, 7 rows ×
  2 `SPINE_FILE` states).
- **Bash-path-unchanged, diff-verified:** `git diff --numstat` shows `spine_rail.py` `+105/-0` and
  `test_spine_rail.py` `+209/-0` — zero deletions, purely additive. `decide_stop`/`_mid_flight_reason`/
  `decide_session_start` hashed byte-identical between `HEAD` and the working tree. The new dispatch
  branch is gated on `tool_name == "mcp__spine__spine_lease"`; a Bash payload's `tool_name` is `"Bash"`,
  so the new branch is structurally unreachable from a Bash call.
- Full suite independently re-run: `139 passed, 1 skipped` — matches `IMPLEMENTER_RESULT` exactly.

## Code/doc quality
Fail-open preserved: every early-return in `_handle_door_lease` returns `{}`, and the whole body is
wrapped in `try/except Exception: return {}`. No new subprocess (grep for `subprocess` in the diff: no
hits). No new imports (stdlib-only preserved). Naming/doc conventions match the surrounding file
(`DOOR_LEASE_TOOL_NAME` sits with the module's other constants; `PATH_SOURCE_DOOR_ENV` extends the
existing `PATH_SOURCE_*` set in place; docstring density matches `_is_valid_claim_target`/`binding_key`).

**Fowler pass** (`.agent-work/stop-hook-door-binding/FOWLER_PASS.json`, `verify_fowler_pass.py` exit 0,
12/12 smells verdicted): 11 absent, 1 overridden. `duplicated-code` is real — the new
`_door_claim_mutate`/`_door_release_mutate` closures mirror the shape of the existing
`_claim_mutate`/`_release_mutate` (same 5-key binding-entry dict, same nudge-reset block) — overridden
with a logged standard + reason: `references/global-crew.md`'s minimal-change/no-speculative-abstraction
rule, combined with the handoff's own non-negotiable that the Bash path stay behavior-unchanged;
extracting a shared helper would restructure already-shipped, tested Bash code for a small line-count
win the handoff scoped out of this gap-closing change.

## Map impact verdict
Skipped — no packet-level map exists for this area (`map/INDEX.md` DEGRADED-UNPARSEABLE, already a
recorded triage candidate per the handoff, not this review's job to fix). The change is purely
additive to the session→spine binding capability and does not touch the decision surface
(`decide_stop`/`_mid_flight_reason`/`decide_session_start`), so no structural/capability/constraint/
decision-impact notes were owed here.

## Reconciliation check
None needed. The one `guess`-graded decision anchor (matcher scope) has its settle condition already
verified true this session (`.mcp.json` registers exactly one server) — resolves cleanly to the
shipped narrow matcher, no authority escalation required.

## Blockers
- none

## Out-of-scope observations
- `test_post_door_never_raises_on_junk`'s fuzz loop has no `len(rows) >= N` assertion the way the
  existing sibling `test_post_tool_use_never_raises_on_junk` does. Low risk since `rows` is a 7-item
  literal, not a derived/filtered collection that could silently go empty — not a blocker, but worth
  matching the sibling's convention if the test is touched again.

## Workflow Feedback
- **Handoff gaps:** none — the handoff's Close Criteria and Stop Conditions were specific enough to
  drive every check directly; no field was missing or ambiguous.
- **Context rediscovered:** the environment's `SPINE_FILE`/`SPINE_SESSION` (inherited from the
  dispatching Commander's own bound spine, `.../spine.json`, `execute` gate) is NOT a survey scoped to
  this reviewer role — it is the Commander's own top-level plan. Per `checklist-engine.md`'s "MCP door"
  section, a `run_crew.py`-dispatched crew is supposed to get its own fresh `SPINE_FILE`/`SPINE_SESSION`
  bound before its MCP server starts, but what was actually bound here was the parent's spine, not a
  reviewer-scoped survey. I did not use the MCP door tools against it (that would have mutated the
  Commander's own `execute` gate); I built and drove my own `REVIEW_SURVEY` via the CLI
  (`scripts/checklist_engine.py`) at the path the handoff named instead, per the reviewer skill's
  documented fallback for "nothing is bound." This is worth a Commander-side look: either the dispatch
  wiring should bind a reviewer-scoped survey file, or the doctrine should say explicitly that a
  reviewer inheriting the parent's own spine env is expected and should always fall back to its own
  survey.
- **Instructions improvised around:** the above — used the CLI-driven own-survey path instead of the
  MCP door, since the door's bound file was not mine to drive.
- **What would have made this easier:** confirming, in the handoff itself, whether a reviewer-scoped
  spine/survey is expected to be pre-bound via the door for this dispatch shape, so a reviewer doesn't
  have to infer it from the mismatch between the env and the checklist-engine reference doc.

## Return status
`complete`
