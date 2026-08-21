# Lived cluster evidence — reproduced by this run, 2026-08-21

> Input for the architecture candidate lanes. Every item below was hit by this
> epic's own execution on current code, not read off an issue. Where a
> workaround was used, the workaround is named — a candidate that still needs
> it has not solved the problem.

The cluster under design is #634, #638, #632, #357, #369, #615. This run
reproduced four of the six in a single session while doing ordinary Admiral
work. That is the strongest available evidence about which root cause
dominates, and it is not recorded anywhere else.

## The packet's open question

The approved `wave1-complete-map-repair` packet states the unknown as:
"whether the dominant root is duplicated plan state, missing parent authority,
or an interaction between them." The lived evidence below bears directly on
that question. Candidates should treat it as data, not as a conclusion — it is
one run, and a run driven by an Admiral, which is the most privileged actor in
the system and therefore not a representative sample.

---

## E1 — #638: the door's binding is fixed to one checkout, so a parent cannot inspect its own children

**What happened.** The Admiral needed to relaunch a Reviewer against a spine
living in a sibling worktree (`/tmp/constellation-20260820-613/.agent-work/`).
A subagent on this harness shares the parent's MCP door. The door's own
contract refuses that bind:

> "Confined to one checkout's work-area tree per process, enforced by path --
> refused for a spine outside this door's own checkout's `.agent-work/`,
> including a sibling worktree of the same repository."

**Consequence.** No crew dispatched from this harness can be engine-railed at
all, because every crew's spine is by construction in another worktree. The
run's workaround was to declare all crew lanes **unrailed** and hand-write the
prohibition into each handoff.

**What this costs.** The engine rail is the mechanism that makes crew work
auditable. Losing it for every dispatched lane is not a small degradation; it
means the run's evidence quality rests on handoff prose and Admiral
re-verification instead of on the engine. This run compensated by
independently reproducing every crew claim, which is expensive and does not
scale.

**Design obligation.** A candidate must state whether a parent can drive or
even read a child's spine, and if not, what replaces the rail for dispatched
work.

## E2 — #632: helper agents inherit the launcher's spine, so the dispatcher strips it by hand

**What happened.** Every subagent launched in this run inherits the Admiral's
`SPINE_FILE` and `SPINE_SESSION`. Nothing in the harness prevents a crew from
calling a door verb and driving the **Admiral's epic spine** by accident.

**Workaround used.** Each of the three handoffs written today carries a
hand-authored clause: *"Do NOT call any `mcp__spine__*` tool — the door in your
session is bound to the Admiral's epic spine and driving it would corrupt the
run."* This is exactly the "every dispatcher must strip four variables by hand"
that #632 describes, in its prose form rather than its env-var form.

**Prior independent sighting.** A standing lesson from an earlier run records
the same seam from the crew side: *"your `SPINE_*` env is the parent's; author
your own plan, never drive that spine."* Two runs, two roles, same defect.

**Design obligation.** A candidate must make the failure closed rather than
prose-guarded. If the answer is "the dispatcher strips env," say who guarantees
it and what happens when they forget.

## E3 — #357 / #615: a dead session's lease on a child plan is unreclaimable and unguarded

**What happened.** The prior Admiral session and its dispatched Reviewer died
together. The Reviewer's plan was left stranded:

```
file:        /tmp/constellation-20260820-613/.agent-work/20260820-issue-613/repair-reviewer-plan.json
session_id:  repair-reviewer-613-20260820
status:      active
claimed_at:  2026-08-21T02:12:56Z
heartbeat:   2026-08-21T02:15:01Z   (dead)
gates:       r0..r3 complete, r4-quality pending
```

The Admiral's own force-claim of the **epic** spine bought nothing over this
child plan — they are separate leases with no relationship. There is no verb
that reclaims it from outside, and nothing guards it either: it simply sits
`active`, owned by a process that no longer exists.

**Workaround used.** The Admiral ruled the stranded plan **superseded** by
hand, in prose, in the log, and dispatched a fresh unrailed review instead.
Nothing in the system records that the stranded plan is dead.

**Design obligation.** This is the strongest single piece of evidence for the
"missing parent authority" hypothesis. A candidate must say who can declare a
child plan dead, and how that declaration is recorded where the next reader
will see it.

## E4 — #369: force-claim attribution is preserved on the spine, absent on the child

**What happened.** The Admiral's takeover of the epic spine recorded both
`previous_session_id` and a `takeover_reason` — so on this surface the
attribution complaint in #369 appears **already addressed**. The stranded child
plan in E3 has no equivalent path at all.

