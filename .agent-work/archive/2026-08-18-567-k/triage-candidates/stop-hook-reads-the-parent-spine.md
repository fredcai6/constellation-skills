# Triage candidate — the Stop hook told a finished lane to drive its parent's spine

**Not filed.** `decision:no-issue-filing-mid-run` — staged only.
**Observed after lane K's own closeout**, which is why it is appended rather than in the original set.

## Observation — measured at `30c0a59e`

Lane K's spine reached terminal and released its lease. The Stop hook then fired with:

> `SPINE MID-FLIGHT: gate execute is still open -- you are in the MIDDLE of the spine, not at its
> end, so ending your turn now abandons an active run.`

It was reading a **different spine**. Both, read side by side in a fresh process:

```
.agent-work/567-k/spine.json          → LEASE released: constellation/567-k/lane-k/commander-delegated
                                        DONE: no open items.
.agent-work/epic-567-door/spine.json  → LEASE active: constellation/epic-567-door (by admiral)
                                        ACTIVE execute [in-progress]
```

This session's `SPINE_FILE` is the first. The hook reported the second, and pasted the **Admiral's**
`execute` imperative — plan waves, dispatch Commanders, merge PRs — as this lane's "next
imperative". `type`: **measured**, by running `current` against both files. `rev`: `30c0a59e`.

## Why it matters

The hook instructed a finished **Commander** to perform the **Admiral's** job. Complying would have
required driving a spine whose lease is held by a live session, which means supplying **another
agent's session id** — the exact shape of #632, where a cold subagent read a session id out of a
journal and drove a live run under it. It would also have closed, blocked or advanced an epic gate
whose condition is "every epic issue dispositioned" while **lane J is still blocked at c6**.

The hook's own escape hatches do not fit either: it offers `spine_halt block` or a human waiver,
but both would have been applied to the **parent's** gate, falsifying epic state on the Admiral's
behalf. There is no offered exit that is correct for a completed child whose parent is still open.

The cause is almost certainly #269 — hooks execute from the main checkout because
`CLAUDE_PROJECT_DIR` resolves once at session launch — and it is the **same two-spine ambiguity**
that produced the other two gauge findings this run: `CONTEXT GAUGE SILENT` for the whole lane, and
the parent's gauge file being overwritten with this session's reading. Three distinct symptoms, one
root: a child session in a worktree cannot be told apart from its parent.

## Possible fix (hypothesis, not a spec)

Have the Stop hook resolve the spine from the session's own `SPINE_FILE`/`SPINE_SESSION` rather
than from the project root, and treat a terminal-and-released child spine as done even when a
parent spine is open.

## Disposition

`recommend-and-defer`. Fails the fix-now ladder on **adjacent to current scope** — hook resolution
is a cold-start area this lane never opened, and the same subsystem as the two gauge findings. It
should probably be triaged **together** with those, since one fix likely closes all three.

## Not claimed

I did not read the Stop hook's source and did not confirm #269 is the mechanism. I have three
correlated symptoms and a plausible common cause, not a diagnosis. I did **not** attempt any verb
against the Admiral's spine, so I cannot say what it would have done.
