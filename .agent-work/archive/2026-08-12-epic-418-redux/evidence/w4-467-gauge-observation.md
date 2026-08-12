# Wave-4 gauge observation — the #467 Commander is itself in the trip band

**2026-08-08T09:49:48Z · `claude-opus-5` · `fill_fraction = 0.194023` (19.4%)**

Read from the Commander's own `gauge.json` at
`epic418-a2-467/.agent-work/issue-467-trip-semantics/gauge.json`.

## Why this reading is worth keeping

**The crew commanded to fix trip semantics is sitting in the HARD trip band while doing so**, and it
has not written a line of implementation code yet. At the moment of reading it had completed
`init`, `context` and `understand`, and produced a design-it-twice brief with three candidates.
`plan` was still open; the branch had **zero commits**.

That makes it a **positive control for #467's own premise**, taken from a crew that had no idea it
was being measured for this.

## RETRACTED: the Admiral-side comparison — the #467 Commander refuted it, and it was right

**This section originally read the Admiral's "44% untripped" as proof the band is role-blind. That
inference does not hold and is withdrawn.** The refutation came from the #467 Commander at its plan
boundary, citing `docs/GAUGE_WRITER_HOOK.md` §residuals: **an orchestrator holding several spines
under one binding key writes no reading at all.** An Admiral holding an epic spine plus crew spines
is exactly that shape (**#452**).

So `no trip at 44%` and `no gauge at 44%` are **indistinguishable without an asserted live reading**
— which is #467's own *"no absence is evidence"* rule, turned on the Admiral who wrote it into the
launch order. The engine's own projection said as much to my face and I read past it:

> `CONTEXT GAUGE SILENT: the last recorded reading at this path was 46% full ... sampled 1h31m ago
> — too old (or otherwise rejected) to trust as a live reading.`

**Fifth instance of this family in one day, and the first one a subordinate caught rather than me.**
That the crew commanded to fix "no absence is evidence" applied it to its own Admiral's evidence is
the mechanism working exactly as intended.

## What survives

| Role | Fill | Status |
|---|---|---|
| Wave-3 crews | 17-21% | tripped, repeatedly |
| **#467 Commander (this reading)** | **19.4%, pre-implementation** | **asserted live reading, in band** |
| ~~Admiral~~ | ~~44%~~ | **withdrawn — cannot distinguish untripped from unmeasured** |

The Commander's own **19.4% is an asserted, live, single-binding reading**, so it stands on its own
without the comparison. **That reading alone is what may carry DC4's "overrides only where a gate
has bitten"** — a crew in the band, pre-implementation, on the issue about the band. The Admiral
comparison was never needed for it and is not used.

## What this reading does NOT say

- It does **not** say the band is too low. Every trip this epic has seen cost a relaunch at a seam
  and lost no work — the cost of a trip is bookkeeping, not progress.
- It does **not** license retuning the global default. That is a production default affecting every
  agent, Tommy has it marked `surfaced`, and the wave-4 launch order forbids the Commander touching
  it.
- **Population is still one laptop.** The gauge writer is wired only in untracked
  `settings.local.json` (**#458**); tracked `settings.json` wires it on nothing.

## Provenance note

This reading exists **because #488 shipped in wave 3**. The Admiral's own gauge was dark for roughly
nine hours of this epic — two bindings resolving to one path read as ambiguous and the writer
skipped. A wave-3 fix is what makes a wave-4 measurement possible, which is the improvement loop
working within a single run.

---

## Second reading, same crew: 28.0% and still no trip — and *why* is the finding

**2026-08-08T10:06:53Z · `fill_fraction = 0.280` (28.0%)** — up from 19.4% at 09:49:48Z, roughly
**+0.5 percentage points per minute**. Spine still `plan=pending`; **zero commits on the branch**.

28% is **well over** HARD (`_PROFILES` sets it at 150k of a 1M Opus window = 15%, and wave-2 crews
were observed tripping at 17-21%). So why no trip?

**Because the trip is evaluated on a gated verb, and this crew has not attempted one since crossing
the line.** The current design refuses `advance` *pre-advance*; an agent working a long stretch
inside a single gate sails past the threshold unnoticed and only discovers it at the boundary. This
crew has been inside `plan` — writing a design-it-twice panel, running a cold critic panel, triaging
19 findings — the whole time.

**Three things follow, and none of them are speculation.**

1. **It corroborates the retraction above rather than reviving it.** *"The Admiral ran to 44% with
   no trip"* was doubly unsound: not only is the reading unasserted (§retraction), but **no trip is
   evaluated while no gated verb is attempted.** An orchestrator between gates and an orchestrator
   with headroom look identical, for a second independent reason.
2. **It is mild support for the shipped design.** If a trip can only land at a gate boundary, it
   lands exactly where a handoff is cheapest to write — the seam. Every trip this epic observed cost
   a relaunch at a seam and lost no work, and this is the mechanical reason why, not a coincidence.
3. **It sharpens what DC5's round trip must actually exercise.** The interesting case is not an
   agent that trips politely at a boundary. It is one that crosses the line **deep inside a gate**,
   accumulates uncommitted work, and only then meets the refusal. That is this crew, right now, at
   28% with zero commits.

**Prediction on the record, before the fact:** this Commander trips on its next `advance`, not
before. Recorded now so the outcome cannot be read back favourably either way.

---

## The claim I retracted, now re-derived properly — and it says something different

The retraction above stands: *"the Admiral ran to 44% with no trip"* was unsound, because no
reading was asserted. **I now have the asserted reading it lacked.**

```json
{"schema_version": 1, "fill_fraction": 0.26286, "model": "claude-opus-5",
 "observed_at": "2026-08-08T10:11:26.677Z"}
```

`.agent-work/epic-418-redux/gauge.json` present, **no `gauge-skip.json`** — a single live binding,
measured, not absent. Two asserted readings on the same machine, model and hour:

| Role | Asserted fill | Over hard (0.15)? | Tripped? |
|---|---|---|---|
| **#467 Commander** | 0.2758 | yes | **yes — at the `plan` boundary** |
| **Admiral (this run)** | 0.2629 | yes | **no** |

**Both are over the line by a similar margin. Only one was ever asked.**

### So the original conclusion was wrong, and the corrected one is more useful

It is **not** that the band is role-blind. Both roles cross the same threshold at nearly the same
fill. It is that **the evaluation points are role-asymmetric**:

- A **Commander** crosses ten gates in a run — `init`, `context`, `understand`, `plan`, `execute`,
  `reconcile`, `triage`, `review`, `feedback`, `archive`. It meets the question repeatedly.
- An **Admiral** sits inside **`execute` for the entire epic** — one gate, many hours, many waves.
  It can run arbitrarily far past the limit and **never be asked once**.

The trip is evaluated on a gated verb. An orchestrator barely attempts them. So the governor's
question reaches the role that is *already* handing off at seams, and skips the role that holds the
most irreplaceable context in the fleet.

### Why this matters to #467 specifically

The shipped design refuses the verbs that **begin** work (`start`, `reopen`). That is the right
shape, and it **inherits this property unchanged**: an Admiral deep inside `execute` begins nothing,
so it is still never asked. **DC1 is satisfied for crews and structurally silent for
orchestrators.**

This is not a defect in the fix and not a reason to widen #467. It is the **honest boundary of what
the fix covers**, and it belongs in the return's per-done-condition accounting rather than being
discovered later by someone who assumed DC1 was universal.

### Provenance

Both readings exist only because **#488 shipped in wave 3**. My gauge was dark for roughly nine
hours of this epic — two bindings resolving to one path read as ambiguous and the writer skipped —
and the comparison that finally corrected my own retracted claim is only possible on the fixed
writer. A wave-3 fix producing the wave-4 measurement that refutes the wave-4 Admiral.