**Design obligation.** #369 may be partly closable on evidence. A candidate, or
the reconciliation lane, should check whether its remaining live half is really
just E3 in another costume. An honest "this issue is mostly already fixed" is a
valuable finding.

## E5 — prior-run lessons bearing on the same cluster

Two standing lessons from earlier runs, recorded before this epic:

- **Archive-move deadlock.** `git mv`-ing a bound `spine.json` deadlocks bind
  and release; recovery is a temp-copy-back, never a hand edit. This is #638's
  "a run cannot move its own work area," observed as a hard failure.
- **Self-waive refused, parent handshake.** The engine refuses a crew waiving
  its own bound spine's check. Recovery is a five-step dance:
  release → parent claims → parent waives → parent releases → child reclaims.
  This is a parent-capability transition performed entirely by hand, and it is
  precisely what #634 and #357 are about.

---

## How candidates should use this

1. **Do not treat the four reproductions as a ranking.** They are what one
   Admiral-driven run happened to hit. Frequency here is not importance.
2. **Use the workarounds as acceptance tests.** For each of E1–E5, state
   plainly whether your design removes the workaround, keeps it, or replaces
   it with a different one. "Keeps it, and here is why that is acceptable" is a
   legitimate answer; silence is not.
3. **The five-step handshake in E5 is the sharpest test.** Any candidate
   claiming to fix parent capability should be able to say what that sequence
   becomes.

---

# CORRECTION — appended 2026-08-21, after Lane C

**E1 as written above overstates its case, and the Admiral wrote it.**

E1 says: *"No crew dispatched from this harness can be engine-railed at all."*
The qualifier "from this harness" is doing more work than the surrounding prose
admits, and the section then generalizes to "losing it for every dispatched
lane," which is false.

**What is actually true.** `run_crew.py --backend cli` spawns a real child
process and **assigns** that child its own `SPINE_FILE`, `SPINE_SESSION`, and
`SPINE_PARENT` (`_crew_door_env`, `scripts/run_crew.py:1078-1086`). The child
gets its own door in its own process bound to its own spine in its own
worktree. **A `run_crew`-dispatched crew is fully railed.** The `--spine` flag's
own contract states this: "On the cli backend, bound into the spawned child's
`SPINE_FILE` (and its assignment-keyed `SPINE_SESSION`, derived from
`--work-id`/`--gate`/`--role`) so the door resolves to this crew's own spine."

That code even records a *fixed* instance of #632's shape: `_crew_door_env`
assigns rather than `setdefault`s precisely because "a door-bound dispatcher's
own `SPINE_FILE`/`SPINE_SESSION` silently win over the value being derived for
a child... so the child claimed the DISPATCHER's lease instead of its own."

**So the rail loss is a property of the dispatch CHANNEL, not of the system.**
It applies to in-session Agent-tool subagents, which share the parent's door.
It does not apply to `run_crew --backend cli`.

**Why this matters to a candidate.** A design that fixes "parents cannot rail
their crews" may be solving a problem that only exists on the channel this epic
happened to use. Two lanes reached this independently: Lane B observed that all
three of this epic's Wave 2 dispatches went through the Agent tool rather than
`run_crew`, "which is exactly where my design buys nothing"; Lane C disputed
E1's framing directly from the source.

**Standing sampling bias.** This epic's lived evidence over-samples the
in-harness Agent-tool path and under-samples `run_crew --backend cli`. E2 is
affected the same way. Treat every E-item as evidence about *one* dispatch
channel until shown otherwise, and note that Lane C proposes an experiment —
run one wave entirely via `run_crew --backend cli` and see whether E3 and E5-b
still reproduce — that would settle it.

**E3, E4 and E5 are unaffected.** Stranded child leases, attribution, and the
five-step handshake were all observed on plan files and engine verbs, not on a
dispatch channel. The Admiral's independent count stands: 58 plans hold a live
`active` lease, 54 of them archived with dead owners.

---

# CORRECTION 2 — appended 2026-08-21, after Lane A

**E3's central claim is wrong, and the truth is worse.**

E3 says: *"There is no verb that reclaims it from outside, and nothing guards it
either."* The second half is right. The first half is false, and the Admiral
wrote it without testing.

**Measured, not inferred.** The Admiral copied the stranded
`repair-reviewer-plan.json` to scratch and drove the engine against the copy
(the real file was never touched):

