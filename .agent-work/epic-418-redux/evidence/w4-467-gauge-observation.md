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
