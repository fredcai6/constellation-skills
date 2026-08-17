# Triage candidate: ExternalBackend cannot go spine-only

**Found in:** lane-f (#535, epic-567-door wave 2), during the measurement step.

**Observation.** `run_crew.py`'s CLI backend already supports handoff-optional, spine-only
crew dispatch (`CrewSpec.__post_init__`, `build_crew_argv`'s spine-only prompt branch,
`scripts/run_crew.py:813-820,1369-1383`), and this very Commander session was launched
exactly that way. `ExternalBackend` -- the backend a Commander running inside the
Constellation Agent-tool harness actually uses to dispatch Implementer/Reviewer crews
(`references/crew-dispatch.md`) -- refuses spine-only dispatch unconditionally
(`scripts/run_crew.py:1685-1702`): a `--handoff` document is always required, even when
`--spine` is given. This is deliberate and tested
(`test_external_backend_refuses_spine_only_with_no_handoff`), not an oversight.

**Why it is not closeable inside `scripts/run_crew.py`.** `ExternalBackend.dispatch` spawns no
process and builds no environment -- the actual subagent is spawned by the dispatching
Commander's own `Agent` tool call, which takes no environment-variable parameter (only
`description`, `prompt`, `model`, `subagent_type`, `isolation`, `run_in_background`). There is
no way for any code inside `run_crew.py` to bind `SPINE_FILE`/`SPINE_SESSION` into an
Agent-tool subagent's MCP door. This mirrors the hook-doctrine precedent already on record for
this repo (`docs/agents/ORCHESTRATOR_CONTEXT.md` "Dogfooding": `CLAUDE_PROJECT_DIR` resolves
once at session launch, #269) -- env for a subagent's own MCP server is fixed at spawn time by
the harness.

**What #535 would need to close this.** Either a harness capability that does not exist today
(an env-passing parameter on the `Agent` tool), or a different mechanism entirely for the
Agent-tool path to resolve spine identity (e.g. something the subagent itself calls at
startup, naming its own gate/role, resolved server-side against the dispatching Commander's
registry). Both are architecture-level questions, not a `run_crew.py` code change.

**Disposition:** recommend-and-defer. Not filed as an issue this run (`decision:no-issue-filing-mid-run`).
