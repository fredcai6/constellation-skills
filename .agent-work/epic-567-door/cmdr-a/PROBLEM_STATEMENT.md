# Problem statement — `cmdr-567-a`

Reconciled against the frozen `LANE_A_LAUNCH_ORDER.md` (no reachable human;
delegated mode). Measured in my worktree at `600de020`. Written per
`constellation-how-to-talk`.

## The ask, restated

Make a role agent able to reach **its own** spine through the MCP door, and make
`checklist_engine.save()` safe against concurrent writers.

## What the order assumed, and what the code actually says

`commander-core.md` requires me to reconcile the order's assumed baseline against
the code before planning, because "a headline mechanism the order treats as
unimplemented may already be shipped." It is. This is the single most important
finding of the `understand` step.

**The order's premise:** "the door binds `SPINE_FILE`/`SPINE_SESSION` as
module-level constants at launch."

**Half of that is already false at `600de020`.** The previous lane A
(`cleanup/a-door`, #603/#604/#605, merged at `33dc3086`) already did the hard part
under `decision:bind-on-open-over-new-verb`:

- `_bind_process_to(spine_file, session)` (`scripts/mcp_spine_server.py:878`) is a
  named, module-level rebinder that reassigns `SPINE` and `SESSION` and keeps
  `os.environ` in step.
- The four import-time derivations of `SPINE` that made rebinding unsafe
  (`CALLLOG`, `START_MARKER`, `REJECTIONLOG`, and `_resolve_confined`'s
  `bound_dir` default argument) were all made late-bound.
- `_unbound_refusal()` is asked **per call, never cached**, explicitly because
  "`spine_open` can rebind this process to a different spine mid-life."
- A module-wide AST pin in `tests/test_mcp_lifecycle.py` asserts the set of
  assignments to `SPINE`/`SESSION` is exactly {module scope, `_bind_process_to`}.

So the door is **not** immutably bound at launch. It can already rebind, safely,
with a guard and a test pin around the one place that does it.

**What is actually missing is one thing: a trigger.** `_bind_process_to` has
exactly one caller — `_spine_open` at `:1041` — and `spine_open` **mints**. It
creates a worktree, a branch, a work area and a compiled spine. Its own tool
description says it "acts on a spine that does not exist yet." There is no verb
that binds the door to a spine that **already exists**.

That is the whole defect, and it is much smaller than the order's framing implies.

## The defect, stated generally

**Any role that did not personally launch its own door has no door path to its own
spine.** Reproduced in my own process at step one of this run, with my spine on
disk and its lease held by me:

```
mcp__spine__spine_status  ->
REFUSED: no spine is bound to this door, so there is nothing for this tool to act
on. Call `spine_open` to mint a spine and bind this process to it, or relaunch
this door with SPINE_FILE set to an existing spine file.
```

Both remedies the refusal offers are unavailable to me. `spine_open` would mint a
second spine I do not want. "Relaunch this door" is not something a dispatched
agent can do — the door's lifetime is its session's, and a subagent cannot
relaunch its dispatcher's MCP server.

`#559` as filed describes the narrower Task-tool-crew case. The order's
`decision:solve-the-general-case` pre-ruling widens it to any role, grounded in
the Admiral's own failure. My measurement confirms the wider statement: the tier
does not matter, only whether the process launched its own door.

**Consequence for the epic.** The CLI is currently the *only* path for every such
agent, so epic #567's deliverable — deleting 15 `CLI fallback` clauses and 11
`<engine>` tokens (both counts re-measured and confirmed at `600de020`) — is
blocked until a door path exists. You cannot delete the only path.

## The second half: `save()` atomicity (#613)

`scripts/checklist_engine.py:255` ends `save()` with a bare
`Path(path).write_bytes(payload)`, and `load()` at `:220` is a bare `read_text`.
`write_bytes` truncates then writes, so a reader concurrent with a writer can see
a partial spine, and a crash mid-write leaves the spine permanently corrupt. My
own spine is 35KB, far past any single-write atomicity.

**Scope boundary I hold to deliberately.** Atomic replace fixes torn reads and
corruption. It does **not** fix lost updates: two writers that each
load-mutate-save still clobber each other and leave a well-formed file. That
read-modify-write race is #613's other half (the parent heartbeat as second
writer) and my order scopes me to "the atomicity half." Lane G's incident this
wave is that other half observed live — its own crew and its own context-inheriting
fork drove one spine under one lease id — and nothing in my lane prevents it.
Recorded as a triage candidate, not fixed.

## Protected intent — what must not change

- `decision:one-spine-per-process-stands`. One process drives exactly one spine at
  a time. A fix may change *when* the binding is decided; it may not raise the
  count.
- `_identity_violation`'s semantics. It compares argv against `SPINE` at **call**
  time and refuses any argv naming another spine. It must keep doing exactly that.
- The module-wide AST pin on `SPINE`/`SESSION` assignments. Nothing may assign
  those names outside `_bind_process_to`. This is a constraint on every candidate
  and a free regression check on the winner.
- `tests/test_mcp_lifecycle.py:137` pins every `return` in `call_lifecycle_tool`
  to literally `_spine_open(args)` / `_spine_close(args)`, and `:194` bans the
  identifiers `SPINE`, `SESSION`, `run_engine` from `_spine_open`'s own source.
  Both were left byte-identical by the previous lane and constrain where new
  dispatch may sit.
- `decision:isolation-not-fencing` (order pre-ruling). Whatever replaces "one file
  per process" must be stated explicitly, including what an agent can now reach
  that it could not before. Silently widening reach is a regression even if every
  test passes.
- `decision:net-deletion`. The lane must end with something deleted.

## Correction to the order (measured, not blocking)

The order cites "`mcp_spine_server.py:164` `_identity_violation`". At `600de020`
that function is at **`:443`**; `:164` is inside `_spine_from_env`'s docstring. The
previous lane's rewrite moved it. The order's substantive claim about the function
— that it already confines `from_child` to paths under `SPINE.parent` via
`_resolve_confined` — is correct.

## Out of scope

`scripts/hooks/*` (untouched — relevant to the Admiral's merge sequencing),
`map/ids.jsonl` (degraded repo-wide, not mine), the doctrine sweep of the 15
fallback clauses and 11 `<engine>` tokens (wave 2), #613's lost-update half, and
filing any issue (`decision:no-issue-filing`).
