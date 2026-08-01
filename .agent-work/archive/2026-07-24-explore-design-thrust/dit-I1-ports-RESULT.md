# DIT I1 candidate — constraint: **ports-and-adapters**

*One agent of the N=3 answerability panel. Constraint: separate the engine's queryable
state (the port) from its presentations (adapters). Design the port to serve the
conductor-inversion future (package D) while staying useful to an agent at a terminal today.*

---

## The candidate in one sentence

Add **one pure state-projection function** — `state(cl, refusal=None) -> StateView` — that
is the single sanctioned answer to "what is true right now, and what may I legally do next,"
and render it through **two thin adapters**: the human CLI text agents read today (default)
and a machine `--json` serialization a future conductor/hook consumes **without any new
verbs**. The refusal path flows through the *same* port, so "how do I recover" is answered by
the same contract that answers "what's active."

---

## Why this is the ports-and-adapters answer (deep-module framing)

Today every verb is its own little presentation function. `current()` hand-formats
`"ACTIVE g-2 [in-progress] — <imperative>"`; `start()` returns `"g-2 -> in-progress"`;
a refusal is a bare `f"REFUSED: {exc}"`; the doctrine rail is bolted on at the CLI boundary
by `_rail()`. There is **no single place that says what the engine's state IS** — every answer
is a side effect of a verb, formatted inline, and none of them is complete. That is exactly why
x1 agents fall through to the raw file: the only *complete* view of state is `spine.json` itself.

The port fixes the root cause, not the symptom:

- **The port is the deep module.** Narrow interface (`cl` in, `StateView` out), hiding the
  entire checklist mechanic: item ordering, the `TERMINAL` status set, condition kinds
  (command/artifact/null), `waived`/`attested` honoring, lease-staleness, `why_trail`
  resolution, and the rail-position derivation. One seam owns "what is knowable about a run."
- **The adapters are shallow by design.** `render_human(view)` and `render_json(view)` are pure
  formatters. They add *no* knowledge; they only choose presentation. This is the whole point of
  the split — knowledge lives once, in the port; presentation is disposable and multipliable.
- **JSON structure can no longer leak upward**, because the JSON *is* the sanctioned, versioned
  contract (`StateView`), not the raw persistence schema. An agent (or conductor) that reads
  `--json` reads a stable projection the engine promises to hold — not `spine.json`'s internal
  key `items` vs `tasks` vs `steps` (the exact key an x1 agent guessed wrong and got `KeyError:
  'steps'`). The port *decouples* the query contract from the storage layout.

## The port contract (what state is queryable, and its invariants)

`state(cl, refusal=None) -> StateView`, a plain dict with a **frozen top-level shape**:

```
{
  "kind":     "gated" | "survey",
  "position": "early" | "mid-flight" | "near-terminal" | "terminal" | "done",
  "lease":    {"owner","session","stale":bool} | null,
  "active":   null | {                       # null iff position == "done"
     "id":            "g-2",
     "status":        "in-progress",
     "imperative":    "<FULL, never truncated>",
     "preconditions": [ {"id","satisfied":bool,"waived":bool,"attested":bool,"kind"} , ... ],
     "postconditions":[ ...same shape... ],
  },
  "why":        {"gate","live":"<running understanding>"} | null,
  "next_verbs": [ "attest --id g-2 --cond <pre> --which preconditions",
                  "advance --id g-2 --why <understanding>" ],   # legal moves FROM here, with arg templates
  "trip":       {...} | null,                # the #182 context-gauge advisory that already rides `current`
  "refused":    null | {                     # populated ONLY on the REFUSED path
     "verb":     "start",
     "reason":   "g-4 is 'blocked'",
     "blocker":  "waiting on x1 result",     # structured, when the refusal carries it
     "recovery": [ "resume --id g-4 --reason <why the blocker cleared>" ],  # the specific legal exits
  },
  "contract":   1,                            # version int — bump on any breaking shape change
}
```

**Invariants the port promises (this is the enforceable part of "never open the file"):**

1. **Completeness.** Every id an agent could otherwise need from `spine.json` — the active id,
   every condition id, the imperative in full, the live why, the lease owner — is present in
   `StateView`. This is *falsifiable*: diff the id-set reachable from raw spine against the
   id-set in `state()`; a non-empty difference is a bug in the port (see Testability).
