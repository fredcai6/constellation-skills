# Lane F notes — #535 "reveal the spec through the spine, not the launch order"

## Problem statement (understand gate, consolidated against LAUNCH_ORDER)

Mission (LAUNCH_ORDER:Mission): dispatch should start with "start the spine with this
identifier," not with pasted launch-order prose. Measure before building; an evidenced
honest null is a complete, correct outcome if the mechanism is already delivered.

## Measurement

### 1. `run_crew.py` CLI-backend spine-only dispatch — ALREADY SHIPPED (PR #623, Lane A)

`CrewSpec.__post_init__` (run_crew.py:1369-1383) requires only ONE of `--handoff`/`--spine`,
and only one of `--result`/`--spine`:

```
if self.handoff is None and self.spine is None:
    raise CrewLaunchError("a crew needs a job: refusing a dispatch with neither --handoff nor --spine given")
if self.result is None and self.spine is None:
    raise CrewLaunchError("a crew needs a completion contract: ... (a spine-only dispatch is judged on its spine reaching a terminal state instead)")
```

`build_crew_argv`'s spine-only branch (run_crew.py:813-820) emits exactly the shape #535 asks
for — no pasted document, just the identifier and the instruction to drive it:

```python
elif spine is not None:
    prompt = (
        f"You are the constellation {role} crew for session {session}. "
        f"{parent_clause} "
        "Call mcp__spine__spine_status first: your spine is already bound. "
        "Drive it gate by gate through the door -- do not author a plan of "
        "your own -- until it reports done."
    )
```

Session identity is derived, never caller-supplied: `_crew_door_env` (run_crew.py:1010-1048)
sets `SPINE_SESSION = assignment_session_name(work_id, gate, role)` — an caller cannot name
an arbitrary identity, matching `IDENTITY_TRADE.md` §3 and Lane A's PR #623 finding, which
this run does **not** reopen.

**Live proof, not just static reading:** this very Commander session was dispatched by
`run_crew.py --backend cli --spine <this spine>` (per LAUNCH_ORDER Workspace section). My own
door resolved to my own spine at startup — I ran `spine_lease claim` with no session-id
argument and it succeeded (`claimed lease constellation/567-f/lane-f/commander-delegated ->
active`), and `spine_status` correctly showed my own gate. The CLI-backend, spine-bound,
identity-derived dispatch #535 asks for is not just implemented, it is the exact mechanism
that launched this run.

Test coverage: `tests/test_crew_launcher.py` —
`test_spine_only_branch_names_no_document_and_names_spine_status`,
`test_spine_only_branch_tells_crew_not_to_author_its_own_plan`,
`test_neither_handoff_nor_spine_is_refused`, plus the parent-clause spine-only tests. Command:

```
python -m pytest tests/test_crew_launcher.py -k "spine_only or refuses_spine or spine_status" -q
-> 14 passed, 203 deselected
```

### 2. `ExternalBackend` (Agent-tool subagent dispatch) — spine-only is REFUSED, by design

`ExternalBackend.dispatch` (run_crew.py:1685-1702) raises `CrewLaunchError` whenever
`spec.handoff is None`, even when `spec.spine` is given:

```python
if spec.handoff is None:
    raise CrewLaunchError(
        "refusing to record: the external backend always needs a "
        "--handoff, spine or not -- it spawns no process and builds "
        "no environment, so it cannot bind a spine either; a "
        "spine-only dispatch here would leave the crew with no job at all."
    )
```

Reason stated in the docstring (run_crew.py:1673-1681): "`--spine` is ACCEPTED here (issue
#432), but VERIFICATION-ONLY... binding is still impossible by construction when nothing is
spawned and no environment is built." `ExternalBackend` is the backend a **Commander in the
Constellation Agent-tool harness actually uses** to dispatch Implementer/Reviewer crews
(`references/crew-dispatch.md`: "In the Constellation Agent-tool harness there is no headless
`claude` CLI, so dispatch the implementer/reviewer as synchronous Agent-tool subagents via
`--dispatch external`"). The Agent tool itself (this harness's own subagent-spawn primitive)
takes no environment-variable parameter — only `description`, `prompt`, `model`,
`subagent_type`, `isolation`, `run_in_background` — so there is no way for `run_crew.py`, or
any code inside it, to bind `SPINE_FILE`/`SPINE_SESSION` into an Agent-tool subagent's MCP
door. This mirrors the hook-doctrine precedent already on record for this repo
(`docs/agents/ORCHESTRATOR_CONTEXT.md` "Dogfooding": `CLAUDE_PROJECT_DIR` resolves once at
session launch, #269) — env for a subagent's own MCP server is fixed at spawn time by the
harness, not something a script or a `Bash` call inside the subagent's own turn can set
after the fact.

This refusal is deliberate and already tested, not an oversight:
`test_external_backend_refuses_spine_only_with_no_handoff`,
`test_external_dispatch_missing_handoff_refuses_with_record_wording`.

### 3. `spine_open`'s spec compilation — covers gate *plans*, not Commander-level mission content

`spine_open`'s `spec` parameter is `generate_spine.py`'s `compile_spec`, which compiles a
`specs/<role>.spine.toml` file into an engine-native spine. The only two specs that exist are
`specs/implementer.spine.toml` and `specs/reviewer.spine.toml` — confirming the LAUNCH_ORDER's
named Local Unknown #3. There is no `commander.spine.toml` or equivalent, and the schema
(`CHECK_KINDS = ("qualitative", "pytest", "script", "population", "artifact")`) has no field
for prose like Mission, Pre-Rulings, Inherited Latitude, or File Ownership — it compiles
postcondition *checks*, not narrative context.

Separately, a Commander's own `spine.json` is stamped from
`templates/COMMANDER_SPINE.template.json` (a **fixed, mission-independent** 10-step
init→...→archive workflow) by the Admiral's `stand-up-work-area.md` step — never spec-compiled
from a launch order at all. The actual mission-specific content (everything this LAUNCH_ORDER
carries beyond the fixed step names) has no compiled-into-the-spine representation today; it
travels only as the pasted `--handoff` document, exactly as it did for this dispatch (both
`--handoff` and `--spine` were given to launch me).

## Remaining gap after measurement

Two distinct claims, not one:

1. **The CLI-backend, Admiral→Commander path** — the concrete mechanism #535 names
   ("dispatch should start with 'start the spine with this identifier'") — is **fully
   delivered**. Nothing to build.
2. **The ExternalBackend, Commander→crew (Agent-tool) path** cannot go spine-only today, and
   the blocker is a harness constraint (`Agent` tool has no env-passing parameter), not a
   defect in `run_crew.py`'s own logic. Closing it would need either a harness capability that
   does not exist, or a different mechanism entirely (e.g. the spine door resolving identity
   some other way for an Agent-tool subagent) — that is an **architecture-level** question,
   out of this lane's latitude (`Architecture / structural change: float to the Admiral`).
3. Making the Commander-level LAUNCH_ORDER content itself spine-carried (not just the identity
   binding) would require a spec schema and Commander spine template that do not exist yet, in
   files fenced to lane D1 this wave (`skills/**` except workbench) — floated, not built.

## Decision

Verdict: **evidenced honest null**, per `decision:honest-null-is-likely-and-fine` and
`decision:honest-null-is-complete`. `scripts/run_crew.py` — the one file this lane owns — has
nothing left to build for the concrete mechanism #535 names; the mechanism is shipped and this
very dispatch is live proof of it. The two remaining gaps (ExternalBackend spine-only, and
Commander-level spec-through-spine) are real but sit outside this lane's file ownership and
latitude — floated to the Admiral below, not built here.
