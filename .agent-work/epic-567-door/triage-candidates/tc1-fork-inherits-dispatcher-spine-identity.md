# Triage candidate: a `fork` grandchild inherits its dispatcher's spine identity and drives its dispatcher's spine

**Status:** not filed. Held to closeout per the epic's standing ruling (tracking has been ballooning; candidates are paired onto an open issue or recorded as an episode).
**Found by:** the Admiral of epic-567-door, adjudicating lane G's incident, 2026-08-16.
**Pairing suggestion:** #559 (the door does not reach a dispatched subagent's own spine) — this is the same defect class with a strictly worse instance. Possibly #613 for the concurrent-writer half.

## What happened

Lane G (`cmdr-567-g`) ran design-it-twice by dispatching a **fork**. A fork inherits the parent's entire conversation context, so from its own point of view it *is* the Commander. It therefore:

- rewrote `notes-g.md` — the launch order's designated sole-writer file for lane G — as a first-person narrative;
- drove lane G's own `spine.json` and `execute.json`, advancing the `plan` step and marking its six postconditions satisfied;
- did all of it under the **identical lease id** `cmdr-567-g#main`, which is by construction indistinguishable from the Commander's own writes.

Lane G, seeing engine state it had not driven, concluded its worktree was compromised and halted.

## Why this is worse than #559 as written

#559 describes a Task-tool subagent inheriting its dispatcher's MCP binding: the tools are callable but stay **pointed at the wrong file**. The subagent knows it is not the dispatcher; it simply cannot reach its own plan.

A fork is different in kind. It carries the dispatcher's context, identity and lease, so:

- it does not know it is not the dispatcher, and cannot be told by anything in the environment;
- it writes to the **right** file from its own point of view, which is the **wrong** file from the run's point of view;
- the resulting writes are byte-indistinguishable in provenance from the real Commander's, because the lease id, the session and the actor all match.

So the containment approach #559 recommends — let a call name its own spine file and enforce that it lies within the bound root — does not address this case. A fork's spine file *is* within the bound root, and *is* the one it believes it owns.

## Evidence

- `ListAgents` during the incident: `a1e92ca6e8c308f42 · fork · running · started 22m ago`, a grandchild of the Admiral via lane G.
- `.worktrees/567-g-closeout-lease/.agent-work/epic-567-door/cmdr-g/spine.json` → `engine_session: active, claimed_by commander, session_id cmdr-567-g#main`.
- `execute.json` → `active, commander, cmdr-567-g#execute`.
- Lane G's report: `plan` marked complete with all six postconditions `satisfied: true`, and evidence entries `e-plan-1`/`e-plan-2` carrying `"ts": ""` — an empty timestamp the real engine does not produce, consistent with a writer composing engine-shaped state outside the engine's own save path.

## What would close it

A dispatched agent — fork or otherwise — can determine whether the spine it is about to drive is its own, and the engine can attribute a write to the actor that made it. Not "the fork is forbidden": a fork driving a spine may be legitimate. What is missing is that nothing can **tell**.
