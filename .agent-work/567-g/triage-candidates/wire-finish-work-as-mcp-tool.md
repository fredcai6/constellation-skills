# Triage Recommendation: wire finish_work as an actual spine_done MCP tool

## Classification
`feature`

## Source checklist/artifact
- g3-integrate (this Commander's own execute.json), the launch order's #574 step 5/6 and the fence noted throughout this lane's plan

## Structural anchor
`scripts/mcp_spine_server.py` (fenced this wave, owned by lane A)

## Cartographer mismatch class
none

## Desired behavior
- **Desired:** `finish_work` (shipped this lane in `scripts/spine_lifecycle.py`) reachable as a proper door tool (`spine_done`), the same way `spine_open`/`spine_close` are already wired via `call_lifecycle_tool` in `mcp_spine_server.py`.
- **Today instead:** `finish_work` is reachable only via direct Python import or the new `scripts/spine_done_cli.py` CLI — a real, working, reachable-today substitute, but not a door tool an MCP-bound agent can call directly.
- **Type:** `measured` — confirmed by reading `mcp_spine_server.py`'s existing `_spine_open`/`_spine_close`/`call_lifecycle_tool` pattern; a third dispatch (`_spine_done`) mirroring that shape is the natural addition, not attempted this wave since the file is fenced (lane A is actively rewriting it).
- **Rev:** this worktree, base `600de020`, `mcp_spine_server.py` unmodified throughout this lane.

## Possible fix
Add `_spine_done(args)` (no arguments, acts on the bound spine, mirrors `_spine_close`'s shape) to `mcp_spine_server.py`, dispatched from `call_lifecycle_tool` alongside `spine_open`/`spine_close`, calling `spine_lifecycle.finish_work(SPINE, root=..., session_id=SESSION, today=..., ...)`. Register the tool in the same place the existing 11 tools are declared. Requires lane A's rewrite to land first (or explicit sequencing/rebase coordination), since `mcp_spine_server.py` is fenced to this lane.

## Open questions
- Should `tree_clean`/`episodes_captured` be auto-detected by the tool (e.g. `git status --porcelain`, an episode-store scan) rather than passed as arguments, so the MCP tool truly takes no caller-supplied state the way `spine_close` does today? Not decided by this lane — `scripts/spine_done_cli.py` currently exposes them as explicit flags with an auto-detect default for `--tree-clean`.

## Recommended priority
`medium`

**Reason:** Not urgent — the CLI already delivers the mechanical, one-call closeout the mission asks for. But it's the natural, concrete next step once the fence lifts, and this lane already did the design work (`finish_work`'s signature and return shape are stable and tested).

## Related artifacts
- `scripts/spine_lifecycle.py` — `finish_work`, `open_pr`
- `scripts/spine_done_cli.py`
- `RETURN.md` section 10 (the lane-A touchpoint)

## Disposition
`recommend-and-defer`

**Detail:** filing authority per `decision:no-issue-filing` — this lane files no issues; recorded here for the Admiral's disposal. Blocked on lane A's concurrent rewrite of the file this touches.

## Issue creation authority
`ask user`
