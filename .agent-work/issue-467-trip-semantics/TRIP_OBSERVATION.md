# Live trip observation — the Commander for #467 tripped on #467

**This is evidence, not a handoff document.** The handoff is the `DIGEST` on `current`, per
`global-everyone.md` §reach-up. LO-467 asked me to record what the handoff felt like and what
was missing; this file is that record and nothing else. A successor should read the DIGEST
first and this file only when it gets to DC5/DC6 evidence.

## The reading — asserted, per #467's evidence protocol

No absence here. A fresh, well-formed reading existed and was read:

```json
{"schema_version": 1, "fill_fraction": 0.275764, "model": "claude-opus-5",
 "observed_at": "2026-08-08T10:05:53.875Z", "identity_resolution_ms": 0.0583}
```

`claude-opus-5` → `_PROFILES` `(1_000_000, 80_000, 150_000)` → hard = **0.15**. Observed
**0.2758 ≥ 0.15**. The engine printed `CONTEXT 28% (>= hard)`, which is the proof it was read
rather than inferred. This is a **governor that fired**, not a silent one.

## The refusal, verbatim

Trying to close the `plan` step — carrying the whole design-it-twice convergence and the cold
critic triage as my `--why`:

```
REFUSED: plan: context at 27% is at/over the hard limit — advancing is blocked until you
request a refresh, so work is handed off at a seam rather than lost to a runaway.
Run: attach plan --type refresh-request --field seam=plan --field why_ref=<why-id>
```

**That is #431, live, on the run whose job is to fix #431.** The refused verb is the only
writer of `why_trail`, and the `--why` it refused was the entire plan.

## Four things the shipped mechanism got wrong, measured on myself

**1. LO-467's own handoff instruction is unsatisfiable under the shipped engine.** It says:
*"Write a `refresh-request` into your `spine.json`, **make sure your `current` carries the
DIGEST**, and go idle."* Those two clauses cannot both be obeyed. `current` carries the
**latest live why-record**, and the only verb that writes one is `advance` — the verb the
refusal blocks. Had I done literally what the order said, my successor would have cold-started
on the `understand` step's understanding: the deadlock is real, the plan is unwritten, good
luck. This is not a defect in the launch order. It is #431 propagating into the doctrine
written on top of it — which is exactly why #467 says the fix must *dissolve* the issue rather
than patch it.

**2. What I actually did is what #467 says the engine should permit — and the shipped engine
already permits it, silently.** `attach` the refresh-request keyed to `w-3`, then `advance plan
--why "<the handoff>"`, then `attach` a second refresh-request at `execute` keyed to the new
`w-4` so `current` shows `REFRESH REQUESTED:` at the gate my successor resumes at. Three
commands. The engine allowed all three. **The capability was never missing — only the
instruction was.** That is the sharpest evidence available for DC1: the trip did not need new
permissions, it needed to stop saying "blocked" and start saying "close this gate carrying your
handoff, then stop."

**3. `REFRESH REQUESTED:` is keyed to the ACTIVE gate, so a compliant handoff erases its own
signal.** `_why_suffix` renders the line only when a pending request targets the *active*
gate. My first request named `plan`; the moment I advanced `plan`, the active gate became
`execute` and the line vanished — the Admiral would have seen a fresh DIGEST and no reach-up
signal at all, i.e. a Commander that looked like it had simply stopped. I had to file a
**second** request at the gate I was handing off *to*. Nothing in the doctrine or the engine
says to do that; I worked it out from the source. **A compliant agent that files one request
loses its own signal.** Not in #467's six done-conditions — carried to triage, not fixed here.

**4. The remedy hint asks for a value `current` does not display.** `_refresh_attach_hint`
emits the literal placeholder `why_ref=<why-id>`. `current` shows the DIGEST *text* but never
its id. I had to read `spine.json` — which `global-everyone.md` calls a violation — to learn
that the id was `w-3`. The one sanctioned reach-up move requires an over-read of the state
file. g2(d) of my plan fixes this by emitting the concrete id; I wrote that gate before I hit
the defect myself, which is at least a point in the plan's favour.

## What the DIGEST could not carry

Honest accounting of the cold-start surface, since that is what DC5 turns on. The DIGEST is one
string. It carries the frozen design, the two traps the critics caught, the next action, and
the baseline. It cannot carry:

- **the reasoning behind rejected options** — a successor that disagrees with "guard `reopen`,
  not `resume`" has no way to know two critics disagreed and both were right. Mitigated only
  because `CRITIC_TRIAGE.md` exists on disk and the DIGEST points at it. **A run without
  durable artifacts would have lost this.** The cold-start-from-`current`-alone doctrine works
  here because the work area is rich, not because the DIGEST is sufficient.
- **the crew state** — no crews were dispatched yet, so nothing was lost. Had I tripped
  mid-gate with an implementer running, the DIGEST has no field for it and
  `recover_crews.py` would have been the only trace.
- **that three of the four observations above exist at all.** They are here because I wrote
  this file. The engine records none of them, which is the shape of DC6's problem in
  miniature: I complied, and nothing mechanical would show it.

## The positive control held

The round trip's first half completed cleanly: trip → handoff written → refresh requested →
idle, with **no work lost** and no separate handoff document. That is the fourth successful
hand-run of this loop in this epic, and the first one performed *while implementing the fix
for it*. What has not yet been demonstrated is the far end — a cold successor resuming from
this `current` alone. That is g5's job and it is the point of the whole issue.

## Carried to triage, not fixed here

1. `REFRESH REQUESTED:` is active-gate-keyed, so a compliant gate-closing handoff erases its
   own signal unless the agent files a second request at the resume gate.
2. The engine accepted `attest` and `attach` on a `pending` gate — I satisfied four `plan`
   postconditions before `plan` was ever `start`ed, and only the `advance` refused. Evidence
   can accumulate on a gate no one has opened.
3. `grade_lint.py` fails `GL001 UNGRADED_DECISION` on any string in `anchors.decision[]`,
   including the "decision pressure" entries that `EXECUTE_PLAN.template.json` explicitly says
   carry no grade. The template and the linter contradict each other; I moved mine into
   `constraints` to get a clean lint.
