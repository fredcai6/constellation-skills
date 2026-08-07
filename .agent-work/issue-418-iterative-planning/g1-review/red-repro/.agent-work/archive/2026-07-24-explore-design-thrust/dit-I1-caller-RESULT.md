# DIT I1 candidate — constraint: **common-caller-first**

**Candidate name:** *Answer at the chokepoint* — fatten the two surfaces the caller already
touches (`current` and the REFUSED path) so the three observed needs are served with zero new
verbs and zero file reads. No general query verb is added; that is the deliberate skip (see §5).

The method the constraint demands: write the *ideal* transcript for each of x1's three caller
needs, then let the interface be whatever those transcripts require. All three, done honestly,
land on the same two chokepoints — so the interface is those two outputs, made complete.

---

## 1. The three ideal transcripts (before → after)

### Need 1 — get condition ids for `attest`

**Before** (measured, `3c5f5837…jsonl:41-49`): three moves, ~271 lines of tax.
```
$ engine current --verbose
ACTIVE g3 [in-progress] — …materialize spine.json with its placeholders resolved (do n   ← truncated
$ python -c "... j['steps'] ..."          → KeyError: 'steps'   (guessed the schema key wrong)
$ Read spine.json                         → 271 lines, to find that g3's postcond ids are c1,c2
$ engine attest g3 --cond c1 --which postconditions --note "…"
```

**After** — one move, zero reads:
```
$ engine current
ACTIVE g3 [in-progress] — <full imperative, never truncated>
  postconditions:
    c1  [pending]   artifact: DESIGN_SPEC.md present, status=confirmed
    c2  [pending]   command:  pytest -q tests/spine
  RAIL: <existing mid-flight rail>
$ engine attest g3 --cond c1 --which postconditions --evidence e-g3-1
```
The condition ids the caller's *next* verb needs are already on screen. The transcript is
`current` → `attest`. The file read is gone because the id was never on disk-only.

### Need 2 — recover from a refused / blocked state

**Before** (measured, `90ab6530…jsonl:1060-1098`): six moves, two source reads, ending in a
doctrine-forbidden hand-edit of spine.json.
```
$ engine start g5        → REFUSED: confirm is 'blocked'…        (no next step)
$ Grep checklist_engine.py "blocked"
$ engine reopen g5       → REFUSED: can only reopen a complete gate
$ Grep checklist_engine.py "unblock|reopen|blocker"
$ Read checklist_engine.py (offset 752, 946)   → confirm no 'unblock' verb exists
$ python -c "… flip status blocked→in-progress …"   ← bypass; the forbidden edit
```

**After** — one move, the refusal names the exact exit verb:
```
$ engine start g5
REFUSED: g5 is 'blocked', cannot start
RECOVER: g5 is blocked. Clear it with `resume g5 --reason <why>`, or leave it blocked and
         escalate. (There is no 'unblock' verb — `resume` is the sanctioned exit.)
$ engine resume g5 --reason "provisioning landed, unblocked"
```
The knowledge the agent reconstructed by *reading engine source* — "what verb exits the
`blocked` state" — is exactly the state-machine knowledge only the engine holds. It now rides
the refusal. No grep, no source read, no bypass.

### Need 3 — get untruncated step detail

**Before**: `current --verbose` truncates mid-sentence → fall through to a raw `spine.json`
read to see the whole imperative (`3c5f5837…jsonl:42,49`; recurs `90ab6530…jsonl:55`).

**After**: the `current` output in Need 1 *is* the untruncated detail. There is no separate
`--verbose` mode to truncate; the plain output is already complete. (§4 on why this stays cheap.)

**The convergence:** needs 1 and 3 are the same surface (`current`, made complete); need 2 is
the other surface (REFUSED, made state-specific). Two outputs, no new verbs. That is the whole
candidate.

---

## 2. Deep-module terms

### Surface A — `current` becomes a complete gate briefing

**Invariant (the load-bearing promise):** *`current`'s output is a superset of every argument
the caller's next verb needs.* After `current`, the caller can construct the next
`attest` / `advance` / `start` / `resume` command without reading any file. This is the
falsifiable core (§4 testability).

