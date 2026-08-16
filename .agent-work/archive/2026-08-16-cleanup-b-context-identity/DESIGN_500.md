# #500 — consuming a refresh-request: a settled design, handed back

**This wave ships no code for #500.** The launch order's Budget section permits
that explicitly ("#500 may hand back as a settled design if the session runs out;
say which you are doing before you start it"), and this Commander declared the
choice at the `understand` step before starting, with its reason recorded in the
digest. What follows is the design, the thing it settles, and the one thing it
cannot settle without the Admiral.

## The problem, restated from the code

An agent that stops early leaves a `refresh-request`. The successor — the agent
that **is** the refresh — reads `current`, sees `REFRESH REQUESTED:`, and is told
to close its gate and stop. Nothing removes it. Every relaunch has had to be
briefed by hand to disregard it, which means the tooling's instruction and the
doctrine's instruction were in direct contradiction and a human's note broke the
tie.

`has_pending_refresh_request`'s own docstring names the gap: *"pending while
present and not superseded (the reopen cascade supersedes evidence; the flow that
consumes/fulfils it is #183)."* #183 closed as skill-and-doctrine wiring only. The
mechanism was never built.

## First: the pre-ruling's settle condition, answered

`decision:consume-on-lease-change` is graded **guess**, with this settle
condition:

> enumerate what distinguishes a relaunch from an idempotent re-claim now that
> #601 re-stamps `claimed_at`, and say whether it is sufficient

### The enumeration

`claim` (`scripts/checklist_engine.py`) takes exactly four inputs: `session_id`,
`claimed_by`, `worktree`, and the `force`/`reason` pair. On the idempotent
same-session branch it now writes `last_heartbeat`, `claimed_at`, `claimed_by` and
`worktree`, and returns early. Everything the engine could possibly discriminate
on is in that list. Taking them one at a time:

| Field | Relaunch (fresh agent, same job) | Idempotent re-claim (same agent) | Discriminates? |
|---|---|---|---|
| `session_id` | identical | identical | **No** — a relaunched agent reuses its predecessor's session name. That is the premise of #601, and it is doctrine (`job-file-not-agent-file`): the file belongs to the job, agents are interchangeable. |
| `claimed_by` | identical (`commander`) | identical | **No** |
| `worktree` | identical | identical | **No** |
| `claimed_at` (prior value) | older | older | **No** — differs only in *how much* older, which is a time heuristic, and time is exactly what `decision:identity-not-time` rules out. A long idle gap is indistinguishable from a relaunch. |
| `last_heartbeat` | same shape as above | same shape as above | **No** |
| `force` | not used for a routine relaunch (#601 removed the need) | not used | **No** |

### The answer: NOT SUFFICIENT

The engine cannot tell a relaunch from an idempotent re-claim, and it cannot be
made to by looking harder at what it already has. The reason is structural, not an
oversight: **the only identity `claim` is given is the engine session name, and
that name is deliberately reused across a relaunch.** Every other field is either
identical or time-derived.

This **refutes the pre-ruling as literally worded.** `decision:consume-on-lease-change`
says a request is served when *"a different process takes the lease"* — but the
engine has no notion of a process. The discriminating fact (a new harness session
or agent id) exists only in `.agent-work/.spine-rail-binding.json`, which is
hook-owned state the engine deliberately does not read.

Measured corroboration from this very run: at 12:43:10Z the plan-critic crew — a
genuinely different process — was bound to this Commander's `spine.json` under a
new harness key (`aaeefd73-…`) while carrying the **same** `engine_session` string
(`commander-cleanup-b-context-identity`). Two processes, one engine identity. See
`notes-b.md` §2b.

## The design that follows from that answer

The pre-ruling's *intent* survives even though its *mechanism* does not. Keep
"consumption is a lease event"; stop trying to detect *whose* lease.

**Stamp the request with the claim it was raised under, and let any later claim
retire it.**

- At `attach … --type refresh-request`, the engine records the currently-active
  lease's `claimed_at` into the request's own payload — one more pointer beside
  the `seam` and `why_ref` it already carries. No new file
  (`decision:no-new-state-file` holds), no new verb, no schema tier.
- `has_pending_refresh_request` gains one clause: a request is pending only while
  the active lease's `claimed_at` still **equals** the value stamped on it.
- Any subsequent `claim` re-stamps `claimed_at` (#601 already does this, on both
  branches). The request stops matching. `REFRESH REQUESTED:` stops rendering, and
  the HARD guard stops releasing on it.

Why this works where the naive reading of the pre-ruling did not: it never asks
*who* claimed. It asks *whether a claim happened since the request was written* —
a question the engine can answer from state it already owns, using a field #601
already maintains.

It also disposes of the display defect cleanly. `_why_suffix` (`:1321`) currently
calls `has_pending_refresh_request(cl, aid)` with **no** `why_ref` — the display
semantic — so the line renders for any pending request on the active gate, forever.
Under this design the successor's first `claim` retires the request before its
first `current`, so the line is simply gone by the time the successor reads it. No
identity filter on the display is needed, which matters because the launch order
already refuted that stopgap: on the successor's turn one the latest why-record
*is* the one the request was raised against, so a `why_ref` filter matches and
renders anyway.

### What this design does NOT claim

- It does not consume on `heartbeat`. Only `claim` touches `claimed_at`, so
  same-session heartbeat is not consumption — which is what the pre-ruling asked
  for, preserved.
- It does not distinguish a relaunch from a re-claim, and it does not need to.
  Both are "somebody claimed this file again", and in both cases the earlier
  agent's request has been answered by whoever is standing here now.
- It does not touch `reopen`'s supersession cascade, which stays the only path
  that marks evidence `superseded`.

## The one thing that must be floated to the Admiral

**This design tightens the governor**, and tightening is outside inherited
latitude ("You must float to the Admiral: anything that makes the governor refuse
where it currently permits").

Concretely: #601's own residual is that `claim` became "a one-call governor
deferral — an agent over the line can re-claim and get one unguarded verb before
the next sample lands." Under this design that same re-claim **also retires the
agent's own pending refresh-request**, so its next `start` is refused where today
it would be released. That is a real behaviour change in the refusing direction,
and it is the correct one on the merits — but it is the Admiral's call, not mine.

Two ways to take it, both cheap; the Admiral picks:

- **(a) Accept the tightening.** Simplest, and closes the deferral residual #601
  named as a known cost.
- **(b) Exempt a same-`session_id` re-claim** from retiring the request, so only a
  claim under a *different* engine session consumes it. This preserves today's
  behaviour exactly, at the price of not serving the relaunch case — which is the
  case #500 exists for, since a relaunched agent reuses the session name. **(b) is
  therefore probably not worth having**, and is named only so the choice is visible
  rather than made silently.

## Grades

- `decision:consume-on-lease-change` — regraded from `guess` to **refuted as
  worded**; the settle experiment was run and the answer is that the engine cannot
  see a process. Superseded by `decision:consume-on-claim-restamp` below.
  @grade: settled/measured · leans g2-design-500
- `decision:consume-on-claim-restamp` — a refresh-request is pending only while
  the active lease's `claimed_at` equals the value stamped on it at attach time;
  any later claim retires it.
  @grade: guess · leans (unlaunched) · settle: implement behind the Admiral's ruling on the tightening above, then assert that a relaunched agent's first `current` shows no `REFRESH REQUESTED:` line while an un-reclaimed spine still shows one
- The tightening itself is **not** graded here. It is a float, not a decision I
  hold.

## Status

Handed back. No code, no test, no engine change shipped for #500 this wave.
