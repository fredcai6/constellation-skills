# x1 Designer A — Minimal-interface / response-text only

**Constraint:** the engine's existing stdout/stderr is the ONLY channel. No hooks, no new verbs, no
state-schema change, no conductor. The smallest diff to `checklist_engine.py` output strings that
carries the doctrine at the moment the agent is deciding.

**One-line thesis:** the engine is *already* the mandatory chokepoint for every state transition, so
its response text is the cheapest possible rail — but a rail is a **deterrent, not a fence**, and it
has **zero reach at the two decision points where no engine call happens** (turn-end, post-compaction
push). I carry everything I honestly can and mark the two nulls rather than stretch the channel.

---

## 0. The austerity decision that shapes everything: there is no per-gate "why"

Field-checked the gate schema (`.agent-work/archive/2026-07-09-issue-99/spine.json`). A gate carries
`title`, `imperative`, `preconditions/postconditions[].statement`, `status`, and list-position in
`items`. **There is no `why` / `rationale` field.** Issue #134's human direction ("engine responses
should carry the next step's imperative AND why it matters") therefore forks:

- **Rejected (out of channel):** add a per-gate `why` field to the spine template. That is a schema
  change, and worse it *relocates* the nine-copies-of-wording problem into nine spine templates
  instead of eliminating it — exactly the failure the shared brief names (§ground-truth: "without nine
  hand-maintained copies").
- **Chosen (in channel):** the **imperative** is already gate-specific and already in state — I surface
  it verbatim plus the *next* gate's imperative (also already in state). The **"why it matters"** is
  **not** gate-specific prose; it is a **fixed doctrinal rail keyed to decision-point TYPE**
  (early / mid / near-terminal / check-failure / terminal-release), baked into the engine as strings.

This is the sharp edge of the minimal constraint: *"why it matters" is the same four sentences for
every gate, because the thing that actually fails a cheap model is never "I didn't understand why gate
7 matters" — it is "I forgot I'm in a workflow at all / I think done-ish is done."* The universal rail
answers that; per-gate rationale would be cost without the matching failure.

---

## 1. The contract at each decision point (concrete payloads)

All rail text comes from **one** engine function, `_rail(point, cl)`, and is appended to existing
messages. Gate-specific tokens (`{imperative}`, `{next_imperative}`, `{n} of {N}`, `{terminal_id}`)
are **derived from existing state** — `items` order gives position and distance; the next item's
`imperative` gives the lookahead. Zero new fields.

### 1a. Step entry — `current` (today: `ACTIVE plan [in-progress] — {imperative}`)

```
LEASE active: commander-issue-99 (by commander, heartbeat 2026-07-12T18:04Z)
ACTIVE plan [in-progress] · gate 4 of 10 · 6 to terminal (archive)
  DO NOW: {full imperative text, verbatim from state}
  THEN: start execute — {first sentence of execute.imperative}
RAIL: You are in the MIDDLE of the run. The workflow IS the deliverable, not a
  detour before it. Every gate goes through the engine; a hand-written result or
  an early "done" is theater the journal exposes. Do not end your turn to wait —
  poll in-turn.
```

### 1b. Step exit — `advance` (today: `plan -> complete`)

```
plan -> complete · gate 4 of 10 done · 6 to terminal
NEXT: `<engine> start execute` then `current`. You are past no gate for free —
  stopping here is quit-early, the most-observed failure shade. Keep going.
```

### 1c. Near-terminal — emitted by `advance`/`current` when `distance_to_terminal <= 1`

```
feedback -> complete · gate 9 of 10 done · 1 to terminal: archive
TERMINAL AHEAD — ORDERING MATTERS: archive is the LAST gate. Do the final
  `advance archive` FIRST, THEN `release` the lease. Release is the last
  journaled action; releasing before the final advance is completion-theater
  and fails the eval's lease-window-vs-journal cross-check.
```

### 1d. Check-FAILURE — `advance`/`start` refusal (today: `REFUSED: plan: postconditions unmet ['c2']`, stderr)

```
REFUSED: plan: postconditions unmet ['c2'] — "plan critic attested".
  This is a real gate, not a formality. Do the missing work and attest/attach the
  evidence; OR if you are genuinely blocked, `block` this gate with a reason (or
  `waive` on cited authority) — a stuck agent stops HONESTLY, it never fabricates
  evidence, invents a session, or hand-edits state. Scoped-null rule: report
  "this check failed", never "this step is impossible" — then try another variant.
```

This is the single most valuable string in the design: it lands the scoped-null + ask-up interceptor
at the exact instant of failure, and it names the escape hatch (`block`/`waive`), satisfying the hard
constraint that every refusal have an honest exit.

### 1e. Terminal — `current` when no open items (today: `DONE: no open items.`)

```
DONE: no open items. All 10 gates complete.
FINAL ORDERING: if you have not already `release`d the lease, do it NOW — it is
  the last journaled action and the record of an honest finish. Do NOT re-announce
  "released" without having run the verb; the journal, not your prose, is the proof.
```

### 1f. Turn-end and post-compaction — see §4. **Not delivered by this channel.** Stated honestly, not faked.

---

## 2. Where the doctrine text lives / who owns it

- **All rail wording:** one module-level function `_rail(point, cl) -> str` in `checklist_engine.py`,
  plus a small `_RAIL` string table keyed by decision-point type. Callers (`current`, `advance`,
  `start`, and the top-level `REFUSED` printer at line ~1415) append `_rail(...)`.
- **Gate-specific tokens:** derived at call time from `cl["items"]` (position/distance) and the next
  item's `imperative`. Nothing is authored per-gate; nothing is stored.
- **Owner:** the engine maintainer, in **one place**. This is the whole point — update the rail once,
  all nine skills inherit it with no per-skill or per-template edit. `global-everyone.md` keeps the
  *prose* doctrine for load-time reading; the engine rail is its *just-in-time echo*. They must not
  drift — a one-line pointer in `global-everyone.md` ("the engine echoes this rail at each step") keeps
  them married without duplicating the sentences.

---

## 3. Eval-check implications (#129 harness)

- **State/journal:** unchanged. Rail text is additive stdout/stderr; no schema field, no new verb, so
  the journal hash-chain, lease-window checks, and "release is the last journaled action" invariant are
  untouched. **No #129 check needs to change.**
- **Does the measured bar move?** Mechanically **unchanged**. Response text is a deterrent; a determined
  cheap model can still ignore it, so nothing here is *test-pinnable* as a mechanism. The only honest way
  to measure value is to **re-run the sonnet eval and watch the completion rate** — same instrument as
  today. The bar becomes *stricter in practice only if the deterrence works*, which is an empirical claim
  this design cannot self-certify.
- **Cheap optional add:** a regression test asserting the rail substrings are present in engine output
  (e.g. `assert "MIDDLE of the run" in current(cl)`). That guards the rail from silent deletion — but it
  tests the **engine**, not the agent. It does not make the *agent-completion* bar stricter.

---

## 4. Failure-shade coverage (honest)

| Shade | This channel | Mechanism |
|---|---|---|
| skip (whole workflow) | **deter** | distance-to-terminal + "workflow IS the deliverable" at every `current`. Cannot force the *first* call — no engine call, no rail. |
| skip (a gate) | **prevent** (inherited) | active-gate enforcement already refuses out-of-order `start`/`advance`; rail just re-explains it. |
| theater / hand-written spine | **deter** | check-failure string names fabrication; the *mechanism* is the journal (existing, not mine). |
| quit-early | **deter** | "past no gate for free — stopping is quit-early" on every advance + distance count. |
| fabrication (invented evidence) | **deter** | check-failure interceptor; mechanism = engine check + journal (existing). |
| completion-theater-at-finish (false "released") | **deter** | terminal release-ordering string; mechanism = eval lease-vs-journal cross-check (existing). |
| wait-by-ending-turn | **deter only** | rail says "do not end turn to wait — poll in-turn". Response text **cannot** mechanically block a turn-end. |
| **turn-end refusal** | **NOT COVERED** | no engine call fires at the turn boundary. Needs a Stop hook (Designer B's channel). Honest null. |
| **post-compaction push** | **PARTIAL** | rail cannot *push* after compaction. It re-lands **only when the agent next invokes the engine** — which the mandated entry ritual ("re-run `current` on resume") forces. So coverage = "on the agent's first post-compaction engine call", never "immediately/unprompted". |

---

## 5. Axis self-assessment (where the constraint hurts)

- **Depth:** shallow implementation, broad reach. A handful of strings + one derive-from-state function
  touches every decision point that *has* an engine call. High leverage per line; all nine skills inherit
  free.
- **Locality:** *strongest axis.* Every rail sentence lives in one function in one file. Update once,
  fleet-wide effect, no template or skill edits. This is the minimal constraint paying off.
- **Seam placement:** the seam is engine stdout/stderr — a *good* seam because the engine is already the
  mandatory transition chokepoint, so the rail rides infrastructure the workflow already forces. The
  *weakness is intrinsic to the seam*: it exists only where the agent already chose to call the engine.
  At turn-end and at the compaction boundary there is no call, so the seam is silent exactly where two
  of the nastiest shades live. No amount of wording fixes a seam that isn't there.
- **Testability:** rail strings are trivially unit-testable (substring asserts). But the property we
  actually care about — *does the cheap model comply* — gains **no new deterministic assertion**; it
  stays measurable only through the sonnet eval, identical to today. Honest: this design adds confidence,
  not a new pass/fail gate.

---

## 6. Deliberately NOT solved (scoped for the comparison)

- **Turn-end refusal** — genuinely out of channel; needs a Stop hook. This is the clearest case for a
  richer channel and I concede it rather than fake it.
- **Post-compaction *push*** — out of channel; I rely on the mandated `current`-on-resume to re-land the
  rail. If that ritual is skipped, the rail never fires. A SessionStart-on-compact hook is the real fix.
- **Per-gate bespoke "why"** — *refused on principle*: it is a schema field that relocates the
  nine-copies problem. I carry a fixed doctrinal why keyed to decision-point type instead.
- **#134 gate-vs-fence write reconciliation** — response text can *emit* fence-aware guidance at the
  feedback/archive gate ("stage the durable trio worktree-local, cite the fence, harvest at closeout"),
  but it **cannot change WHERE the gate condition writes** — that is a check/verb change, out of my
  channel. I deter with wording and defer the mechanism to a verb-owning design.
- **Forcing the first engine call** — nothing in this channel can reach an agent that never invokes the
  engine at all; that is skill-load-time doctrine's job, not the rail's.
