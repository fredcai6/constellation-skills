# DIT I1 candidate — constraint: **minimal-interface**

*Engine answerability designed as the smallest possible addition to the existing verb set.*

## Thesis (the one design move)

Every over-read in x1 is a question asked at one of exactly **two moments the engine already
prints at**:

- **"what now?"** — answered by `current` (already the agent's heartbeat call).
- **"why not?"** — answered by the `REFUSED:` line (already printed on stderr at every refusal).

So the minimal interface adds **zero new verbs and zero new flags.** It widens the *two strings the
engine already emits at those two moments* until they carry what the agent currently goes to disk for.
The deep-module boundary is unchanged; only the payload crossing it grows. This is the disciplined
answer to the brief's test — *"could an existing verb's output carry this?"* — applied to all three
observed caller needs, and for all three the answer is **yes**:

| x1 caller need | existing carrier | why it already fits |
|---|---|---|
| get condition ids (Exhibit A) | `current` | already renders the ACTIVE task; it just omits the task's conditions. The agent calls `current` at the exact moment it needs the id — right before `attest`/`advance`. |
| recover from refused/blocked (Exhibit B) | the `REFUSED:` line | already raised BY the verb that knows precisely why (`start` raising `is 'blocked'`); the fix is that the raised message names the sanctioned recovery verb. |
| untruncated step detail (Exhibit A) | `current` | already prints the imperative; the engine must guarantee the WHOLE imperative crosses, and doctrine forbids re-fetching it from disk. |

No `explain`/`show`/`describe` verb is minted. Idea 2's `explain` verb is **the road not taken** here
(loud skip): a standalone query verb is a second answerability surface the agent must remember to call,
at a moment distinct from where it already stands. minimal-interface refuses that second surface and
instead makes the two strings the agent *already receives* total over the questions.

---

## Interface — the two output contracts

### A. `current` (enriched renderer — same verb, wider output)

`current` continues to emit the lease line, `ACTIVE <id> [<status>] — <imperative>`, and the existing
`DIGEST:` / `REFRESH REQUESTED:` / `RAIL:` / Trip-advisory suffixes **unchanged**. It gains two blocks:

1. **CONDITIONS block** — for the active task, each *open* (unsatisfied, non-waived) pre/postcondition,
   one per line, prose-shaped:
   ```
     postcondition c1 [pending] command  — work area scaffolded and spine.json materialized
     postcondition c2 [pending] manual   — engine session lease claimed for this spine
   ```
   Fields drawn from the real condition dict: `id`, satisfaction state (`pending`/`satisfied`/
   `attested`/`waived`), check `kind` (`command`/`artifact`/`git-change-policy`/`manual` for
   `check: null`), and `statement`. This is the **condition-id answer** — the agent reads the id it
   must pass to `attest --cond` without ever opening the file. Satisfied conditions are summarized
   (`2/3 met`) not listed, so the block stays short.

2. **RECOVERY line** — emitted only when `status == blocked`, derived from `status_detail`:
   ```
   BLOCKED: <blocker> (authority: <authority_needed>). Next: <next_action>.
     Clear with: resume <id> --reason "<how the blocker was resolved>"  (or skip / reopen if OBE)
   ```
   This single line is what Exhibit B read engine *source* to discover — surfaced at the agent's
   heartbeat call. It reflects the live engine: `resume` already exists (`checklist_engine.py:1157`)
   and restores the pre-block status; the renderer names it. When the blocked gate has no restorable
   prior (rework-cap escalation), the line instead points at `reopen`/`skip`/human — mirroring
   `resume`'s own refusal text, so `current` never advertises a verb that will itself refuse.

### B. `REFUSED:` (enriched raise sites — same path, wider message)

The dispatch wrapper `REFUSED: {exc}{rail}` (`:1937`) is **unchanged**. The enrichment lives at the
`raise EngineError(...)` sites: every refusal of a state-transition names the **sanctioned next verb**
in its own message. The load-bearing ones are the blocked-state refusals — `start`/`advance`/`attest`
against a blocked gate:

> `REFUSED: confirm is 'blocked', not startable; resolve the blocker then `resume confirm --reason "..."`
> (or `skip`/`reopen` if OBE). Do not edit the JSON — use the engine.`

The "Do not edit the JSON" clause directly counters the doctrine breach x1 recorded (`checklist-engine.md:118`).

### C. `check-failure` rail (one clause added)

The rail (`:179`) already says *"do the missing work and attest/attach … or escalate with block/waive."*
Add one clause pointing back at the enriched `current`: *"Run `current` to see the open condition ids
and, if blocked, the exact clear command."* The rail becomes the pointer that closes the loop — an agent
at a refusal is told to consult `current`, which now answers completely.

**What the rail strings promise, restated:** at every decision point the agent is *always* one
engine call (`current`) away from the full open-condition list and, when stuck, the exact recovery
command — never a file, never source.

---

## Invariants (what the engine always tells you, at each moment)

- **After any `current`:** the agent holds the active id, its *full* imperative, every id it could pass
  to `attest`/`advance`, each open condition's satisfaction state and check kind, and — if blocked —
  the exact recovery command. No residual question is answerable *only* by the file.
- **After any refusal:** the agent holds *what* was refused, *why* (the raised message), and the
  *sanctioned next verb*. A refusal never dead-ends into a state resolvable only by reading source.

## Error modes (what a refusal now carries)

A refusal is `REFUSED: <verb-specific reason naming the next verb>` + the widened check-failure rail.
The three refusal families and what each now carries:

- **precondition/postcondition unmet** — already names the unmet ids (`:1033`, `:1070`); rail points to
  `current` for their statements. (Already good; rail clause is the only add.)
- **wrong-state transition** (`start` on blocked, `reopen` on non-complete, `resume` on non-blocked) —
  now names the correct verb for the actual state, so the Exhibit-B grep-the-source loop cannot start.
- **authority/why-missing** — already names the exact flag (`--why`/`--mechanical`, `:1083`); unchanged.

## What becomes forbidden (doctrine line — idea 1)

Opening `spine.json` / `cycle-*.json` / `checklist_engine.py` between `claim` and `release` is a
**lintable violation**, because `current` + the `REFUSED:` line are now *total* over the questions those
files answered. This is enforceable **precisely because** minimal-interface kept the surface to two
strings: there is a single, small, auditable place where "the engine's answer" lives, so "the agent
never needs the file" is a claim about two functions, not a sprawling verb set.

---

## Before / after — the real x1 exhibits

### Example 1 — condition-id lookup (Exhibit A, `3c5f5837…jsonl:41-49`)

**Before:** `current` returns `ACTIVE init [in-progress] — Run: py …init_work_area.py … (do n`
[truncated]; agent tries a one-liner assuming key `steps`; `KeyError: 'steps'`; **reads all 271 lines
of `spine.json`** to find `c1`/`c2`. Cost ≈ 271 lines ≈ 2,700 tokens.

**After:**
```
ACTIVE init [in-progress] — Run: py …/init_work_area.py explore-design-thrust --spine …  [full imperative]
  postcondition c1 [pending] command — work area scaffolded and spine.json materialized
  postcondition c2 [pending] manual  — engine session lease claimed for this spine
```
Agent runs `attest init --cond c2`. **Zero file reads.**

### Example 2 — blocked-state recovery (Exhibit B, `90ab6530…jsonl:1060-1098`)

**Before:** `current`/`start`/`attest` all return terse `REFUSED: … is 'blocked'`; agent greps engine
source for `blocked`, tries `reopen` (refused "can only reopen a complete gate"), greps again, **reads
engine source at two offsets**, concludes no unblock verb exists, and **hand-edits `spine.json` via
inline Python** to flip status — the exact bypass `checklist-engine.md:118` forbids.

**After:** `current` on the blocked gate prints:
```
ACTIVE confirm [blocked] — [full imperative]
BLOCKED: waiting on human sign-off (authority: human). Next: get explicit confirmation.
  Clear with: resume confirm --reason "<how the blocker was resolved>"  (or skip / reopen if OBE)
```
and `start confirm` refuses with `REFUSED: confirm is 'blocked', not startable; resolve the blocker
then resume confirm --reason "…" (or skip/reopen). Do not edit the JSON — use the engine.` Agent runs
`resume confirm --reason "human confirmed"`. **Zero source reads, zero raw mutation.**

### Example 3 — truncated `current` forces a raw read (Exhibit A, `90ab6530…jsonl:55`)

**Before:** right after `init_work_area.py` scaffolds a fresh spine, the agent **reads the raw 86-line
spine** instead of calling `current` at all — partly habit, partly distrust that `current` carries the
whole imperative + conditions.

**After:** `current` is the documented *complete* source (full imperative + CONDITIONS block), so the
first move after scaffolding is `current`, and the doctrine line makes the read a lint violation. The
distrust is removed because there is provably nothing in the file `current` didn't print.
**Scoped weakness (honest):** if the *caller's terminal* truncates a very long imperative, the engine
emitted the full bytes but the display cut them — see weakness (d).

---

## Self-scores (depth / locality / seam placement / testability)

### Depth — **4.5/5**
Zero JSON structure crosses the boundary: the agent never learns the key is `items` vs `steps`, never
sees `status_detail`'s shape — it receives rendered sentences. The module gets *deeper* (more hidden
behind the same two strings), which is the textbook definition of a deep module.
**Weakness:** enriching `current` pushes more text per call, so a lazy caller could begin
pattern-matching the CONDITIONS block as a de-facto schema — the rendered text ossifies into a
contract. Mitigated by keeping it prose-shaped (em-dash sentences, not parseable columns), but the risk
is real: the wider the string, the more it invites parsing.

