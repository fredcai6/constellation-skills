# Design-it-twice convergence — #467 A2

**Panel of 3, not a single.** Rationale surfaced to the Admiral at plan approval: #467 states
that workstream F (#424) *"cannot ship a signature for `advance` until this settles"*, so the
shape chosen here is consumed by another workstream. Briefs and full candidates:
`.agent-work/issue-467-trip-semantics/DIT_BRIEF.md`, `dit/CANDIDATE_{A,B,C}.md`.

Convergence is normally the human's. Here it is **mine by explicit grant**: #467 lists "how
the two advances are distinguished" under **Open (Commander's call)**, and LO-467 §Inherited
latitude repeats it. Recorded rather than assumed.

## The three candidates, in one line each

| | Constraint | Mechanism | Its own named cost |
|---|---|---|---|
| **A** | zero new CLI surface | the engine **decrees**: the first advance at/over HARD *is* the handoff (forces a real `--why`, suspends `why_exempt`, files the refresh-request itself); every later advance still over HARD is refused | the engine never hears intent, so an agent two minutes from done is forced to write a handoff for a successor who will never exist, then refused at its last gate |
| **B** | intent stated, never inferred | `advance <gate> --handoff` declares "close and stop"; plain `advance` is refused at/over HARD; a `handoff_pledges` record resolves `kept`/`broken` by comparing session ids | the flag is a toll that is cheap to type; the pledge catches a false declaration one gate late, as audit rather than as a gate |
| **C** | move the refusal, add no machinery | HARD stops refusing `advance` entirely and refuses `start`/`resume` instead — closing the gate you are in is always allowed and *is* the handoff | C forbids new work but cannot **force** a handoff: an agent that trips and simply stops is caught by a render, not a refusal |

## Ruling: **C is the base, with one plug from A and the override all three converged on.**

### Why C wins the base

1. **C found the fact the other two designed around.** `advance --why` **already is** the
   handoff artifact: a non-exempt gate fails closed on a silent advance, and that `--why`
   *is* the DIGEST. Nothing needs building — the governor is simply refusing the one verb
   that writes it. A and B both add machinery to reconstruct a thing that already exists.

2. **C's DC2 mapping is literal, not figurative.** "Refuses only the one that starts new
   work" — under C the refused verb is `start`, which *is* the verb that starts work. A and
   B both refuse an `advance` and reinterpret "starts new work" as "an advance that will be
   followed by new work."

3. **C costs #424 nothing.** No verb, no flag, no evidence type, no payload field. F can ship
   its typed `advance` today; only `start`'s failure modes change, and F wraps refusals as
   errors, not as parameters. Given #467 names F as blocked on this, "no signature at all" is
   the strongest available answer, and B's own case for paying the signature cost does not
   outweigh it.

4. **C un-shadows #431's actually-observed case.** Today `_trip_hard_gate` fires *before*
   `advance` runs, so an agent whose gate has unmet postconditions is told "advance is
   blocked, request a refresh" and never learns its real problem. With the guard off
   `advance`, the same call reaches the postcondition check and refuses with the true
   statement about the world. **You may not buy past unfinished work with a handoff** —
   already settled engine doctrine (postconditions are proven before the why is solicited),
   and C keeps it by construction.

### Why A's plug is taken

C's own §6 is the honest hole: **C forbids new work but cannot force a handoff.** The agent
that trips and stops without advancing leaves the stale DIGEST — which is #431's symptom
recurring — and C answers it with a render. A render is an instruction, and instructions are
what DC6 says we can no longer rely on.

A's contribution is the shape of the answer: **an engine-only record the agent cannot
author.** So g4 ships a **trip ledger** — one engine-written, append-only entry every time the
HARD band is evaluated and found tripped, recording the gate, the verb, the fill, the
resolved threshold, the live why-record id, and what the engine did about it. That gives two
mechanical signals rather than one:

- the **refusal at `start`/`resume`** — self-enforcing and self-recording, covering "handed
  off, then kept working";
- the **ledger plus a pure compliance predicate** — covering "was told, and closed nothing",
  the case that has no refusal to lean on.

The ledger earns its keep a second time, and this is the part neither A nor B argued:
**without it, "the governor never tripped" and "the governor never ran" are the same
observation.** That is precisely the failure #467's own evidence protocol forbids, and this
epic has already been bitten by it (the gauge writer was silent on the orchestrator tier for
about nine hours while every downstream measure read the absence as a quiet pass). The ledger
turns "no absence is evidence" from a discipline an agent must remember into a fact the
engine records.

### What is NOT taken

- **A's decree** that the first over-HARD advance *is* the handoff, with `why_exempt`
  suspended and `--mechanical` refused. It forces a handoff on a run that was about to finish
  cleanly, and A names this itself. Under C the agent closes its gate the way it always
  would; only *starting the next one* is blocked.
- **A's byte-identical-to-digest refusal.** A genuine idea, but it puts a refusal back on the
  `advance` path, which is exactly what C removes. Raised as a triage candidate instead.
- **B's `--handoff` flag.** Its own §6 concedes the flag is a toll bought with a string, and
  it charges #424 a permanent signature for a distinction C gets from a verb that already
  exists.
- **B's `handoff_pledges` session-identity comparison.** Elegant, but it rests on the
  identity key that #467's own "Recorded constraint" says is **not durable across a session
  drop** — a restarted session returns under a new identity, which would read as `kept` when
  nothing was handed off. Fold the useful half (the engine records who acted) into the ledger
  without making the verdict depend on identity durability.

### Where all three agreed — taken as converged

**DC4: the override is `context_headroom_tokens`, absolute tokens, tighten-only,** resolved
gate → checklist config → model default, with the arithmetic in `gauge_reader` (the module
that owns the window and the caps). Three candidates authored under three different
constraints reached the same answer from the same evidence: `_PROFILES` is already
intent-first absolute because context-rot degradation tracks absolute token count rather than
window fraction, so a fractional override would reserve five times more room on a 1M model
than a 200K one from the same authored number. Tighten-only is what keeps the Commander from
raising a production default it was fenced away from.

**Ruling on #467's third open question — fraction or absolute headroom: absolute headroom.**

### One thing this hybrid still cannot do — stated, not papered over

Neither C's refusal nor the ledger can judge handoff **quality**. The engine can prove a
non-empty understanding was written at the seam; it cannot prove it was a good one. That is
consistent with the shipped v1 rule that reason quality is not policed, and no candidate
proposed a way past it. It goes to triage as a named limit, not a gap I closed.

## Untaken roads (surfaced, not silent)

- **A single critic instead of a panel** for the plan review — not taken; this plan changes
  the engine's core policy and unblocks another workstream.
- **Decomposing #467 into sub-issues** — not taken, per LO-467 pre-ruling 1 and Tommy's
  stated preference twice over.
- **A mid-gate handoff channel** for the gate that trips with unmet postconditions — deferred
  to triage. C's answer (`block --next`, whose text `current` does not render) is real but
  weaker than a gate-closing handoff.
