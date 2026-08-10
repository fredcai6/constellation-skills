<!-- episode-state: schema=1 id=epic-418-followon_commander-f2-001 status=active -->

# episode: epic-418-followon_commander-f2-001

## Mechanical
- run: epic-418-followon/commander-f2
- project: constellation-skills
- role: implementer
- spine-step: g2-implement
- context-manifest-ref: ctx-epic-418-followon/commander-f2-g2-implement@3fbabd5546028bf0d03832837566272cdb04b4a2
- refusals: 2
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: scripts/mcp_spine_server.py
- artifact-ref: tests/test_mcp_friction_capture.py
- artifact-ref: .agent-work/epic-418-followon/commander-f2/evidence/g2-friction-capture/mcp_rejections.jsonl
- artifact-ref: .agent-work/epic-418-followon/commander-f2/evidence/g2-friction-capture/seed_rejections.py

## Agent-supplied

### assertion:epic-418-followon_commander-f2-001.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Instrumented the MCP door (scripts/mcp_spine_server.py) to record its own rejections -- unknown tool name, unknown multiplexed action, missing required argument -- to a door-side JSONL, because those three classes return _tool_error(...) before run_engine() is ever called and so never reach the engine's own refusals counter or mcp_calls.jsonl (reproduced independently by demo_engine_refusal_reaches_episode.py before any code changed).

### assertion:epic-418-followon_commander-f2-001.a2
- kind: expected-behavior
- strength: medium
- lifecycle-standing: active
- statement: A new wrapper function around _tool_error(), logging one record per rejection, could be substituted at every call site in call_tool() and in main()'s tools/call branch without disturbing anything else in the module.

### assertion:epic-418-followon_commander-f2-001.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: call_tool()'s own choke-point pin (tests/test_mcp_identity.py::IdentityBindingPinTests.test_call_tool_can_only_produce_content_two_ways, closed earlier in this same run's g1 gate) restricts every return in that function to literally as_result(run_engine(...)) or _tool_error(...), checked by an AST walk keyed on the called function's own name. Wiring a differently-named wrapper at all 14 in-scope call sites and running the full suite produced one failing assertion naming 14 offenders, even though the wrapper never touched run_engine() and never bypassed the engine -- the pin is blind to what a call does and exact about what it is named.

### assertion:epic-418-followon_commander-f2-001.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: Caught before commit by running the full relevant test slice rather than only the new file: the AST pin fired on the first run that included tests/test_mcp_identity.py, immediately naming the exact 14 offending lines by line number.

### assertion:epic-418-followon_commander-f2-001.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Folded the two new facts (tool, rejection_class) into _tool_error() itself as optional keyword-only arguments, so every call site's function name stayed literally _tool_error and the pin's AST check kept passing. python -m pytest -q tests/test_mcp_friction_capture.py tests/test_mcp_spine_server.py tests/test_mcp_identity.py tests/test_mcp_imperative_equivalence.py reported 55 passed after the refactor; a real subprocess seeding run against a throwaway spine produced 3 rejection records (unknown-action, missing-required-argument, unknown-tool), one per induced rejection.

## Diagnosis (optional)

### assertion:epic-418-followon_commander-f2-001.d1
- kind: suspected-cause
- strength: medium
- lifecycle-standing: active
- statement: An AST-shape pin that keys on a called function's literal name is exact about call SHAPE but blind to the parameters flowing through that name, which is why extending the door's behavior at those return sites had to happen inside the sanctioned name rather than through a new one.

## Retirement
- status: active
- retired-reason: 
- retired-at: 
- consolidated-into: 
- superseded-by: 
