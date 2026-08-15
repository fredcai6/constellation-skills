# Triage Recommendation: `spine_rail.py's Stop-hook mid-flight block never binds an MCP-door session`

## Classification
`bug`

## Source checklist/artifact
- `.agent-work/launcher-hygiene/spine.json` triage candidate `tc1`, raised at `execute` gate `g4-stop-hook-decision` during `launcher-hygiene` attempt 2's evaluation of LAUNCH_ORDER's Task 3b.

## Structural anchor
`scripts/hooks/spine_rail.py:decide_stop`, `scripts/hooks/spine_rail.py:handle_post_tool_use`

## Cartographer mismatch class
None — no packet map exists in this repo (context step's DEGRADED-UNPARSEABLE discharge).

## Observations

### Observation 1 — the mid-flight Stop-hook block is a no-op for this session's own claim path
- **What's wrong:** `decide_stop` correctly refuses a turn-end while a bound spine is mid-flight, but that
  refusal only fires when `handle_post_tool_use` has already recorded a session->spine binding. That
  binding is only ever written when a session claims via a Bash `checklist_engine.py claim` invocation
  (matched by `handle_post_tool_use`'s tool matcher). A session that claims the same spine through the MCP
  door's `spine_lease` tool — this repo's own documented default claim path, and the one this very
  Commander session used — never triggers `handle_post_tool_use`, so no binding file is ever written for
  it.
- **Expected:** the Stop hook's mid-flight block should refuse a turn-end for any session holding an
  active claim on a mid-flight spine, regardless of whether that claim was taken via the Bash-matcher path
  or the MCP door.
- **Conditions:** any session that claims a spine/checklist lease exclusively through `mcp__spine__spine_lease`
  (or the epic variant `mcp__spine-epic__spine_lease`) without ever issuing a matching
  `checklist_engine.py claim` Bash call. This is the normal shape for a Commander driving its own bound
  spine through the MCP door, as documented and as used throughout this run.
- **Type:** `measured` — ran the Stop hook by hand against this session's own `session_id` mid-run (spine
  `execute` step `in-progress`, MCP-door lease active); it returned `{}` (allow), and no binding file
  existed anywhere in this worktree for this session.
- **Rev:** as observed 2026-08-15, worktree `/home/tommy/projects/constellation-skills/.worktrees/launcher-hygiene`,
  commit range up to and including this run's g5 gate closure (suite green: 3031 passed / 6 skipped / 0
  failed).

**Field notes**

This is plausibly the actual root cause behind the auto-backgrounding parking incidents the Stop hook was
*meant* to catch — see the separate, broader recommendation
`.agent-work/triage-candidates/auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md` (durable
root, six documented occurrences across this and prior waves, most recently `launcher-hygiene` attempt 1's
own Observation 6). That recommendation's proposed remedy (a Stop-hook mid-flight/pid-liveness check) is
the one design not yet falsified by the two documentation-shaped remedies that were tried and failed. This
observation narrows *why* a naive implementation of that remedy would still fail for the dominant current
dispatch path: building it on top of the existing binding store, without also closing the MCP-door binding
gap, would ship a check indistinguishable from not shipping it for any session that claims via
`spine_lease` rather than `checklist_engine.py claim`.

## Possible fix

Wire the MCP door's `claim`/`release` verbs into `spine_rail.py`'s binding store (or widen
`handle_post_tool_use`'s matcher to cover MCP tool calls, not only the Bash `checklist_engine.py`
invocation). Either shape needs its own red (proving the block now fires for an MCP-door-claimed,
mid-flight spine) and a control (proving a legitimate turn-end, e.g. after `release`, is not blocked) per
the fail-open-hooks constraint (Pre-Ruling 4: a hook change must never crash or hang a turn).

## Open questions

- Should the binding store key on session id alone, or also record which claim path (Bash vs. MCP) was
  used, in case the two paths need different liveness semantics later?
- Does this gap also affect `mcp__spine-epic__spine_lease` (the epic variant), or only the per-work-id
  `mcp__spine__spine_lease` door exercised this run?

## Recommended priority
`high`

**Reason:** this is very likely the mechanism, not just a symptom, behind a defect already rated `high` in
the durable-root recommendation (five-then-six documented occurrences, each costing a full dispatch, and
resistant to two independently-tried documentation-shaped remedies). Closing this specific binding gap is
the concrete step that would make the "only remedy not yet falsified" (a mechanical Stop-hook check)
actually effective for the dispatch path most runs use.

## Related artifacts
- `.agent-work/triage-candidates/auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md` (durable root, broader defect this narrows)
- `.agent-work/launcher-hygiene/MISSION_FRAME.md` (Decision Pressure section, Task 3b feasibility)
- `.agent-work/launcher-hygiene/spine.json` (`triage_candidates[0]`, id `tc1`)

## Disposition
`recommend-and-defer`

**Detail:** `recommend-and-defer: the fix touches scripts/mcp_spine_server.py and/or .claude/settings.json
plus scripts/hooks/spine_rail.py's binding store -- outside this run's file-ownership fence (LAUNCH_ORDER
grants only tests/test_mcp_identity.py, scripts/run_crew.py + its tests, skills/commander/references/crew-dispatch.md,
and scripts/hooks/spine_rail.py's Stop handler + tests only under Task 3b's own red+control proof gate,
which this run explicitly declined). A second subsystem beyond this run's budget; no tracker-filing
authority exercised this run.`

## Issue creation authority
`issue-ready only`