**Output contract** — gated checklist, active task:
```
[lease line, if a lease exists]
ACTIVE <id> [<status>] — <full imperative, verbatim, never elided>
preconditions:                    ← block omitted entirely when the list is empty
  <pid>  [<state>]  <kind>: <one-line check summary>
postconditions:                   ← block omitted entirely when the list is empty
  <cid>  [<state>]  <kind>: <one-line check summary>
RAIL: <existing position rail, unchanged>
```
- `<state>` ∈ `satisfied | waived | pending` and is read from the **stored** condition flags
  (`satisfied` / `waived` / `attested`), NOT live-evaluated. `<kind>` is `command` /
  `artifact` / `git-change-policy` / `attest-only` (for `check == null`). For a command
  condition not yet satisfied, state is `pending` (engine has not run it), never a fake
  green — honest about what the engine has actually checked.
- Survey (non-gated) checklists and the DONE/empty cases keep today's exact output — condition
  blocks are a gated-active-task feature only.

**Depth win:** the JSON shape (`items`, `tasks[id].postconditions[].id`) never surfaces; the
caller sees ids and states, not structure. The schema-key guessing (`KeyError: 'steps'`) can't
happen because the caller never touches the schema.

### Surface B — REFUSED carries a state-derived recovery line

**Invariant:** *every REFUSED caused by task STATE names the exact verb that changes that
state* — the specific command, not generic doctrine.

A pure helper `_recovery(cl, iid, attempted_verb) -> str` maps `(status, attempted verb)` to
the sanctioned exit. It is engine-owned because the state machine is engine-owned — this is
precisely the knowledge that leaked to source-reads:

| current status | attempted | recovery line (the exact next command) |
|---|---|---|
| `blocked` | start/attest/advance | `resume <id> --reason <why>` (names it; states no `unblock` verb exists) |
| `complete` | start/attest/reopen | `reopen <id> --reason <why>` (notes the rework cap applies) |
| `pending`, precondition unmet | start | keep the unmet-id list **and** append `attest <id> --cond <pid> --which preconditions` |
| any | attest, cond id unknown | **list the valid ids**: `valid conditions: pre[<pids>] post[<cids>]` |

The last row fixes a second under-informative error observed in source: `attest`'s
"condition not found" refusal (engine line 1566) names *nothing* the caller can use — my
contract makes it enumerate the ids, so need 1 is served on the error path too.

**Placement:** `_recovery` rides `main()`'s REFUSED path (engine line ~1937), exactly like the
existing `check-failure` rail. Verb functions stay **pure** — no return-value change — so the
exact-equality tests the #138 rail preserved keep passing.

**Recovery ≠ check-failure rail.** They are distinct channels: the frozen `check-failure` rail
says *"you did the work wrong — attest/attach or escalate"*; the recovery line says *"you are
in a state this verb cannot act from — here is the state-changing verb."* Exhibit B failed
because only the first existed. Both now fire where each applies.

### What the rail strings promise
The five `_RAIL_STRINGS` stay **frozen and verbatim** (the #145 measurement precondition is
untouched). The recovery line is a **new, separate channel**, state-derived and templated on
`{id}`/`{verb}` — it is not part of the frozen doctrine table, so naming a verb in it does not
paraphrase or violate the freeze.

---

## 3. Invariants & error modes (summary)

- **INV-1 (completeness):** `current` on an active gate contains every condition id of that
  gate. Falsifiable per §4.
- **INV-2 (cheapness/purity):** `current` never executes a condition check — stored flags
  only — so it stays as cheap and side-effect-free as today, and the #138 "current is pure"
  invariant holds.
- **INV-3 (recovery totality):** every `(status, mutating-verb)` pair that refuses on a STATE
  mismatch yields a non-generic recovery line naming a verb. Enumerable in a test.
- **INV-4 (enforcement agreement):** the states `current` shows are the same stored flags the
  verbs read; `current` can never claim `satisfied` where `advance` would refuse, because a
  command condition unproven-by-the-engine shows `pending`, not `satisfied`.
- Error mode — condition with `check == null` (attest-only): shown as `attest-only`, state
  from stored `satisfied`. Error mode — waived postcondition at a DONE gate: the existing
  `WAIVED [...]` line is unchanged.