2. **Purity / read-is-not-a-probe.** `state()` reports **recorded** condition satisfaction; it
   NEVER re-runs a command/artifact check (those are `attest`/`advance`'s job). A conductor
   reading the port therefore never triggers side effects. Sharp edge, made explicit: `satisfied:
   false` means "not yet recorded as passing," not "would fail if run now."
3. **Refusal is a state, not a string.** A refused verb produces a `StateView` with `refused`
   populated *and* `active`/`next_verbs` still valid — the same shape as a success. Recovery is
   derived from task status, not authored per-message: `blocked -> [resume]`, `complete gate ->
   [reopen]`, `postconditions unmet -> [attest that cond | waive it | block]`.
4. **`next_verbs` is exhaustive and legal-from-here.** It is derived from `(status, position,
   condition state)`, so it is exactly the set of verbs that will NOT refuse from the current
   state. This is the anti-"read the source to find a verb" invariant.
5. **Shape is versioned and frozen.** `contract` bumps only on a breaking change; adapters and
   any future conductor pin it. Additive fields don't bump. (The five FROZEN rail strings, a
   measurement precondition for #145, are reproduced verbatim BY the human adapter — see below —
   so freezing the port does not disturb them.)

## The adapters

- **`human` (default).** `render_human(view)` reproduces today's terse `current` line and the
  frozen rail block verbatim — so the 906 exact-equality tests survive — then adds two things the
  raw read was being used for: the condition ids under the active line, and, on refusal, the
  `recovery` list in place of (before) the generic check-failure rail. Stays terse: one active
  line, an indented conditions line, one `next:` line. Never JSON.
- **`json` (`--json`, a global flag on `--file`, applying to every verb's stdout AND to the
  REFUSED path).** `render_json(view)` is `json.dumps(view)`. This is the adapter a **conductor
  process or a hook** consumes. It needs **no new verbs**: the conductor asks the questions an
  agent asks (`current --json`, and reads `refused` off any `--json` refusal) and gets the whole
  contract. That is the load-bearing promise of this constraint — future adapters are new
  *renderings of the same port*, not new query surface.

## Error modes

- **Refused verb** → exit 1, `refused` populated in the view; human adapter prints
  `REFUSED: <reason>` + `recover: <recovery...>` + rail; json adapter prints the full view to
  stdout (refusal is data, not just a stderr string). `main()` already persists legitimate
  mutations on the error path; unchanged.
- **`--json` on a survey / terminal / done state** → a well-formed view with `active: null`,
  `kind: "survey"`, `refused: null`. No special-casing for the consumer.
