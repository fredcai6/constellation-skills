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
