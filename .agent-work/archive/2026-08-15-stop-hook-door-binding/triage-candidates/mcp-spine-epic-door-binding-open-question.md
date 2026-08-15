# Triage Recommendation: `mcp__spine-epic__spine_lease door binding left unaddressed`

## Classification
`unresolved decision`

## Source checklist/artifact
- This run's `MISSION_FRAME.md` (Decision Anchors) and `g1-implement`/`g1-review` out-of-scope observations.
- The archived `.agent-work/archive/2026-08-15-launcher-hygiene/triage-candidates/stop-hook-binding-gap-for-mcp-door-sessions.md`,
  "Open questions": "Does this gap also affect `mcp__spine-epic__spine_lease` (the epic variant), or only
  the per-work-id `mcp__spine__spine_lease` door exercised this run?"

## Structural anchor
`.claude/settings.json` `PostToolUse` block; `scripts/hooks/spine_rail.py::DOOR_LEASE_TOOL_NAME`

## Cartographer mismatch class
None.

## Desired behavior
- **Desired:** an Admiral driving an epic-tier spine entirely through `mcp__spine-epic__spine_lease` gets
  the same mid-flight Stop-hook protection this run just shipped for `mcp__spine__spine_lease`.
- **Today instead:** the new `PostToolUse` matcher and `DOOR_LEASE_TOOL_NAME` constant name only
  `mcp__spine__spine_lease`. An `mcp__spine-epic__spine_lease` claim/release is not recognized -- if that
  tool is ever reachable from a session bound to this repo, its claims still leave no binding, and the
  exact defect this run fixed for `spine` would persist for `spine-epic`.
- **Type:** `measured` -- this repo's own `.mcp.json` registers exactly one MCP server, named `spine`
  (confirmed by both the implementer and reviewer this run, and independently by this Commander at
  `understand`). `mcp__spine-epic__spine_lease` is not registered anywhere in this repo's tracked
  configuration, so it could not be exercised or tested from inside this worktree -- but this Commander's
  own session had that tool name available via a global/user-level MCP registration outside this repo
  (observed via this session's own deferred-tool listing), meaning an Admiral session in THIS SAME repo
  could plausibly reach it too, through configuration this repo does not own or see.
- **Rev:** as observed 2026-08-15, worktree `stop-hook-door-binding`, `.mcp.json` at `2c46cab8`.

## Open questions
- Is `mcp__spine-epic__spine_lease` ever actually reachable from a session operating inside this repo (as
  opposed to a purely user/global-level tool this repo's own settings never wire in)? This run could not
  settle it from inside the worktree.
- If reachable, is its claim/release payload shape identical to `mcp__spine__spine_lease` (same `action`
  field), so the fix is a one-line matcher/constant widening, or does it differ?

## Recommended priority
`medium`

**Reason:** same failure class as the defect this run just fixed (a Commander/Admiral parking mid-spine
with no Stop-hook binding to catch it), but unconfirmed reachability and no in-repo way to test it this
run -- not urgent until reachability is confirmed, but worth settling before the next Admiral-tier
auto-backgrounding incident makes it urgent.

## Related artifacts
- `.agent-work/stop-hook-door-binding/MISSION_FRAME.md`
- `.agent-work/archive/2026-08-15-launcher-hygiene/triage-candidates/stop-hook-binding-gap-for-mcp-door-sessions.md`

## Disposition
`recommend-and-defer`

**Detail:** `recommend-and-defer: reachability of mcp__spine-epic__spine_lease from inside this repo could
not be settled this run (LAUNCH_ORDER's own matcher-scope decision anchor named this exact deferral,
graded 'guess'). Widening the matcher is a one-line change once reachability and payload shape are
confirmed, but confirming them is outside this run's bounded appetite. No tracker-filing authority
exercised.`

## Issue creation authority
`issue-ready only`
