# Problem statement — #467 (A2: trip semantics)

Reconciled against LAUNCH_ORDER `LO-467.md` (frozen), issue #467, and the code as it
actually stands at `d376b786`. Delegated mode with a **reachable** Admiral: gaps float
rather than being guessed.

## The ask, in one sentence

The governor's HARD band expresses itself as a **refusal of `advance`**, and `advance` is
the only writer of the `why_trail` whose latest live record is the `DIGEST` a cold
successor reads — so the event that forces a handoff is the same event that prevents the
handoff's brief from being written (#431). Convert the trip from a refusal into a **change
of instruction**, so the agent still advances, the DIGEST still lands, and #431 dissolves.

## Baseline reconciliation — what the code actually does today

Read at `d376b786`. This is the "reconcile the order's assumed baseline against the actual
code" step, and it changes the shape of the RED.

1. `dispatch()` (`scripts/checklist_engine.py:2679`) calls `_trip_hard_gate` **before**
   `advance` runs, so a HARD refusal never mutates state.
2. `_trip_hard_gate` (`:1439`) refuses **unless** a non-superseded `refresh-request`
   evidence item targets the gate **and** carries `why_ref == _latest_why_record(cl).id`.
3. `advance` (`:1854`) appends the why-record at `:1899-1903` — **after** postconditions
   are proven at `:1885`. `_append_why` (`:1095`) is the **only** writer of `why_trail`
   (`_append_reopen_marker` writes a marker, never an understanding).
4. `_digest` (`:1139`) → `_latest_why_record` (`:1121`) → the `DIGEST:` line on `current`
   (`_why_suffix`, `:1179`). That line plus `ACTIVE <gate> — <imperative>` is the entire
   cold-start surface (`global-everyone.md` §reach-up).

**So the deadlock is not "advance is unreachable".** Mechanically an agent *could* attach a
refresh-request and then advance. The deadlock is that **the composite of the refusal and
the doctrine it enforces** leaves the trail unwritten:

- the refusal's own text says advancing "is blocked", which reads as *stop*, not as
  *attach-then-advance*; and
- `global-everyone.md` §reach-up instructs the tripped agent to write the refresh-request
  **"...then go idle"** — it never says advance.

Both halves point the agent away from the one verb that records what it learned. The
successor therefore cold-starts on the **previous** gate's understanding. That is #431's
observed symptom verbatim: *"a fresh agent ... read 'nothing about the epic's substance is
settled yet' — even though the latitude contract had, in fact, just been confirmed."*

**Consequence for the RED (LO pre-ruling 3).** The RED cannot be "advance raises". It must
be the *end-to-end* property: at a HARD gate, a tripped agent that follows the shipped
instruction leaves `_digest(cl)` naming the pre-trip understanding, so the successor's
cold-start brief is stale. That is the thing that must go green.

## What is Fixed and not renegotiable (#467 `Fixed`)

- A missing or failed reading never forces a handoff. `_read_gauge` collapses every failure
  to `None` and both bands no-op on `None` (`:1411`, `:1448`). This survives.
- HARD means "wrap up", never "you are unsafe".
- The reading is **pushed** by the engine on tool use, never fetched by the agent.

## The six done-conditions, as I read them against the code

| DC | Restated mechanically |
|---|---|
| DC1 | At/over HARD the engine **changes the imperative** the agent is given rather than refusing the verb it needs. |
| DC2 | The engine distinguishes an advance that **carries a handoff** from one that **starts new work**, and refuses only the second. Two-way test required. |
| DC3 | The why-record lands on the handoff-carrying advance, so `DIGEST` is fresh at the seam. #431 verified dissolved (not closed — closing is the Admiral's). |
| DC4 | Per-gate threshold override exists **and is exercised once**: one gate carries an override that changes its behaviour and not its neighbours'. Global default unchanged (floating any change). |
| DC5 | Round trip completes once: trip → handoff → refresh → resume, resumed work verified against what the tripped agent was mid-way through. |
| DC6 | Non-compliance is **mechanically** observable: the engine can see whether a handoff artifact appeared before the next advance at an over-threshold gate. |

## Open — Commander's call (mine, per #467 and the LO)

- How the two advances are distinguished: flag / separate verb / inferred from a handoff
  artifact's presence.
- Where the default threshold sits (`_PROFILES`: 1M-window models 80K soft / 150K hard →
  0.08 / 0.15).
- Whether the threshold is a fill fraction or absolute headroom.

## Floats identified at understand (none blocking yet)

1. **The 44%-no-trip observation may be a silent gauge, not headroom.** LO field-evidence
   item 2 reads the Admiral's 44%-without-trip as role-blindness. But
   `docs/GAUGE_WRITER_HOOK.md` §residuals records that an orchestrator holding several
   spines under one key writes **no reading at all** — and an Admiral holding an epic spine
   plus crew spines is exactly that shape. By #467's own "no absence is evidence" rule I
   cannot treat "no trip at 44%" as evidence of headroom until a reading is asserted to have
   existed. I will state this rather than act on it, and I will not retune the global
   default (LO fence).
2. **The governor does not ship** (#458): tracked `.claude/settings.json` wires the gauge
   writer on nothing, so every governor observation is one laptop's local config. My
   acceptance therefore plants gauge readings deliberately rather than depending on live
   hook wiring, and my evidence will say so.

## Out of scope

Retuning the global default threshold; anything touching tracked `.claude/settings.json`;
filing issues; closing #431; the identity-durability constraint #467 records for #441/#452.
