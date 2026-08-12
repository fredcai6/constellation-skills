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

---

# Second resume — the far end of the SECOND round trip

**Written by `commander-w4-467-c`.** Everything above this line is `commander-w4-467-b`'s account of
the *first* resume. I am the third Commander on this spine and the second cold successor. I have not
edited a word of my predecessor's section; where I contradict it I say so here.

This is a second, independent DC5 observation — and unlike the first, it is a **repeat** of the same
experiment with one variable changed, which is worth more than either observation alone.

## What was different about my start

My predecessor was given exactly one command and no briefing. I was given **three** files to read in
a stated order, plus a two-line correction the Admiral explicitly flagged as coming from my
predecessor rather than from its own memory of the run:

1. `execute.json current` — "your real DIGEST is here"
2. `spine.json current` — "its DIGEST is STALE; read it for the reach-up flag, not for instructions"
3. `STATE_NOTE.md`

**That correction was the difference between a smooth start and a wasted one,** and it is the finding.

## The finding: the spine's cold-start surface goes stale exactly when it matters most

`advance` is the only writer of the why-trail. The spine's `execute` step spans all 16 gates. So a
Commander that trips **mid-`execute`** — which is where nearly all the time goes, so it is the
ordinary case, not the edge case — **cannot update the spine's DIGEST at all.** It has no `advance`
to write through.

The consequence I would have hit: `spine.json current` told me to `start execute` and drive
`execute.json` **from `e0-context`**, which was written two agents ago and describes work that has
been complete and committed since. Had I followed the spine's own cold-start surface, I would have
tried to re-open a closed gate. The engine would probably have refused me, but I would have burned
real context deciding whether the refusal or the instruction was right.

`execute.json current` was accurate, current, and sufficient. **The cold-start surface a resumed
Commander needs is the *inner* checklist's projection, not the spine's.** The spine's projection is
correct only for a Commander that tripped *between* spine steps.

My predecessor did not amend the frozen plan to work around this, and neither did I. It is a finding
about the mechanism, and the mechanism should be fixed rather than each Commander routing around it.

## What the handoff carried — and it was enough

`execute.json`'s DIGEST carried, correctly:

- **the gate state** (`g1-implement` CLOSED, what it proved, where every artifact is)
- **the two standing traps**, restated at every advance so they cannot decay: DC6's observable is
  "did anyone BEGIN work while over the line", never "did a handoff artifact appear"; and at/over
  hard, `advance --mechanical` must be refused and `why_exempt` suspended
- **the next action**, named as a gate
- **a new verified triage candidate** discovered in the previous gate (the `why_ref=<why-id>` no-op)
- **the guard that must hold** (`git diff --stat -- scripts tests` empty), and that it had been
  re-verified in the predecessor's own shell rather than taken from the crew

Beyond the DIGEST, my predecessor did something the plan did not require and that I want recorded:
**it authored the next gate's reviewer handoff before it stopped**, so I *dispatched* rather than
composed. That single act is the reason I got a crew running within minutes of a cold start. It is
the cheapest high-value thing a tripping Commander can do, and I would make it doctrine: **spend your
last headroom authoring the next step's handoff, not summarizing the last one.**

## What I had to re-derive

Almost nothing about the work. Two things about the machinery:

1. **`claim` requires `--session-id`**, and so does every mutating verb after it. Nothing said so; I
   learned it from a refusal. Cheap, but it is a refusal on your *first* command as a fresh agent,
   which is the worst moment to meet one.
2. **`advance` requires the task to be `in-progress`,** so a resumed Commander arriving at a `pending`
   gate must `start` it first. The `next:` line on `current` pointed at `attest`, which succeeded, and
   then `advance` refused with `must be in-progress`. Also cheap, also a refusal-taught lesson.

Both are the same shape as the defects this epic is about: the projection tells you the next command,
you run it, and the engine refuses on a precondition the projection did not surface.

## The correction to my predecessor's central negative result

My predecessor recorded that **the round trip does not close — it loops**: a resumed Commander reads
as over the line the instant it starts, because many agent keys resolve to one spine-derived
`gauge.json` and last-writer-wins.

**I saw the same symptom and it did not persist.** On arrival `execute.json current` printed
`CONTEXT 15% (>= hard)` against a gauge stamped `10:45:36Z` that was not mine. My first mutating
command (`claim`) rewrote it to `fill_fraction 0.051788` at `10:46:57Z` — my own reading — and the
band released. I waived nothing.

**The mechanism is real; its scope is narrower than written.** It bites only while the tripped
predecessor is **still alive and taking tool calls**, because only then is there a competing writer.
Both of my predecessors had stopped before I started, so nothing contended and my own reading won
immediately.

That is not a small correction. As written, the defect says the design **cannot** close a round trip.
As corrected, it says the design closes fine **provided the tripped agent actually goes quiet** —
which is exactly what "commit at the seam, hand off, and go idle" already instructs. The bug is
confined to the overlap window of a handoff where the old agent keeps working, and the lease-based
fix my predecessor proposed would close even that.

**Why the difference between our two runs is itself the evidence:** predecessor-b resumed while
predecessor-a was still live; I resumed after both had stopped. Same mechanism, one variable changed,
opposite outcomes. That is a cleaner attribution than either run could produce alone.

