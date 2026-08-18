# Lane K return — #634, one spine per agent: frozen bookends, mutable middle

Commander: `constellation/567-k/lane-k/commander-delegated/attempt-1`. Base `9b38b9d9`, rebased
onto `main` at `e92e1a35`. Head **`392b7917`**. **PR #635**, open and mergeable.

---

## 1. Verdict

**Delivered, partially, with two scope floats stated rather than hidden.**

Delivered: the engine now freezes a **declared** bookend, the closing bookend included, while the
middle stays freely mutable; the three role spine templates this lane owns declare theirs; the
plan change stays legible through `amend`'s existing `amendments` trail.

Not delivered, and **floated to you rather than worked around**: the **crew** half of
`decision:every-planning-role`, and the migration of the roles' second-file middles.

Not taken by design: **convergence between the design candidates**. That is the human's.

### The gap I found is not the one the order predicted, and it is worse

The order framed the remaining work as "the roles put their middle elsewhere." Reconciling against
the code first — as delegated-mode doctrine requires — moved that twice:

1. **`amend` already gives a gated plan a mutable middle.** add/drop/rescope on pending gates,
   retext-check on a pending or in-progress one, all-or-nothing, with reason+authority landing in
   `cl["amendments"]`, exposed at the door as `spine_amend`. That half was built.
2. **The closing bookend was not frozen at all.** `_floor()` (`:3036`) freezes what has already
   been *started*, so a plan's opening was covered by accident of status and its closing by
   nothing. I measured it before changing anything:

```
$ amend --delta '{"ops":[{"op":"drop","id":"archive"},{"op":"drop","id":"feedback"},
                         {"op":"drop","id":"review"}]}'
amended: dropped archive, dropped feedback, dropped review (authority probe)
exit: 0
```

A Commander standing at `execute` deleted its own `review`, `feedback` and `archive` in one call,
no `--force` — including the independent-review step `README.md` calls the corpus's core safety
net. Evidence: `.agent-work/567-k/evidence/probe-closing-bookend.md`.

**Caveat I will not let stand as more than it is:** this proves the *capability*, not that anyone
ever did it. I did not search the journals for an occurrence.

---

## 2. What `spine_advance --from_child` is for

**Read at source** (`checklist_engine.py:2617-2645`) **and in its tests**
(`tests/test_checklist_engine.py:429-471`), as `decision:establish-from-child-first` required.

`--from-child` reads a child checklist's `consolidation` and attaches it to the parent gate as
`review-result` evidence *before* postconditions run. `consolidate()` (`:2733`) refuses anything
that is not a **survey** (`:2734`) — and a survey is the **reviewer's** work file. The test fixture
(`_review_gate`, `:430`) is a parent gate carrying `child_checklist` plus an artifact postcondition
matching `{"verdict": "APPROVE"}`.

**So it is a cross-agent verdict seam**: it exists so a *different* agent's finished survey can
satisfy a parent gate's `review-result` postcondition without the parent re-typing the verdict.
`test_advance_from_child_block_refuses` (`:456`) shows the intent — on BLOCK the advance is refused
**but the evidence is still attached**, so a parent cannot launder a rejection into a pass.

**What it means for the design, which is what you asked:** it is **not** a workaround for
gated-can't-grow, so it **survives untouched and left my scope**. And it constrains the design's
vocabulary: *one spine per agent* must mean **one agent drives one spine**, never *no spine may
reference another*. The sanctioned cross-spine reference is evidence flowing **upward**, and
`from_child` is it. A design that removed it would have broken the reviewer seam for no gain.

---

## 3. The design-it-twice comparison

**Full text: `.agent-work/567-k/DESIGN_COMPARISON.md`.** Candidates:
`.agent-work/567-k/crew-handoffs/design-{A,B,C}-result.md`. **Do not converge from this summary —
the comparison document is the deliverable.**

Three cold Sonnet agents, same brief and facts, **one distinct named constraint each**, none
seeing the others, each required to attack itself with ≥4 genuine weaknesses.

| | **A — Positional** | **B — Per-gate flag** | **C — Mutable region** |
|---|---|---|---|
| Constraint | no new state | declare per gate | declare the window once |
| Backward compatible | **No — by its own admission** | Yes | Yes |
| Protects spines already running | **Yes, immediately** | No, until retrofitted | No, and no retrofit path |
| Retrofit through the engine | n/a | **Yes** | **None** |
| Crew (`m0-context, m1`) | **Breaks it** — freezes the real work | Opening only | `before: null` |
| Misdeclared fails | n/a | **silently permissive** | loudly |

**Where all three agree — treat as settled.** All put the guard in the **same four places**; all
leave `_floor()` alone; all need **no door schema change**, which confirms **`spine_amend` is the
seam**. That agreement is why the declaration form is a cheap, late decision: it is one helper.

