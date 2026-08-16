# Interactive MCP-door demo spine

This is the checklist the project-scope `.mcp.json` points at. It exists so
opening this worktree in an interactive Claude Code session gives a real,
safe, session-less checklist to drive through the `spine_*` tools without
touching any live project state (the commander spine that actually drove
issue #424, or any other in-flight `.agent-work` run).

It is a throwaway fixture, not project history in its own right — regenerate
it any time with:

```
python examples/mcp-interactive-demo/make_demo_spine.py
```

The generator lives next to the spine it writes, and
`tests/test_shipped_examples_are_portable.py` asserts the committed
`spine.json` is exactly what it produces. So the spine is generated, never
hand-edited — which is what keeps a machine-specific path from creeping back
into it (issue #605).

`.mcp.json` carries no session id (`SPINE_SESSION=""`), so no lease needs to
be claimed first — every `spine_*` tool works session-less against this file,
matching the engine's own "no lease -> legacy behavior" rule
(`checklist-engine.md` "Session lease").

Project-scope `.mcp.json` is the **interactive convenience path only**. It is
not the delivery mechanism for a cold or headless agent: a fresh project-scope
`.mcp.json` is not picked up by a live session, and on a fresh process it
lands in `Pending approval` with no human present to clear it. For a real
dispatch, bind the spine through the caller's own environment — `.mcp.json`
writes `SPINE_FILE` as `${SPINE_FILE:-<default>}`, so a dispatcher exports
`SPINE_FILE`/`SPINE_SESSION` before launching and passes
`--mcp-config ... --strict-mcp-config`. That seam is covered end to end by
`tests/test_mcp_spine_server.py`.

## Where the demo writes

Two different places, and only one of them is in this repository.

The **workspace** the four gates read and write — `notes.txt`,
`optional_report.txt`, `SUMMARY.md` — lands outside the repo, at
`${SPINE_DEMO_WORKSPACE:-${TMPDIR:-/tmp}/constellation-mcp-demo-$(id -u)}/workspace`.
Set `SPINE_DEMO_WORKSPACE` to put it somewhere else. Nothing about that path is
machine-specific and none of it needs a particular working directory, which is
the whole point: `checklist_engine.py` runs a `command` check with no `cwd`, so
a path written relative to this directory would resolve from nowhere.

The **spine's own state** does land here: driving the demo advances gates in
this tracked `spine.json` and writes the engine's per-run side-cars
(`spine.json.journal`, `context/`, `mechanical/`) beside it. The side-cars are
git-ignored; `spine.json` is not, so after trying the demo, reset it with the
regeneration command above.

## Why it lives here and not under `.agent-work/`

It used to sit in issue #424's own work area. That is exactly wrong for a fixture the **committed**
`.mcp.json` points at: when the run archived, the work area moved and the shipped default resolved to
a path that no longer existed. `tests/test_mcp_spine_server.py`'s
`test_mcp_json_referenced_spine_file_exists_and_loads` caught it immediately, which is what that test
is for. A default the shipped config depends on belongs somewhere stable and tracked, with no
lifecycle of its own.
