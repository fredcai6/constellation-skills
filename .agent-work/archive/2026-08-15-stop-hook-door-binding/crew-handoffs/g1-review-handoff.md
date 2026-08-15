# Reviewer Handoff

## Gate
`g1` (execute.json: `g1-review`)

## Survey State Location
`.agent-work/stop-hook-door-binding/g1-review/review.json`

## What Was Implemented
`scripts/hooks/spine_rail.py`'s `handle_post_tool_use` now recognizes a door-issued
`mcp__spine__spine_lease` claim/release (via a new `_handle_door_lease` helper, dispatched on
`tool_name == "mcp__spine__spine_lease"` before any Bash command parsing) and records/removes a
session->spine binding equivalent in shape to the existing Bash `checklist_engine.py claim`/`release`
binding entry. The claimed spine's path is resolved from this process's own `SPINE_FILE` environment
variable (the door carries no `--file`), `engine_session` from `SPINE_SESSION`, reusing the existing
`_is_valid_claim_target` validator unchanged. `decide_stop`/`_mid_flight_reason` are untouched — they now
effectively refuse a mid-flight door-claimed turn-end because a binding now exists for it.
`.claude/settings.json` gained one `PostToolUse` array entry: `{"matcher": "mcp__spine__spine_lease", ...}`,
alongside the existing `Bash`-matcher entry.

## How to Inspect the Diff
Uncommitted working tree in this worktree (`/home/tommy/projects/constellation-skills/.worktrees/stop-hook-door-binding`):
```bash
git status --porcelain
git diff scripts/hooks/spine_rail.py tests/test_spine_rail.py .claude/settings.json
```
Three files touched: `scripts/hooks/spine_rail.py` (+105 lines), `tests/test_spine_rail.py` (+209 lines, 16
new tests), `.claude/settings.json` (1 line changed — one array entry added).