### Locality — **5/5** (the constraint's biggest win)
The entire change is `checklist_engine.py` — `current()` (`:1003`), a shared `_recovery_hint(t)` helper,
the wrong-state `raise` sites, and one `check-failure` rail string (`:179`). **No SKILL.md changes:**
skills already say "ask the engine"; the engine now answers more. Nothing fans out into every skill body.
**Weakness:** the blocked-recovery wording lives in two places (the `current` RECOVERY line and the
`start`/`attest` refusals). Contained by a single `_recovery_hint(t)` helper both call, but it is a
coupling to watch — if `resume` semantics change, one helper must move, not scattered strings.

### Seam placement — **5/5** (strongest axis)
The two moments — "what now?" and "why not?" — are *exactly* where the agent stands when it currently
goes to disk. We add nothing the agent must *remember* to call; we widen what it already receives at its
heartbeat call and at the instant of a dead end. That is the seam at the point of confusion, by
construction.
**Weakness:** a question asked at *neither* moment has no home. Specifically, "what are the condition
ids of a **non-active downstream** gate?" (planning ahead) is unanswerable, because `current` only
renders the active task and minimal-interface refuses a `show <id>` verb. x1 shows **no** instance of
this need, so I judge it rare — but it is the honest hole this constraint leaves, and the file remains
its only answer.

