# Resume-side observation — the far end of the #467 round trip

**Companion to `TRIP_OBSERVATION.md`, which is the near end.** That file was written by
`commander-w4-467` as it tripped. This one is written by `commander-w4-467-b`, the cold successor
launched into the same worktree and the same `spine.json`, with **no briefing from the Admiral by
deliberate design** — the launch instruction said so explicitly: *"I am deliberately not briefing you
from my own memory of the run — the whole point is that the spine's own `current` projection carries
everything you need. If it does not, that is a finding."*

This is DC5 evidence: the round trip's second half, recorded by the only agent that can see it.

## What I was given

One command: `checklist_engine.py --file .agent-work/issue-467-trip-semantics/spine.json current`.
Nothing else about the run's content.

## What the handoff carried — and it was enough to act

The `DIGEST` on `current` carried, correctly and unambiguously:

- **that the plan is frozen and I must not re-plan.** First words. This is the single most valuable
  thing in it: a cold agent's default failure mode is to re-derive the design, and it was shut off
  before I could start.
- **the design in one sentence** — HARD refuses the verbs that *begin* work (`start`, `reopen`), not
  `advance`, because `advance --why` is the only writer of the DIGEST and already fails closed on
  silence. I did not have to reconstruct this, and I would not have arrived at the `resume`/`reopen`
  distinction on my own.
- **both cold-critic traps, stated as "do not reintroduce".** DC6's observable is "did anyone BEGIN
  work while over the line", not "did a handoff artifact appear" (true by construction); and
  `advance --mechanical` would reproduce #431 after the fix because `_latest_why_record` skips
  mechanical markers. Two live landmines, disarmed before I stepped on either.
- **the next action** (`start execute`, then drive `execute.json` from `e0-context`).
- **the baseline to hold** (1793 passed, 2 skipped, 683 subtests, real exit 0).
- **a reading-asserted account of its own trip**, and a pointer to `TRIP_OBSERVATION.md`.

**Verdict: sufficient to start from cold.** I began real work inside ten minutes and re-derived
nothing about the plan.

## What it did not carry

Honest accounting, because a smooth resume is the less useful report.

1. **Why, for anything.** The DIGEST is a set of conclusions. Every "why" lives in
   `CRITIC_TRIAGE.md`, `MISSION_FRAME.md`, and `DIT_CONVERGENCE.md`. It names those files, which is
   the right design — but it means the cold-start surface is `current` **plus a rich work area**, not
   `current` alone. **On a run whose artifacts had not been written yet, this handoff would have
   carried conclusions I could not have audited.** My predecessor reached the same conclusion from
   the other side; two independent observations, one from each end.

2. **The launch order.** `LO-467.md` is the dispatch contract — fences, environment invariants,
   pre-rulings, the return format. It is not in the worktree at all; it lives in the Admiral's
   `.agent-work/epic-418-redux/launch-orders/` in the **main** repo, which the same launch order
   fences me *out of writing to*. Nothing in `current` points at it. I found it by guessing that a
   file named `LO-467.md` existed and searching for it. Had I not, I would have missed: the exact
   pytest invocation (`FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`, never `py`, #454), the
   `${PIPESTATUS[0]}` rule, the `gh` markdown-body rule, the ban on inferring merge state from an
   exit code, and the six-part return format. **These are the environment invariants that the epic
   paid for in real incidents, and the handoff does not carry a pointer to them.** This is the
   sharpest gap I found.

3. **The Admiral's rulings are only in one artifact.** `CRITIC_TRIAGE.md` carries three binding
   Admiral rulings and a **binding retraction** of the launch order's own field evidence
   (LO-467 item 2, the 17–21% vs 44% role-blindness reading, withdrawn). A successor that read
   `LO-467.md` and *not* `CRITIC_TRIAGE.md` would have cited retracted evidence as current. Ordering
   saved me — the DIGEST puts `CRITIC_TRIAGE.md` second in its read order — but nothing marks the
   retraction as superseding the LO where the LO itself lives.

4. **One stale line, silently.** `MISSION_FRAME.md` line 85 still reads *"the band refuses
   `start`/`resume`, never `advance`"*. Critic finding 4 **dropped** the `resume` guard and finding 3
   **added** `reopen`. The DIGEST is right and the frame is stale, so I took the DIGEST — but only
   because the DIGEST happened to state that exact distinction. A successor resolving a conflict
   between two durable artifacts has no rule telling it which wins.

## What I had to re-derive

Only one thing, and it was not in the plan: **why the engine was still ordering me to hand off.**
See below. Nothing about the design, the gates, or the evidence.

## The defect the resume found — the round trip does not close as built

This is the part only the far end could see, and it is a **negative result about the mechanism, not
about the design.**

On arrival, `current` printed at me:

```
CONTEXT 31% (>= hard): refresh already requested for execute — hand off now; do not keep working.
```

That reading is not mine. Measured directly from the transcripts the gauge hook itself reads:

| agent | tokens | fill | last turn |
|---|---|---|---|
| `acommander-w4-467-b-…` (me) | 64,577 | **6.5%** | 2026-08-08T10:13:18Z |
| `acommander-w4-467-…` (predecessor) | 313,521 | **31.4%** | 2026-08-08T10:12:40Z |

`.agent-work/.spine-rail-binding.json` holds a **live binding for both of us**, and both resolve to
the same `.agent-work/issue-467-trip-semantics/gauge.json`. The binding registry is keyed per-agent
(`session_id#agent_id`, #419) precisely so that readings are not misattributed — and then every key
resolves to a single **spine-derived** gauge path. Last writer wins. I watched my own `0.039` get
overwritten by the predecessor's `0.308` inside one tool call.

`gauge_writer_hook.handle_post_tool_use` has an `ambiguous-binding` guard, but it fires when **one
key resolves to many paths**. The handoff is the mirror case — **many keys, one path** — and it is
unguarded. Note the history: LO-467 records that this hook was silent on the orchestrator tier for
~nine hours of this epic because it counted *bindings* rather than *distinct paths*, fixed in #488.
That fix is correct and its replacement is what I hit: counting distinct paths makes two agents on
one spine look unambiguous, because as far as the *path* is concerned they are.

**Consequence.** A resumed Commander reads as over the line the instant it starts, so the engine
tells it to hand off again, and the successor after that inherits the same thing. The round trip
**loops** instead of closing. This is not an edge case: trip and resume necessarily share a spine, so
this is the exact shape the design guarantees at *every* handoff.

**Why it did not stop me.** The shipped HARD band guards only `advance` — I verified that `start
execute` refuses on unmet preconditions and not on context, exactly as the frozen design describes.
So I could open the gate and work. I would have hit the wall at the first `advance`. I reported this
to the Admiral and did not waive a governor stop on my own judgement.

**Fix direction, recorded as a triage candidate and not implemented here** (it is outside #467's six
done-conditions): the engine already knows who owns a spine — it holds a **lease**. I force-claimed
that lease on arrival; the predecessor has not held it since. A gauge writer that declines to write
for an agent that does not hold the spine's lease would resolve this using a mechanism that already
exists, rather than adding one. Routed, not decided.

## Positive control, and what it is worth

The round trip's first half was already known to work: LO-467 records three successful hand-runs in
earlier waves, and my predecessor's was the fourth. What was untested was the far end. It now has one
observation: **the handoff's *content* carried; the handoff's *instrument* did not.** A cold
successor can reconstruct the work from `current`. It cannot, as built, be told it has room to do it.

That is a better result for #467 than a clean resume would have been, and it is the kind of thing
DC5 exists to catch — DC1–DC3 were all satisfiable while this was true, because none of them look at
the far end.