## Task Statement
Close a real gap: a Commander whose spine is claimed entirely through the MCP door (`spine_lease`,
`spine_start`, `spine_advance`) can end its turn mid-gate and never be refused by the Stop hook's mid-flight
check, because `decide_stop` only refuses when a session->spine binding exists, and a binding was
previously recorded only from a Bash `checklist_engine.py claim`/`release` command — never from a door
call. Full background: `LAUNCH_ORDER.md` (this worktree's root) and
`.agent-work/triage-candidates/auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md` (primary
checkout, untracked).

## Close Criteria
- A door-issued `spine_lease` claim (`action=claim`) records a binding equivalent in shape to the Bash-path
  entry (`spine`, `engine_session`, `worktree`, `claimed_at`, `path_source`), resolved from this process's
  own `SPINE_FILE`/`SPINE_SESSION` environment — NOT from `tool_input` and not via a new candidate-root
  resolution ladder (must reuse `_is_valid_claim_target` unchanged).
- A door-issued release (`action=release`) removes exactly that binding entry and resets the nudge ledger
  for a top-level release, mirroring the Bash release path.
- RED: prove genuinely (not just read the pasted evidence) that BEFORE this fix, a door-claimed mid-flight
  spine's turn-end was NOT refused by `decide_stop`. Suggested check: `git stash push --
  scripts/hooks/spine_rail.py`, re-run the new door-path claim/mid-flight tests, confirm they FAIL, `git
  stash pop`, confirm GREEN again. (The Commander already did this once independently — you are the second,
  adversarial check; do not skip it because a prior pass exists.)
- CONTROL: a door-claimed legitimate turn-end is NOT refused — terminal spine + released lease; foreign
  worktree; unreadable/malformed spine; honestly-blocked gate (`status == "blocked"`). All four must be
  covered by a real test, run and passing.
- Fail-open proof: a malformed/unrecognized door payload (missing `tool_input`, non-dict `tool_input`,
  missing `action`, unrecognized `action`, missing `SPINE_FILE`, `SPINE_FILE` pointing at a non-checklist
  file, `SPINE_FILE` outside `.agent-work/<work-id>/`) records no binding and raises nothing. At least one
  fuzz-style test covering several malformed shapes at once.
- Every existing (pre-this-gate) `tests/test_spine_rail.py` test still passes, UNMODIFIED in its assertions
  — confirm via `git diff tests/test_spine_rail.py` that no existing test body changed, only new tests were
  appended.
- `_mid_flight_reason`, `decide_stop`, and `decide_session_start` are byte-for-byte unchanged in this diff.
- `.claude/settings.json`'s diff is exactly one new `PostToolUse` array entry with matcher
  `"mcp__spine__spine_lease"` (not the whole namespace, not `"*"`) and the identical hook
  command/shell/timeout shape as the existing `Bash`-matcher entry; `Stop`, `SessionStart`, and the
  `gauge_writer_hook` entry are byte-for-byte unchanged.
- No new subprocess anywhere in the new code.

## Allowed Scope
- `scripts/hooks/spine_rail.py` — additive to `handle_post_tool_use` and its helpers.
- `tests/test_spine_rail.py` — new tests only.
- `.claude/settings.json`'s `PostToolUse` array.

## Specific Exclusions
- `scripts/checklist_engine.py`, `scripts/run_crew.py`, `scripts/apply_episode_delta.py`,
  `scripts/verify_episode_observations.py`, `scripts/hooks/gauge_writer_hook.py`, `.mcp.json` — must be
  untouched (verify via `git status --porcelain` showing only the three files above as modified).
- `.claude/settings.json`'s `Stop`, `SessionStart`, `gauge_writer_hook` entries — must be byte-for-byte
  unchanged.
- `_mid_flight_reason`, `decide_stop`, `decide_session_start` — must be byte-for-byte unchanged.

## Constraints the Implementation Must Respect
- Fail-open: any error path in the new code must return `{}`, never raise, never block a turn.
- No new subprocess on the PostToolUse path.
- Stdlib only, no new imports beyond what the module already had.

## Map Anchors (inbound)
No packet-level map exists for this area (`map/INDEX.md` DEGRADED-UNPARSEABLE — per-module pages absent).
- **Structural:** `scripts/hooks/spine_rail.py::handle_post_tool_use`, `::_handle_door_lease` (new),
  `::_is_valid_claim_target` (reused, must be unchanged), `::decide_stop`/`::_mid_flight_reason` (must be
  unchanged). `.claude/settings.json` `PostToolUse` block.
- **Capability:** session->spine binding store — now fed by two additive sources (Bash command, MCP door).
- **Decision anchors:**
  - Door-binding source of truth: resolve from this process's own `SPINE_FILE`/`SPINE_SESSION`, reuse
    `_is_valid_claim_target` unchanged. `@grade: settled/measured · leans g1-implement`
  - Matcher scope: `mcp__spine__spine_lease` only. `@grade: guess · leans g1-implement,g2-review · settle:
    if a later run finds mcp__spine-epic__ reachable from this repo's own configuration, add its tool name
    to the matcher then` — confirm this repo's `.mcp.json` (read-only) registers exactly one MCP server.
- **Evidence expectations:** RED (independently reproduced by you), CONTROL (4 cases), fail-open (several
  malformed shapes), Bash-path-unchanged (diff-verified, not just test-count-verified).
- **Map confidence flags:** `map/INDEX.md` DEGRADED-UNPARSEABLE — already a recorded triage candidate, not
  something to fix in this review.

## Evidence Produced
IMPLEMENTER_RESULT (`.agent-work/stop-hook-door-binding/crew-handoffs/g1-implement-implementer-result.md`):
`python -m pytest -q tests/test_spine_rail.py` -> `139 passed, 1 skipped` (pre-change baseline `123 passed,
1 skipped`; +16 new tests, 0 regressions). Targets this gate's `g1-implement.c1` postcondition
(`implementer-result`, `status: complete`).

## Suggested Model Tier
Stronger — security/reliability-critical hook; adversarial verification of the RED claim and the
fail-open/CONTROL coverage is the point of this review, not a formality.

## Stop Conditions
BLOCK if: the RED does not reproduce genuinely when you check it yourself; any existing test's assertions
changed; `_mid_flight_reason`/`decide_stop`/`decide_session_start` differ from `main`; the matcher is
anything other than exactly `mcp__spine__spine_lease`; `Stop`/`SessionStart`/`gauge_writer_hook` entries
changed; a new subprocess was introduced; any excluded file was touched.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK, per-check findings, blockers, out-of-scope observations,
workflow feedback), written to
`.agent-work/stop-hook-door-binding/crew-handoffs/g1-review-reviewer-result.md` before ending your turn.