```
lease:              repair-reviewer-613-20260820   status: active
heartbeat:          2026-08-21T02:15:01Z
lease_stale_seconds: 1800   ->   _is_stale: True

require_session(advance, 'a-total-stranger-session'):
  refused -> "checklist lease 'repair-reviewer-613-20260820' is stale;
              `claim` it (same id or --force --reason) before mutating"

claim('a-total-stranger-session', claimed_by='admiral', worktree='/anywhere'):
  SUCCEEDED
  previous_session_id: repair-reviewer-613-20260820
  takeover_reason:     "stale lease reclaimed"     (written automatically)
```

A **plain `claim`** — no `--force`, no reason supplied, an unrelated session id,
and a `worktree` of literally `/anywhere` — took the stranded plan. The engine
reads no location at all (`origin_worktree_refusal` retired in #609 g2:
"THE ENGINE NOW READS NO LOCATION AT ALL, ambient or derived"), so this works
from anywhere on the machine.

**So the defect is not scarcity of authority. It is the absence of any.** The
stranded plan was never protected; it merely *looked* `active` to a human
reader. What actually stopped the Admiral from reclaiming it was the Admiral's
own ruling that crew lanes run unrailed — **doctrine, not mechanism.** Lane A
identified this from source; the run above measures it.

**This makes B's count much more serious.** 58 plans in this checkout hold a
live `active` lease and 54 sit archived with dead owners. Every one of those is
freely claimable, right now, by any session id, from any directory, with the
weakest verb in the engine — while presenting to a reader as owned and busy.
That is #615 ("a spine with no active lease has no ownership guard at all")
demonstrated one step further: a spine with an *apparently* active lease has no
guard either, once the heartbeat ages past 1800 seconds.

**Design obligation, restated.** The question is not "who may reclaim a dead
child's plan." Anyone may. The questions are: *what should a stale lease
present as to a reader*, and *should reclaiming one be as cheap as the weakest
verb?* A candidate that adds parent-reclaim capability without addressing the
free-for-all underneath has added a lock to a door that has no frame.

**A further finding from Lane A, verified.** `require_session`'s live refusal
text tells the caller to *"pass `--session-id <the holder's>` or take over with
`claim --force --reason ..."* — `scripts/checklist_engine.py:1148-1152`. Both
remedies it recommends are filed defects: passing the holder's id is #632's
inheritance hazard, and `claim --force` is #369's attribution erasure. The
engine's own error message routes users into two known bugs.

---

# THREAT MODEL AND SUCCESS CRITERION — human ruling, 2026-08-21

**Every "design obligation" above is written in an adversarial frame. That frame
is wrong and the human has corrected it.**

- **There are no bad actors.** Nothing here is protecting against malice, theft,
  or impersonation. The only adversary is an honest agent about to make a
  mistake.
- **Ease of use for agents is the success criterion.** If a design makes the
  tools harder to use, it failed — no matter how much it "closes."
- **Added machinery is a COST, not a feature.** A new module, a new verb set, a
  new permission concept, a new file to keep in sync: each is a debit that the
  design must earn back in mistakes prevented.

## What this changes

The question is never "who is ALLOWED to act." Anyone may act; we assume good
faith. The questions are:

1. **Does the system tell the truth?** A dead plan that presents as `active` is
   the defect. Not the absence of a lock.
2. **Is the easy path the correct path?** If avoiding a mistake takes five
   manual steps, agents will get it wrong, and that is the system's fault.
3. **Do refusals teach?** A refusal that names a remedy which is itself a filed
   defect (`require_session`, see Correction 2) actively causes the next error.
4. **Is failing closed cheap?** Defaults that are safe without ceremony beat
   permissions that must be requested.

## Re-reading the evidence under the corrected frame

- **E3 / the 58 stale leases.** The reclaim mechanism already works and already
  records attribution. Nothing needs to be added. What needs to change is that a
  stale lease must *present as stale* to whoever reads it. This is a display and
  labeling fix, not an authority fix.
- **E5's five-step handshake.** A pure usability defect. One verb, no new
  concepts.
- **E2 / #632.** Not "a crew could corrupt the parent." An agent drives the
  wrong spine by accident because the ambient default is wrong. Fail closed on a
  mismatch, with a message saying what to do instead.
- **`require_session`'s refusal text.** The cheapest high-value fix identified
  anywhere in this epic. It is a string edit.
- **E1.** Channel-specific (see Correction 1). The usability question is why two
  dispatch channels behave so differently and whether the in-harness one can
  simply work, not who is permitted to rail whom.

**A design that only changes messages, defaults, and what the system displays is
a legitimate winner.** It must be on the ballot, and it must be scored fairly
rather than treated as the do-nothing option.
