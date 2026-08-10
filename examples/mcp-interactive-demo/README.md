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

## If the door does not start on your machine

`.mcp.json` names its interpreter as `${CONSTELLATION_PYTHON:-python3}`. On any host where `python3`
is a working command, nothing is needed. On a stock Windows host it is not one — the python.org
installer provides `python.exe` and the `py` launcher and no `python3.exe` — so export
`CONSTELLATION_PYTHON` in the environment you launch Claude Code from, naming an interpreter that
works there:

```
setx CONSTELLATION_PYTHON py          # Windows, persistent; restart the shell afterwards
export CONSTELLATION_PYTHON=/usr/bin/python3   # POSIX, if `python3` is not on PATH
```

Two things worth knowing, both measured against the real client rather than assumed:

- The expansion reads the **`claude` process's own environment**. An `env` block in
  `.claude/settings.local.json` does *not* feed it, even though that block does reach hooks and
  Bash tool calls.
- A variable exported as the **empty string wins over the default**. `${VAR:-default}` here means
  "if set", not POSIX "if set and non-empty", so `CONSTELLATION_PYTHON=""` yields an empty command
  and the door fails to launch. Unset it rather than blanking it.

`python scripts/install_constellation.py --agent claude --scope project --dest <project>/.claude/skills
--check-readiness` reports this as its `mcp` item, by expanding the committed `command` and actually
launching it. `--wire-mcp` writes a project's `.mcp.json` with the interpreter probed on that host. It needs the
project root named — `--project <project>`, or a bare `--scope project` run started from it — and
refuses under `--dest`, which names a skills directory rather than a project. It also refuses when
the file is git-tracked — a probed interpreter name is right on one machine and
wrong on every other, so it must never reach a shared file. This repo's own `.mcp.json` is tracked
and stays tracked; here the environment variable is the fix.

## Why it lives here and not under `.agent-work/`

It used to sit in issue #424's own work area. That is exactly wrong for a fixture the **committed**
`.mcp.json` points at: when the run archived, the work area moved and the shipped default resolved to
a path that no longer existed. `tests/test_mcp_spine_server.py`'s
`test_mcp_json_referenced_spine_file_exists_and_loads` caught it immediately, which is what that test
is for. A default the shipped config depends on belongs somewhere stable and tracked, with no
lifecycle of its own.