---

## 4. Why it stays cheap (the one non-obvious step)

Naively, showing `[met|unmet]` tempts calling `_check_condition`, which for a **command**
condition *executes the command* (engine line 504-519) and appends evidence. That would make
the hottest, read-only verb side-effecting and slow — a regression. The contract therefore
pins `current` to **stored flags only**: it reports what the engine has already proven, marks
unproven command checks `pending`, and leaves live evaluation where it belongs, at `advance`.
This is what keeps INV-2 true and is the load-bearing detail a fast read would miss.

---

## 5. Deliberate skip (loud)

**No general `explain <id>` / `--json` query verb.** A verb that details an *arbitrary* task
(a future gate g7 while sitting on g3) is the minimal-interface/ports agent's natural move —
but it is **not** what makes the three observed transcripts shortest. Every measured caller
needed only the **active** gate's detail (to attest it) and recovery from the **active**
refusal. Serving an arbitrary task is unobserved demand; adding the verb now widens the
surface without shortening a single evidenced transcript. I bet against it and name the bet:
if callers start needing non-active-task detail, promote the `current` briefing logic into a
`show <id>` verb reusing the same renderer — cheap to add later, wasteful to add now.

---

## 6. Self-scores (honest)

| axis | score | reasoning |
|---|---|---|
| **Depth** | **5/5** | Hides both the JSON schema (ids not structure) and the state machine (recovery verb) behind two outputs. The two things agents read source/raw-state to reconstruct — condition ids and "what exits `blocked`" — both move behind the seam. |
| **Locality** | **5/5** | Entirely in `checklist_engine.py`: `current()` render + a `_recovery()` helper + the `main()` REFUSED path. **Zero** SKILL.md edits; frozen rail table untouched. |
| **Seam placement** | **5/5** | The constraint's payoff: the two surfaces are the caller's *first move at every gate* (`current`) and *the exact moment of confusion* (REFUSED). Reachable at need with no extra action — that is why the transcripts collapse to one line each. |
| **Testability** | **4/5** | INV-1/3/4 are golden-output + enumeration tests ("current contains every active cond id"; "a blocked task's refusal names `resume`"; every state/verb pair mapped). Directly wires idea-5 structure-blindness eval: assert zero Read calls across a scripted attest flow. −1: INV-2 (no side effects) needs a test that `current` runs no command condition — provable but easy to regress silently. |

### Named weaknesses (not scored away)
1. **Fattens the hottest verb.** `current` grows on every gated call. Mitigated by
   id+kind+state one-liners (not full check bodies) and omitting empty blocks — but a
   many-condition gate yields a longer `current`, and a caller who only wanted "am I done?"
   pays for detail. I refuse a `--brief` mode (reintroduces the truncation-prone split); the
   length *is* the next command's arguments, which is the constraint's whole thesis.
2. **Blind to non-active tasks** — the §5 skip; a real gap I'm betting is unobserved.
3. **Recovery table is a maintenance surface** — a new status/verb pairing added later without
   a table row re-opens the terse-refusal gap. INV-3's enumeration test is the guard; it must
   be kept exhaustive.

---

## 6-line summary
Candidate *Answer at the chokepoint*: serve x1's three needs by fattening the two surfaces the
caller already hits — no new verbs. (A) `current` becomes a complete gate briefing: full
imperative + every condition id/kind/**stored** state, so `attest`/`advance` args are on screen
and the spine.json read dies. (B) REFUSED gains a state-derived `RECOVER:` line naming the exact
exit verb (`blocked`→`resume`), plus `attest` errors now list valid cond ids — killing the
source-read-then-hand-edit bypass in Exhibit B. Key non-obvious constraint: `current` reads
**stored** flags only, never live-runs command checks, so the hottest read-only verb stays cheap
and pure (#138 invariant preserved); rail freeze (#145) untouched via a separate recovery
channel. Deliberate skip: no general `explain <id>`/`--json` verb — unobserved demand, promote
`current`'s renderer to a `show <id>` later if it appears. Scores 5/5/5/4 (depth/locality/seam/
testability); top weakness — fattens the hottest verb.