**Three findings all three reached independently**, which is what makes them worth believing:
`retext-check` is an escape hatch on check *text*; **hand-editing `spine.json` defeats every
candidate** (`load()` is a bare `json.loads`, nothing cross-checks the journal); and the
`execute.json` migration is unfunded because it reaches lane J's files.

**The one factual disagreement, and the measurement that settled it.** A said an Admiral's waves
can never be reified; B said they can. **Neither was right.** On a copy of your live spine:

```
REFUSED: drop execute: only a pending gate can be dropped (is 'in-progress')
```

**The window to reify waves closes the moment `execute` starts.** An Admiral that re-plans at
`latitude` can decompose `execute` into `wave-1..wave-N`; once it has started `execute`, no verb
reaches back. **Your live spine has `execute` in-progress, so this epic can never reify its own
waves.** That answers Local Unknown #3 with a measurement: a doctrine choice with a deadline, not a
free option.

**The cold critic dissolved my own framing, and it was right.** I had written the trade-off as
"immediate protection *or* backward compatibility, not both." That is false: *backward compatible*
describes the mechanism's default reading of an **undeclared** plan and says nothing about whether
you **also run the retrofit** over live spines in the same release. It also found a **fourth
option (D)** — positional for the uncontested *opening*, declared for the contested *closing*.
D is in the comparison, credited, and **flagged as not having had a self-attack pass of its own**.

**My recommendation — yours to accept or reject: B, with the ship-time retrofit attached.** Not
because it is prettiest; C's single key matches your "bookends and a squishy middle" phrasing more
closely and is the runner-up. B wins on one operational fact: **it is the only candidate that can
reach a spine already running**, via `rescope {bookend: true}` — and hand-editing `spine.json` is
forbidden here and has already caused a lease deadlock in this project. With two spines live under
this epic, a mechanism that cannot reach them is not finished. B's real cost, unhidden: forgetting
to declare fails **silently permissive** and surfaces late. Mitigation is a template lint, and
**I did not build it** — staged as a candidate.

---

## 4. The mechanism

`amend()` reads an optional per-gate `"bookend": true` through **one helper**, `_is_bookend()`.
Guards at four sites: `add` gains a **ceiling** (nothing lands after the last bookend, so a frozen
finish keeps meaning finish); `drop`, `rescope` and `retext-check` refuse a bookend gate
**regardless of status** — which is what closes the measured gap, since the old guard was
`status == "pending"` and nothing else.

**`retext-check` is covered deliberately, overriding candidate A**, and the reasoning is on the
record because A argued the other way: it could otherwise rewrite a frozen gate's `command` check
to something trivially true and pass it. **A freeze that only stops deletion is not a freeze.** The
typo case keeps two sanctioned paths — fix the template and re-instantiate, or `waive` under a
recorded authority. The g1 reviewer, told it could disagree, agreed.

`bookend` joined `rescope`'s `overwritable` tuple: **the retrofit path**, and because the guard
precedes the overwrite, a **one-way latch** — a later `rescope` unsetting it is refused.

**Bookends frozen, middle moving — demonstrated, not asserted.** A Commander standing at `plan`,
on a copy:

```
$ amend --delta '{"ops":[{"op":"add","id":"g1-implement","after":"plan",...},
                         {"op":"add","id":"g1-review","after":"g1-implement",...},
                         {"op":"add","id":"g1-integrate","after":"g1-review",...}]}'
amended: added g1-implement, added g1-review, added g1-integrate (authority commander)

items: [init, context, understand, plan, g1-implement, g1-review, g1-integrate,
        execute, reconcile, triage, review, feedback, archive]
amendments: [{ts, reason: "author g1 work gates into the middle",
              authority: "commander", ops: [added g1-implement, ...]}]
```

**That is #634's actual point working** — work gates authored into the agent's *own* spine, no
`execute.json`, no invented session id — and *"the plan changed, here's how"* falls out of the
existing `amendments` trail with **no third record invented**, per `decision:plan-change-is-legible`.

Declared: Commander `init`+`archive`, Admiral `init`+`closeout`, Explorer `init`+`route` — the
outermost two per spine and **no more**, because you asked for frozen ends and a squishy middle.
Pinned by a test asserting the **exact** flagged-id set, so a flag on the wrong gate fails rather
than passing a "something is flagged" assertion.

**The declaration form is one function.** `_is_bookend()` is the only place the key is read; no
guard site re-reads it. The reviewer verified that by grep, not by trust. **You can still pick A,
C or D cheaply.**

---

## 5. The self-hosting proof

Full transcript: `.agent-work/567-k/evidence/self-hosting-proof.md`. Fresh process, explicit paths,
`SPINE_*` and `CREW_SCRATCH_DIR` stripped, **mutating verbs against COPIES only**.