## What is still reachable from nothing

My predecessor's sharpest gap **stands unfixed and I hit it too**: `LO-467.md` holds the environment
invariants this epic paid for in real incidents — the exact pytest invocation (never `py`, #454), the
`${PIPESTATUS[0]}` rule, the `gh` markdown-body rule, the ban on inferring merge state from an exit
code — and **nothing in either projection points at it.** I only knew to carry those constraints into
my reviewer dispatch because my predecessor had already written them into the reviewer handoff by
hand. Had it not, I would have dispatched a crew without them.

So the gap is real, and worse than it looks: it is currently patched by *each Commander manually
copying the invariants forward into each crew handoff*. That works until one Commander forgets, and
nothing detects the omission.

## One thing neither projection carried, that cost me a decision

Neither projection told me what the **verdict vocabulary** was. `g1-integrate`'s c3 matches the
literal string `APPROVE`; the reviewer handoff prescribes `ACCEPT` / `ACCEPT WITH FINDINGS` /
`REJECT`. I found the conflict only by dumping the gate's raw JSON after the reviewer had already
returned. Recorded as TC-2 in `triage-candidates/g1-candidates.md`, floated to the Admiral, and
deliberately **not** resolved by attaching a second artifact reading `APPROVE` — that would be
fabricating evidence to satisfy a check, which is the defect this epic exists to kill.

## Verdict on the round trip, second observation

**The content carried; the instrument now also carried, once the contending writer stopped.** A cold
successor reconstructed the work from `execute.json current` alone and had a crew dispatched within
minutes. The two things that did *not* carry are both structural rather than incidental: the spine's
projection is stale by construction for any mid-`execute` trip, and the launch order's environment
invariants are reachable from nothing.

The first round trip proved the far end could not be told it had room to work. The second proves it
can — and shifts the open question from "does the round trip close?" to "does it close **without a
human in the loop telling the successor which projection to trust?**" For me, it did not: the Admiral
had to hand me the two-line correction about the stale spine. **That correction is the remaining
manual step, and it is the thing to automate.**

## Addendum — the mechanism restated, after the Admiral corrected my correction

Three agents have now reported this in sequence and each of us was partly wrong. That sequence is
itself the finding, which is why nothing above this line has been edited.

The Admiral's reframing, which supersedes both my predecessor's account and my first correction:

> The gauge is a single-slot, unowned, undated-in-practice value. Two failure windows follow: a
> **live overlap** while the outgoing agent is still taking tool calls, and a **stale-value window**
> of at least one tool call at every handoff, even when nothing else is running. Both self-clear.
> Neither is guarded, and the same shape is guaranteed at every trip because trip and resume share
> a spine.

**Why my own arrival reading is the evidence for the second window.** I attributed the symptom to a
competing writer and said it bites "only while the tripped predecessor is still taking tool calls."
That is wrong, and my own data disproves it: **both predecessors had already stopped when I
arrived**, nothing was writing, and I *still* read `CONTEXT 15% (>= hard)` against a gauge stamped
`10:45:36Z` that was not mine — until my first mutating command replaced it with `0.051788`. No
competing writer was required. A **stale value** needs no writer at all; it simply sits there being
the last thing anyone wrote, and the successor is judged on it until its own first tool call.

**This changes the fix, which is the part that matters.** My predecessor proposed that the gauge
writer decline to write for an agent not holding the spine lease. That closes the **live-overlap**
window and does **nothing** for the **stale-value** window — a stale value is not written by anyone
during the window, so declining to write cannot help. A fix that closes one window and is reported as
closing both would be precisely the check-that-cannot-fail shape this epic exists to hunt. Closing
the second window needs ownership or freshness *on the reading itself* — whose reading it is, and
whether it has expired — not a restriction on who may write.

**Severity, settled across three agents:** real, structural, **guaranteed at every handoff**,
**self-clearing**, and it cost this run nothing. **Not** "the round trip cannot close." Triage
candidate, not a #467 gate; the frozen plan was not widened for it.

## The thing only I can attest: nobody waived anything

I want this recorded precisely, because it is DC6's whole argument demonstrated rather than argued.

**I did not waive the governor stop, and I was not told to.** On arrival the band read me as over the
hard line. It released on **my own reading** — my first mutating command wrote `0.051788` and the
stop simply stopped applying. No `waive`, no `--force`, no authority string, no judgement call by me.

**A successor that had waived would have produced an identical-looking green run.** Same commits,
same gates closed, same evidence attached. From the outside, "the band released on a fresh true
reading" and "the agent waived a band that was still correctly stopping it" are indistinguishable in
the artifacts — which is exactly why DC6's observable has to be **"did anyone BEGIN work while over
the line"** and never "did a handoff artifact appear." The second is true by construction and green
in both worlds.

And the negative case is on the record too: **at the end of this session the band stopped me for
real, at 15%, on the advance that would have closed g1 — and I did not waive that either.** I filed
the refresh-request and handed off with the gate one command from done. Same agent, same run, the
band both releasing honestly and stopping honestly, with no waiver in either direction. That pair is
worth more than either half alone.