### Testability — **4/5**
Two concrete, cheap tests: (1) the **structure-blindness eval** (idea 5) asserts zero Reads of
`spine.json`/`checklist_engine.py` between `claim` and `release` — under this candidate it passes *by
construction* and fails loudly the moment a caller need reappears that the two strings don't cover,
which is the exact falsification the brief wants. (2) **Golden-output unit tests** on `current()` for
each active-task state (open-with-conditions / blocked-with-recovery / done) and on each wrong-state
refusal asserting it names a verb — exact-string tests, the style the engine's 906-test suite already
uses (x4).
**Weakness:** the eval proves the agent *didn't* read the file on a given run, not that it *couldn't
have needed to* — a run that never hits a blocked state never exercises the recovery path, so eval
coverage depends on scenario design touching each state. The golden tests cover the states the eval
misses, but keeping the two in sync with real caller moments is manual.

### Named weaknesses, consolidated
- **(a) rendered-text-as-contract ossification** — the wider `current` output invites callers to parse
  it; the wider the string the greater the pull. (depth)
- **(b) no home for forward-looking / off-active queries** — deliberate refusal of a `show <id>` verb
  leaves downstream-gate lookups answerable only by the file; rare in x1 but real. (seam)
- **(c) recovery wording duplicated** renderer ↔ raise-sites — contained by one helper, still a
  coupling. (locality)
- **(d) terminal truncation of a long imperative** is outside the engine's reach, and this candidate
  *declines* to add a pager/`--field` flag to solve it — that would be a new surface, which the
  constraint forbids. Honest cost of refusing to grow the interface. (depth/seam)

---

## One-line self-summary
The smallest interface that makes the file unnecessary: **no new verbs** — widen the two strings the
engine already prints (`current` gains the active task's open conditions + a blocked-recovery line;
every wrong-state `REFUSED` names its sanctioned next verb), and the file becomes lintably forbidden
because two small functions are now total over what it answered.