**Read-only on the live spines — exit 0 under the engine I had just patched:**

```
$ ... --file .agent-work/epic-567-door/spine.json current
LEASE active: constellation/epic-567-door (by admiral, heartbeat 2026-08-18T04:35:30...)
exit=0
$ ... --file .agent-work/567-k/spine.json current          → exit=0
```

**Mutating, on copies:**

```
[drop the frozen closing bookend]  REFUSED: drop archive: a declared bookend gate cannot be
                                   dropped, regardless of status
[grow the middle]                  amended: added g1-implement (authority proof)
[mixed legal + illegal delta]      REFUSED — and `reconcile`, the LEGAL op, did NOT land
$ git status --porcelain .agent-work/epic-567-door/     → (empty)
```

The all-or-nothing case matters because `main()` persists state even on the error path. Your work
area is untouched.

**A non-owner is refused by the lease — but the lease is not a bookend guard.** It keeps *other*
sessions out; the agent that would delete its own closing bookend is the owner and passes it by
definition. Worth stating because it is the obvious place to think the problem was already solved.

---

## 6. Suite result

**Commit `392b7917`. Clean detached worktree of the branch, not the working copy.** Run by the
engine as `g3-proof`'s own `command` postcondition, so the gate could not close unless it exited 0.

```
3383 passed, 6 skipped, 2 deselected, 1222 subtests passed in 134.70s
$ grep -c '^FAILED' /tmp/567k-suite.log
0
```

`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR`, per Inherited Context.

The 2 deselected are `MapTreeFreshnessTests`, permitted by `decision:map-index-is-admiral-owned`.
**I checked the deselection was necessary rather than assuming it** — run alone at the same sha:
`1 failed, 1 passed`, the failure being the `map/INDEX.md` freshness assertion. So the class
deselection also removed one test that would have passed; stated rather than glossed. **Nothing
else fails.**

---

## 7. Touched paths

**Written:** `scripts/checklist_engine.py`; `scripts/mcp_spine_server.py` (tool-description prose
only — all three candidates independently found the door needs no schema change);
`tests/test_checklist_engine.py`; `skills/{commander,admiral,explorer}/templates/*_SPINE.template.json`;
`docs/CHECKLIST_SCHEMA.md` (reconcile); `.agent-work/567-k/**`; this return.

**Wanted to touch and did not:**

