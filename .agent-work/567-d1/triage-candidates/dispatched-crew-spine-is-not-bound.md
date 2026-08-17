# Triage candidate — the crew skills state a norm that is the exception for this dispatch shape

**Found at:** `g1`, `g1b`, lane D1, epic #567 wave 2. Reported **independently by four crews across
two gates** — the g1 implementer, the g1 reviewer, and the g1b implementer, each unprompted.

**What was found.** The implementer and reviewer skills open by telling a dispatched crew that its
spine is already bound before it starts (`SPINE_FILE`/`SPINE_SESSION` in its environment) and that
`spine_status` is therefore its first call, not plan-building.

For a handoff-driven `run_crew.py` dispatch that is false. `run_crew.py` binds the spine pair **only
when `--spine` is given**; a handoff-driven crew is registered with `"spine": null` and its
environment carries only `SPINE_PARENT`. Every crew this lane dispatched took the skill's *other*
branch: authored its own `IMPLEMENTER_PLAN.json` / survey under `CREW_SCRATCH_DIR`, claimed the
lease as its first command, and drove it through the engine.

**Why it is worth recording.** Four independent reports of the same misfit is a stronger signal than
any one of them: for this dispatch shape the skill's stated norm is the exception, and the skill
says the opposite. A crew that believes the opening sentence spends its first minutes looking for a
spine that was never bound.

Two fixes were proposed by the crews themselves, and they are different in kind:
1. **Cheap** — reword the skills so the `spine: null` branch is stated as a first-class case, and add
   a **Plan File Location** field to the implementer handoff template (the `CREW_SCRATCH_DIR`
   convention was discovered by one crew reading a sibling's result artifact, not from any document).
2. **Deeper** — have `run_crew.py` bind a handoff-driven crew's own plan into `SPINE_FILE`, which
   would make the opening sentence true instead of needing a caveat.

**Why it is a candidate and not a fix.** `scripts/run_crew.py` is **lane F's** this wave. The skill
wording is in this lane's files, but changing a role's opening doctrine on the strength of one
lane's observation is a doctrine call, and `decision:no-doctrine-promotion` reserves that for the
human. Recorded, as that ruling requires.

**Disposition:** `recommend-and-defer`. Pair onto an open issue at epic closeout, or record as an
episode. **Not filed as an issue** — `decision:no-issue-filing-mid-run`.

---

## Escalation, `g1b-review` round 2 — the misfit is not just wrong prose, it actively pushes a crew to impersonate its dispatcher

The g1b re-reviewer finished its work, wrote its result, consolidated and released its own survey —
and was then **refused permission to end its turn by the Stop hook**, which told it to drive a spine
it does not own.

The mechanism: the hook resolves a spine from disk when `SPINE_FILE` is unset. For a handoff-driven
crew, what it finds is **the dispatcher's** spine — here
`constellation/567-d1/lane-d1/commander-delegated`, whose lease was active and whose in-progress
step was `g1b-review`, i.e. **the crew's own dispatch**. Complying would have meant passing the
Commander's session id on mutating verbs against the parent's spine, closing the gate that is its own
dispatch, and dispatching the reviewer of its own review.

It refused, in its own words: *"That's impersonation, not delegation."* **The refusal was correct**
and this lane endorses it.

Worse, the hook's sanctioned escapes do not fit. `spine_halt block` and a human-authority `waive`
both **write to the parent's spine**, so the prescribed "honest stop" is itself the destructive act —
and `block` is the exit for a gate of one's own, which a crew with a consolidated, released survey
does not have.

**This is the sixth independent reproduction in this lane, across three gates and both roles.** It is
the same root cause as above, one consequence deeper: the lane-H precedent the launch order warned
about — *"a cold subject read its dispatcher's session id off disk and drive the live run under it"* —
is not an accident of one agent, it is what the hook instructs.

**Both fixes named by the crews:**
- **Cheap and exactly detectable:** skip the hook when `SPINE_FILE` is unset **and** `SPINE_PARENT` is
  set. That is precisely the handoff-driven-crew signature.
- **Durable:** have `run_crew.py` bind the crew's own plan/survey into `SPINE_FILE`, which makes the
  skills' opening sentence true instead of needing a caveat, and removes the disk-resolution path
  entirely.

Hook code and `scripts/run_crew.py` are both outside this lane's ownership, so this stays a
candidate. **It should be paired onto an open issue with priority** — it is a live impersonation
hazard, not a documentation nit.
