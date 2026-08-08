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

## Against the Admiral-side reading

Same machine, same `PostToolUse` hook, same model tier (`claude-opus-5`), same morning:

| Role | Fill | Tripped? |
|---|---|---|
| Wave-3 crews | 17-21% | yes, repeatedly |
| **#467 Commander (this reading)** | **19.4%, pre-implementation** | in band |
| Admiral (this run) | **44%** | no |

**The band does not appear to be role-blind by accident — it is measured against a window the roles
do not share.** A Commander loads an issue spec, a launch order, a codebase region and a design
space; an Admiral holds a log and a ledger. The same fraction means different things to them, and
the current default is global-per-model (`_PROFILES`, HARD at 150k of a 1M Opus window).

**This is exactly what #467's DC4 exists to license** — *"the override mechanism existing and
exercised at least once ... overrides only where a gate has bitten."* This gate has bitten, on
camera, in the crew fixing it.

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