| Path | Why not |
|---|---|
| `scripts/generate_spine.py`, `specs/*.spine.toml`, `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` | **The crew half.** Unowned by either lane — **float #1** |
| `scripts/run_crew.py`, `scripts/recover_crews.py` | Lane J's — blocks the `execute.json` migration, **float #2**; also holds a bug I found (below) |
| `map/INDEX.md` | Yours (#544). Its staleness is the one permitted suite failure |
| `current`'s rendering of the freeze | Staged — the human has not picked the declaration form |

**Correction to my own plan, mid-run:** I originally scoped `specs/` and the crew template into
gate g2. Both were wrong. `IMPLEMENTER_PLAN.template.json` **never matched my ownership pattern**
(`*SPINE*.template.json`) — my error, caught while triaging the critic. And it is **compiled** from
`specs/implementer.spine.toml` by `generate_spine.py`, whose `_compile_gate` (`:669-684`) returns a
**fixed field list with no `bookend` key**, so a hand-added declaration would have survived until
the next regeneration and then vanished. **This repo has already had that exact incident** —
`tests/test_generate_spine.py:1694-1700`, "the artifact diverged from its source". Shipping it
would have looked like a delivered feature and been a durability hole.

---

## 8. Triage candidates — **five, none filed**

Under `.agent-work/567-k/triage-candidates/`, index at `README.md`. All `recommend-and-defer`; the
`user-decision` records the **deferral**, not a filing approval. Each fails a **different** rung of
the fix-now ladder, checked honestly rather than waved off under the no-filing ruling.

1. **`current` does not render the bookend freeze** — an agent cannot see which gates are frozen
   through the projection, and reading `spine.json` to find out is itself a doctrine violation.
   **The schema doc had already predicted this**: `TaskFieldCompleteness`'s stated residual limit
   is that a template-only field is invisible to it. So the suite passing is evidence the check
   **cannot see** the field, not that it is rendered. Deferred until you pick the declaration form.
2. **Human confirmation sits in the mutable middle** — found by the g1 reviewer. Admiral's frozen
   `closeout` carries its own human-acceptance postcondition; Commander's `archive` and Explorer's
   `route` do not, so for those two the acceptance gate (`review`) is still amendable away. **The
   freeze protects a run's completion, not its acceptance.** Rigor-dial change; yours.
3. **The crew registry loses concurrent dispatches** — **measured**: three design crews dispatched
   in one loop all ran and wrote results and stdout; **only one registry entry survived**. A
   relaunched Commander running `recover_crews.py`, exactly as doctrine instructs, would be told
   two never ran and would redispatch them. `run_crew.py` is **lane J's** — route it there, that
   lane has the file open.
4. **The gauge writer overwrote its parent's reading** — your gauge file was rewritten with *my*
   session's reading (`claude-opus-5`, 4.8%). Reverted on my branch. The same writer separately
   reported `CONTEXT GAUGE SILENT` for the same ambiguity, so it has two behaviours that disagree.
5. **A template lint for an undeclared role spine** — the mitigation for B's silent-permissive
   failure mode, named in the comparison and not built.

---

## 9. Workflow feedback, including my own mistakes

**My mistakes, first:**

- **I mis-scoped my own gate plan** and would have written a file I was never granted. The critic
  reached the same place by a different road; the ownership error was mine and predates it.
- **I authored a proof gate whose postconditions were `check: null`** — the gate meant to *be* the
  empirical proof could not fail. The cold critic caught it. I replaced both with `command` checks
  **and proved they exit 1 against the pre-change tree**, because a replacement I had not falsified
  would have been the same mistake wearing better clothes.
- **I silently closed a question my own comparison called open** (`retext-check`). The critic
  caught that too. It is now an explicit decision with A's counter-argument named.
- **I got the ceiling formula wrong in my own handoff** — I wrote `max(indices) + 1`, which permits
  the append-past-`archive` case my own prose said must be refused. The implementer caught it and
  implemented the correct semantics; the reviewer re-derived the same off-by-one independently. I
  corrected the comparison so a later reader does not copy it.
- **One of my verification commands was wrong** and I reported the failure as mine rather than the
  code's: I tested "the middle still grows" with `after: plan` while `execute` was in-progress, so
  `_floor()` correctly refused it. Re-ran it properly.

**What helped:** the pre-rulings did real work — `establish-from-child-first` was the right first
question and it *did* change my scope, exactly as the order predicted. Making the crews **attack
their own candidates** produced the three convergent findings that are the most trustworthy part of
the comparison. And the **cold critic was the highest-value dispatch of the run**: two blocking
defects in my plan, plus the observation that dissolved a false dilemma I had already written down
as settled.

**What got in the way:**

- **I had to create an `execute.json` to fix `execute.json`.** The spine's `plan` step mandates it,
  so I drove a second checklist file under a session id I invented — `commander-567-k-execute` —
  off the door. That is the defect #634 names, performed by the agent fixing it. **The engine now
  supports the alternative** (demonstrated in §4); what remains is doctrine, and it is float #2.
- **The context gauge was silent for the entire run** because this session is bound to two
  candidate spines, so I judged headroom unaided — while the same writer was overwriting your gauge
  file with my reading (candidate 4).
- **`run_crew.py --verify-result` could not verify a handoff-only crew** (no `--spine`, so mtime
  alone). I verified by **re-running the crews' work myself** instead, which is stronger, but the
  documented path did not work for this dispatch shape.
- Reviewer crews wrote scratch into a **doubled path**, `.agent-work/567-k/567-k/`. Cosmetic;
  noted, not chased.

---

## 10. PR

**#635** — `feat(#634): frozen bookends, mutable middle — one spine per agent`, `main` ←
`feat/567-k-one-spine-mutable-middle`. Head **`392b79174c19964c19af187788de345060aa1461`**. Open,
`MERGEABLE`, verified against the forge rather than inferred from ancestry.

Merge position last, per the order. **Lane J is not merged** — `main` records it blocked at c6
(`c5100f9b`) — so I rebased onto current `main` (`e92e1a35`), which carries only your log entries.
**If lane J merges after this, re-verify before merging me.**

---

## What I need from you

1. **Pick the declaration form** (A / B / C / D). My recommendation is B with the ship-time
   retrofit; the convergence is yours, not mine. Everything downstream is one function.
2. **Rule on float #1 — the crew half.** `decision:every-planning-role` is `settled/human` and I
   satisfied it for Admiral, Commander and Explorer only. Crew needs `scripts/generate_spine.py` to
   carry the field through `_compile_gate`; it is in **neither lane's** grant. Roughly one line
   plus a spec key — but it is an ownership call, not mine to take.
3. **Rule on float #2 — the `execute.json` migration.** The engine now supports it. Completing it
   touches `run_crew.py` and `recover_crews.py` (lane J's) and Commander/Admiral prose in neither
   lane's grant. **Note the deadline in §3:** an Admiral can only reify its waves *before* `execute`
   starts, so this epic's own spine can no longer do it.
4. **Route triage candidate 3 to lane J now** — the crew registry silently loses concurrent
   dispatches, and lane J has that file open this wave.