- **Corrupt/legacy spine (no `why_trail`, no lease)** → port degrades to nulls, never raises
  (matches the engine's existing backward-compat posture). A missing field is `null`, not absent.
- **Contract drift** → a consumer pinned to `contract: 1` sees the int change and fails loud,
  rather than silently mis-parsing.

## What the rail strings promise, restated through the port

The rail today is doctrine-at-a-decision-point bolted onto six verbs. Under this candidate the
rail becomes **the human adapter's rendering of `position` + `next_verbs` + `refused.recovery`**.
The frozen strings stay verbatim (human adapter emits them), but the check-failure rail gains a
*specific* recovery line beneath it — the generic "do the missing work and attest, or escalate"
prose is now backed by the exact verbs legal from this task's status. The json adapter carries the
same `next_verbs`/`recovery` as data, so a conductor gets the doctrine's *operational content*
without parsing English.

---

## Before / after (from the x1 exhibits)

**Exhibit A — truncated `current` forces a 271-line raw read (need #3 detail + need #1 ids).**

Before (`3c5f5837…jsonl:41-49`): `current --verbose` output cut off mid-imperative
(`"...placeholders resolved (do n"`), agent guesses schema key `steps`, gets `KeyError: 'steps'`,
`Read`s the whole 271-line `spine.json` to see one task's condition shape.

After — human adapter (non-truncating, ids inline):
```
$ checklist_engine.py --file spine.json current
ACTIVE t-3 [in-progress] — scaffold .agent-work/explore-design-thrust/ and materialize
spine.json with its placeholders resolved (do not commit yet).
  preconditions:  pre-1 [ok]  pre-2 [unmet]
  postconditions: post-1 [unmet · artifact]
  next: attest --id t-3 --cond pre-2 --which preconditions | advance --id t-3 --why <understanding>
```
After — json adapter (a hook/conductor):
```
$ checklist_engine.py --file spine.json --json current
{"kind":"gated","position":"early","active":{"id":"t-3","status":"in-progress",
"imperative":"scaffold ...(do not commit yet).","preconditions":[{"id":"pre-1","satisfied":true},
{"id":"pre-2","satisfied":false}],"postconditions":[{"id":"post-1","satisfied":false,"kind":"artifact"}]},
"next_verbs":["attest --id t-3 --cond pre-2 --which preconditions","advance --id t-3 --why <...>"],
"refused":null,"contract":1}
```
Both give the full imperative (#3) and every condition id (#1) — zero file reads, and the json
key is the *contract's* `active.preconditions[].id`, never the raw spine's internal layout.

**Exhibit B — mis-applied `block`, no recovery verb, source-read then hand-mutation (need #2).**

Before (`90ab6530…jsonl:1060-1098`): `start`/`attest` return terse `REFUSED: confirm is
'blocked'…`; agent greps the engine for `"blocked"`, tries `reopen` (refused), greps again,
**reads `checklist_engine.py` source at two offsets**, concludes no unblock verb exists, and
**hand-edits `spine.json` via inline Python** to flip status — the exact bypass doctrine forbids.

After — human adapter (specific recovery on the refusal):
```
$ checklist_engine.py --file spine.json start g-4
REFUSED: g-4 is 'blocked' (blocker: waiting on x1 result; authority: parent agent).
  recover: resume --id g-4 --reason <why the blocker cleared>
  RAIL: This check failed; that verdict is scoped to this check, not the approach. ...
```
After — json adapter (what a conductor reads to decide dispatch-or-escalate):
```
$ checklist_engine.py --file spine.json --json start g-4
{"refused":{"verb":"start","reason":"g-4 is 'blocked'","blocker":"waiting on x1 result",
"recovery":["resume --id g-4 --reason <why>"]},"active":{"id":"g-4","status":"blocked",...},
"next_verbs":["resume --id g-4 --reason <why>"],"contract":1}
```
The `resume` verb the agent burned two source-reads and a doctrine-violating hand-edit to find is
now the **first line of the refusal**, because the port derives legal-next-verbs from `status ==
blocked`. The conductor future reads the identical `recovery` as data.

---

## Self-scores (honest, on the four brief axes)

**Depth — HIGH (strongest axis).** One narrow seam hides all checklist mechanics; adapters carry
zero knowledge. Uniquely among the three constraints, this one makes "leak JSON structure upward"
*structurally impossible* — the exposed JSON is a versioned contract decoupled from storage, so
enriching or refactoring the spine schema never breaks a caller. The port is a genuine deep module.

**Locality — MEDIUM-HIGH.** Fully contained in `checklist_engine.py` + the rail strings; fans out
into **zero** SKILL.md files. The honest tax: to keep the 906 exact-equality tests green *without*
a giant diff, the port runs **alongside** the existing verb-return strings rather than replacing
them, so for a transition period there are **two rendering paths that must agree** (each verb's
hand-formatted string vs the human adapter). Full inversion — verbs return `StateView`, the CLI
boundary renders — is the clean end state but a bigger, riskier change; I'd ship the port + `--json`
first and consolidate the verb strings into the human adapter as a fast-follow. Named, not hidden.

**Seam placement — HIGH.** Both x1 moments-of-confusion route through the port: a truncated line
(→ non-truncating human render / `--json`) and a REFUSED (→ refusal-as-`StateView`, recovery
inline). The key move is treating a refusal as a *state view*, which puts the seam exactly where
the agent stands at the moment of confusion, not one indirection away.

**Testability — HIGH (differentiator).** The port is a pure `cl -> dict`, so the **structure-
blindness eval (idea 5) becomes a diff**: assert the id-set in `state()` ⊇ the id-set an agent
could reach from raw spine; a non-empty difference *falsifies* "the agent never needs the file."
One golden-JSON fixture per `position` pins the whole contract; the human adapter keeps exact-
equality tests. This is the only candidate where "agent never needs the file" is a mechanical
assertion, not a judgment call.

## The cost of the extra abstraction TODAY (loud skip / honest weakness)

1. **The json adapter has zero live consumers right now.** The entire port/adapter *split* is paid
   today for a future (conductor/hook, package D) that has not shipped. A minimal-interface
   candidate delivers needs #1–#3 to a terminal agent with ~two string edits (enrich `current`,
   enrich REFUSED) and **no** second serialization or stability contract to maintain. My candidate's
   bet is explicit: package D is human-named as the core thread, and the payoff is that when the
   conductor arrives it needs *no new query verbs* — it reads the port. **If D dies, this is
   over-built.** That is the real trade to adjudicate against the min-interface candidate.
2. **`--json` can re-introduce the very over-read it cures.** A tight human line is far fewer
   tokens than a full state dump; an agent that reflexively `--json`-dumps every step is *worse*
   than the truncated line. So the human adapter MUST stay the terse default and `--json` MUST be
   opt-in (for tooling/conductor), or the cure costs more context than the disease.
3. **The `--json` global flag is a hair's cheat on "no new verbs."** I add no verb, but I do add a
   presentation flag and surface an implicit full-state projection on `current`. I'd argue
   `current` already *is* the state-query verb and `--json` only swaps its adapter — but a reviewer
   should weigh whether "one global flag" is genuinely smaller than the min-interface candidate's
   "no new surface at all."
