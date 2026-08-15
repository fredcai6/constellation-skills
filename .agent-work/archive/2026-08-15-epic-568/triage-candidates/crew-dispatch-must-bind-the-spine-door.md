# Triage Recommendation: `crew dispatch must bind the child's MCP spine door before its servers start`

## Classification

`infrastructure` / `agent-dispatch-correctness`

## Source checklist/artifact

Floated independently by two Commanders in the `epic-568-wave-2-repair` launch:
`constellation/epic-568-530/g2-repair/commander/attempt-1` and
`constellation/epic-568-510/g2-repair/commander/attempt-1`. Recorded in
`.agent-work/epic-568/ADMIRAL_LOG.md`, 2026-08-14.

## Structural anchor

`scripts/mcp_spine_server.py:145-146` (binds at module import), `.mcp.json` (defaults `SPINE_FILE`
to `examples/mcp-interactive-demo/spine.json`), `scripts/run_crew.py` (dispatch does not export the
binding into the child environment), `tests/test_mcp_identity.py:914` (pins that no argument may
redirect a running door).

## Cartographer mismatch class

None. The code does what it says; the dispatch path never sets what it reads.

## Observations

### Observation 1

Both dispatched Commanders found their `mcp__spine__` door bound to a foreign spine rather than to
the spine they were dispatched to drive. One reported its `spine_status` returning a scratch spine
under `constellation-skills-wt/f-424/…`. The `mcp__spine-epic__` door returned `Connection closed`
for both, and for the Admiral session as well.

### Observation 2

The binding is read at module import from the environment, so a server that is already running
cannot be rebound, and `tests/test_mcp_identity.py:914` deliberately pins that no argument can
redirect it. `spine_open` only creates spines that do not yet exist, so it is not an escape either.
The condition is therefore unfixable from inside the dispatched session — it must be set before the
child's MCP servers start.

**Field notes**

The consequence is not a crash but a false constraint. Launch orders in this epic carry "spine
interaction is MCP-only" as a hard constraint, and that instruction was impossible to obey from the
sessions it was issued into. The two Commanders resolved it in opposite, individually defensible
ways: one obeyed and was left unable to take its lease or attach evidence, the other used the engine
CLI directly and disclosed the deviation. Neither hand-edited spine state. The divergence is the
real signal — an unsatisfiable constraint does not stop work, it silently randomizes how agents
handle it, and only the ones that disclose leave a trace.

Note the recurrence of a stale path: the foreign spine one Commander landed on sits under
`constellation-skills-wt/`, the pre-relocation worktree prefix. The wave-1 relocation survives in
ambient MCP configuration as well as in bytecode caches — see
[`pycache-root-mismatch-guard`](pycache-root-mismatch-guard.md).

## Desired behavior

`run_crew.py` dispatch exports `SPINE_FILE`, `SPINE_ENGINE`, and `SPINE_SESSION` into the child's
environment before its MCP servers start, so the child's door resolves to its own spine. A dispatch
that cannot bind the door should refuse rather than hand the child a door pointing somewhere else.

## Possible fix

The `cli` backend already derives an assignment-keyed `SPINE_SESSION` from
`--work-id`/`--gate`/`--role` and binds `SPINE_FILE` for spawned children. Extend the same binding to
out-of-band (`external`) dispatch, where the parent constructs the child's environment. Where the
parent genuinely cannot control that environment, the launch order should say the door is unbound
rather than asserting an MCP-only constraint the child cannot satisfy.

Alternative considered and rejected: relaxing `test_mcp_identity.py:914` to allow runtime
redirection. That pin exists so a crew cannot point its door at someone else's spine, which is worth
more than the convenience.

## Open questions

- Should a door that comes up on a spine other than the dispatch's own refuse to answer at all,
  rather than answering about a foreign spine? Answering confidently about the wrong spine is the
  failure mode that cost two Commanders their lease handling here.
- Is `mcp__spine-epic__`'s `Connection closed` the same defect or a separate lifecycle bug? It
  dropped for three independent sessions in one run.

### Observation 3 — added after a third independent hit

The Codex archive Commander hit the same defect and was the first for whom it **blocked the work
outright**: its archive gate is otherwise fully satisfiable (`c1`, `c2`, `c2b`, `c4` all verified;
only the lease release is unreached), and it could not proceed because a `spine_lease claim` from a
door bound to `examples/mcp-interactive-demo` would have mutated the **demo** spine rather than its
own. It declined to call it.

That is the sharpest statement of the risk: the failure mode is not "the door does not work", it is
"the door works, on someone else's spine." Three agents, three different coping strategies — obey and
stall, disclose a CLI fallback, refuse and report — one shared cause. Only the third was blocked, and
only because it was the one whose remaining work was a mutation.

The relaunch path that clears it is known and cheap: dispatch through the `cli` backend with
`--spine`, which binds `SPINE_FILE` and an assignment-keyed `SPINE_SESSION` into the child before its
MCP servers start. That path already exists; out-of-band (`external`) dispatch simply does not use it.

## Recommended priority

**High.**

**Reason:** it makes a hard constraint unenforceable and pushes agents into divergent workarounds,
and on the third occurrence it blocked a gate outright. Every launch order in this epic carries that
constraint. Worse than the stall is the near-miss: a less careful agent would have claimed a lease on
the demo spine and believed it had claimed its own. The cost is paid in silent divergence, which is
the expensive kind.

## Related artifacts

- `.agent-work/epic-568/ADMIRAL_LOG.md` — the incident and both Commanders' floats.
- `.worktrees/epic-568-510/.agent-work/epic-568-510/FINDINGS-wave2-repair.md`
- `.worktrees/epic-568-530/.agent-work/epic-568-530/FINDINGS-wave2-repair.md`
- [`pycache-root-mismatch-guard`](pycache-root-mismatch-guard.md) — the other stale-path survivor.

## Disposition

**recommend-and-defer**

**Detail:** `recommend-and-defer: no tracker-filing authority was exercised this run, and no wave-2
latitude covers implementing it. The lifecycle/dispatch work it belongs beside is already deferred
to a later high-risk wave by the human's 2026-08-14 ruling.`

## Issue creation authority

Not exercised. The Admiral's delegated classes cover merge-to-main and repo hygiene, not tracker
creation. This document is the durable record until someone with filing authority acts on it.
