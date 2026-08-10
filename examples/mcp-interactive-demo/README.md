# Interactive MCP-door demo spine

This is the checklist the project-scope `.mcp.json` points at. It exists so
opening this worktree in an interactive Claude Code session gives a real,
safe, session-less checklist to drive through the `spine_*` tools without
touching any live project state (the commander spine that actually drove
issue #424, or any other in-flight `.agent-work` run).

It is a throwaway fixture, not project history in its own right — regenerate
it any time with:

```
python .agent-work/epic-418-followon/commander-424/crew-plans/scratch-mcp/make_scratch_spine.py \
    .agent-work/epic-418-followon/commander-424/crew-plans/scratch-mcp/interactive-demo
```

`.mcp.json` carries no session id (`SPINE_SESSION=""`), so no lease needs to
be claimed first — every `spine_*` tool works session-less against this file,
matching the engine's own "no lease -> legacy behavior" rule
(`checklist-engine.md` "Session lease").

Per the handoff (`crew-handoffs/g1-implementer-handoff.md`), project-scope
`.mcp.json` is the **interactive convenience path only**. It is not the
delivery mechanism for a cold or headless agent: a fresh project-scope
`.mcp.json` is not picked up by a live session, and on a fresh process it
lands in `Pending approval` with no human present to clear it (measured,
`MISSION_FRAME.md`). For a real dispatch, use `scripts/gen_mcp_config.py` and
`--mcp-config ... --strict-mcp-config` instead — see that script's docstring.

## Why it lives here and not under `.agent-work/`

It used to sit in issue #424's own work area. That is exactly wrong for a fixture the **committed**
`.mcp.json` points at: when the run archived, the work area moved and the shipped default resolved to
a path that no longer existed. `tests/test_mcp_spine_server.py`'s
`test_mcp_json_referenced_spine_file_exists_and_loads` caught it immediately, which is what that test
is for. A default the shipped config depends on belongs somewhere stable and tracked, with no
lifecycle of its own.
