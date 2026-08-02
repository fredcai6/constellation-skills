# Implementer Result — g2-implement REWORK (attempt 2)

**Return status: `complete`.** All four tasks landed. Nothing committed — Commander integrates.

Crew id `constellation/issue-305/g2-implement/implementer/attempt-2`. Plan driven through the
engine at `.agent-work/issue-305/crew/g2-implement-rework-plan.json` (6 items, all complete,
lease `impl-305-rework-2`). Composer NOT redesigned, per instruction.

**Files changed:** `scripts/episode_capture.py`, `tests/test_episode_fields.py`,
`docs/CHECKLIST_SCHEMA.md`. Engine untouched.

```
 docs/CHECKLIST_SCHEMA.md     |  11 +-
 scripts/episode_capture.py   | 139 ++++++++----------------
 tests/test_episode_fields.py | 200 +++++++++++++++++++++++++++++++----
```

---

## 1. TASK 1 — fix shape B, and the repro now exiting 0

**Landed entirely inside `scripts/episode_capture.py`.** `reopen()` and `main()` are untouched;
`git status` shows no `scripts/checklist_engine.py`.

- `reopen_total(checklist)` — signature lost its `spine_path` parameter and now *is* the rework
  witness: it sums each task's `rework_count` directly. `_rework_total()` was folded into it
  rather than left as a one-line indirection, so there is exactly one function and one name.
- **Deleted:** `journal_reopens()` (~29 lines), `find_spine_path()` (~29 lines, including the
  untested multi-match silent-`None` branch the reviewer flagged — it is gone, as B predicted,
  so triage item 2 is moot), and the `spine_path=` parameter on `mechanical_fields()` plus its
  one call site. Net −139/+? on the module; the composer shed 84 lines.
- **The cost is documented, not hidden.** The new docstring says, verbatim:
  *"**The cost, stated rather than hidden: this can now UNDER-count.** An `amend` that drops a
  `pending` gate carrying `rework_count > 0` takes its reopens with it, and that is the recovery
  the second witness existed for. It is accepted deliberately — under-counting is the direction
  this field's doctrine already concedes, and over-counting fabricates."*

**The repro, exiting 0:**

```
$ python .agent-work/issue-305/evidence/hunt1_reopens_overcount.py
  $ reopen a --reason -> ESCALATED a: rework cap 1 reached; blocked and bubbled to parent (not reopened)
  $ skip a --reason   -> a -> skipped because escalation resolved by parent: OBE
  $ start b --session-id -> b -> in-progress

  journal `reopen` lines      : 2
  total rework_count          : 1
  TRUE reopens (ground truth) : 1   <- the 2nd ESCALATED, 'not reopened'
  SHIPPED `reopens` in b.json : 1

PASS - `reopens` matches ground truth. The defect is FIXED.
EXIT=0
```

The gate's own imperative ("reopens from the journal's reopen entries") is superseded by the
handoff's ruling, as instructed.

---

## 2. TASK 2 — the discriminating test **(the real deliverable)**

`tests/test_episode_fields.py::EscalatedReopenIsNotAReopenTests`, two methods, both driving a
real fixture through the real CLI as subprocesses. **No journal is hand-edited anywhere**; the
escalation is reached the only way it can be, and `skip` is the only continuation past a
cap-escalated gate. Each test also asserts that the fixture *still reproduces the divergence*
(journal lines vs. rework total), so it cannot go quietly green on a run where the two witnesses
happen to agree.

### RED — against the shipped `max(journal_reopens, _rework_total)`

```
$ python -m pytest tests/test_episode_fields.py -k EscalatedReopen -q
>       self.assertEqual(self.snapshot("b")["mechanical"]["reopens"], 1)
E       AssertionError: 2 != 1
tests\test_episode_fields.py:538: AssertionError

>       self.assertEqual(self.snapshot("c")["mechanical"]["reopens"], 3)
E       AssertionError: 4 != 3
tests\test_episode_fields.py:562: AssertionError

FAILED tests/test_episode_fields.py::EscalatedReopenIsNotAReopenTests::test_an_escalation_does_not_inflate_reopens_at_a_start_seam
FAILED tests/test_episode_fields.py::EscalatedReopenIsNotAReopenTests::test_escalations_do_not_inflate_reopens_at_a_reopen_seam
2 failed, 34 deselected in 3.45s
```

Note the *shape* of the two failures — they are the reviewer's table, measured:
`start` seam inflates by `E` (2 vs 1, `E=1`); `reopen` seam inflates by `E−1` (4 vs 3, `E=2`).

### GREEN — against fix B

```
$ python -m pytest tests/test_episode_fields.py tests/test_episode_capture.py -q
.................................................................        [100%]
65 passed in 16.21s
```

(63 before, +2 new.) The engine also ran this as `m2-fixb.c1`'s command check and advanced.

### Both seams are covered, and the second one is the load-bearing half

| test | seam | gates | `T` | `E` | journal at emit | asserts |
|---|---|---|---|---|---|---|
| `..._at_a_start_seam` | `start b` | a, b | 1 | 1 | 2 | `reopens == 1` |
| `..._at_a_reopen_seam` | `reopen c` | a, b, c | 3 | 2 | 4 | `reopens == 3` |

The reopen-seam case deliberately uses **two** escalations. With `E=1` the missing in-flight
journal line cancels the inflation exactly (`T+E−1 == T`) and a reopen-only test would have
passed on the broken code — that trap is written into the test's own docstring so nobody
"simplifies" it back to one escalation later.

**M5 is now dead.** The mutation that survived review (`reopens = _rework_total(checklist)`) is
literally the shipped implementation, and the inverse mutation — restoring the journal witness
and the `max` — is what produced the RED output above.

---

## 3. TASK 3 — the falsified invariant, both sites

I checked both sites rather than assuming deletion covered them, and swept the whole repo
(`grep -rni "over-count|under-count|two witnesses|second witness" scripts/ tests/ docs/ skills/`)
for a third. There is no third.

**Site 1 — `scripts/episode_capture.py`, `reopen_total`'s docstring.** Was:

> *"Both can only ever UNDER-count ... Neither can over-count. So the larger reading is the
> best-corroborated one and is never a guess."*

Now names the mechanism instead of asserting the invariant:

> *"An earlier version of this field took `max(journal_reopen_lines, rework_total)`, resting on
> the claim that both witnesses could only ever UNDER-count. **That claim is false.** `reopen()`'s
> rework-cap branch blocks the gate and bubbles it to the parent WITHOUT incrementing
> `rework_count`, and it returns an ordinary string rather than raising — so `main()` takes the
> success path and, because `reopen` is a `MUTATING_VERB`, journals a `reopen` line for a reopen
> its own message says did not happen. ... a run with ONE real reopen emitted `"reopens": 2`.
> ... `rework_count` cannot over-count: the same branch that fabricates a journal line pointedly
> leaves it alone."*

**Site 2 — `tests/test_episode_fields.py`.** The handoff placed this in
`tests/test_episode_capture.py`; **the code contradicts the handoff and the code wins** — it is
`tests/test_episode_fields.py:383`, `ReopensFieldTests`. Two docstrings there asserted it, not
one:

- The **class** docstring said *"`reopens` comes from the JOURNAL"* — which fix B makes flatly
  false, and which the handoff did not list. Now: *"`reopens` sums the tasks' own `rework_count`
  ... The journal sidecar over-counts too, for a subtler reason — see
  `EscalatedReopenIsNotAReopenTests`, which is the test that killed it."*
- `test_a_missing_journal_is_covered_by_the_second_witness` → renamed
  `test_the_journal_sidecar_is_not_consulted_at_all`, docstring corrected. It is **kept, not
  deleted**: under B, unlinking the sidecar and finding `reopens` unmoved at a real non-zero
  value pins that the journal witness has not crept back in.
- `test_reopens_is_refused_only_when_no_witness_can_be_read` → renamed
  `..._when_the_witness_cannot_be_read` (there is one witness now), calls updated to the
  one-argument signature.

---

## 4. TASK 4 — the three schema-doc corrections

**I did not disagree with the adjudication.** I did not implement session-filtered counting; the
counting semantics are byte-identical. I re-measured all three claims myself before writing
rather than transcribing them, and all three held:

```
  exit=0 refusals=0  <- claim --session-id own
  exit=0 refusals=0  <- start a --session-id own
  exit=2 refusals=0  <- frobnicate a          (malformed verb: argparse, before the load)
  exit=1 refusals=1  <- start b --session-id SOMEONE-ELSE   (foreign session moves the tally)
```

and `setdefault("refusals", 0)` is at `checklist_engine.py:964`, inside `claim()` which opens at
`:894` — confirmed by walking back to the enclosing `def`, not by eye.

1. **"written by the CLI boundary alone, never by a verb function"** → *"Every **increment**
   happens at the CLI boundary — no verb function counts a refusal — while the initial arming
   write (`cl.setdefault("refusals", 0)`) sits inside `claim()`, deliberately."* The
   self-contradiction with the next bullet is gone, and that bullet now carries the *reason* the
   placement is correct (after `claim`'s idempotent-resume early return, so a same-session
   re-claim cannot backdate a `0` over real refusals).
2. **"a malformed verb"** dropped from the justification list, and replaced by an explicit
   statement of why it is absent: *"argparse exits `2` before the checklist is ever loaded, so it
   is never counted."* Recording it as a non-example is worth more than silently deleting it.
3. **"run-scoped" → "checklist-scoped"** in the field comment at `:45`, the section heading, the
   opening sentence, and the bullet — plus a new bullet stating the caveat plainly with the
   measured transcript, and naming why filtering is deferred rather than forgotten. The same
   correction is made to the composer comment (`episode_capture.py`, the `refusals` block), which
   now says *"CHECKLIST-scoped ... a teammate's stale-lease retry takes a lease conflict and
   increments this run's tally."*

I deliberately did **not** leave the dead phrase "run-scoped" standing in the corrected prose as
a changelog of its own error — this is user-facing schema documentation, so it states the correct
scope plainly.

---

## 5. Full suite

```
$ cd C:/Programs/constellation-skills-wt/e298-305 && python -m pytest -q
1472 passed, 2 skipped, 472 subtests passed in 87.95s (0:01:27)
```

**Delta from the 1470 / 2 / 472 baseline: `+2 passed`, nothing else.** Those two are exactly the
new `EscalatedReopenIsNotAReopenTests` methods. No test was deleted — the four tests touched were
renamed and/or re-docstringed in place, so the count does not move on their account. Skips and
subtests unchanged.

**CI-pin hazard checked directly, not assumed.**

- `grep -n "read_text([^)]*newline=" scripts/episode_capture.py tests/test_episode_fields.py` →
  **none**. (The repo-wide hits are all prose warnings *about* the kwarg in files I did not
  touch.) Every write I made is `encoding='utf-8', newline='\n'`.
- Both changed `.py` files `py_compile` cleanly under `py` = **3.12.13**, the CI pin.
- A local green is not the gate; this is the hazard check, not a claim CI will pass.

---

## 6. Deviations, and one handoff error

- **Handoff error (code wins, as instructed).** The handoff locates
  `test_a_missing_journal_is_covered_by_the_second_witness` in `tests/test_episode_capture.py`.
  It is in **`tests/test_episode_fields.py:383`**. Immaterial to the work, reported per protocol.
- **TASK 3 had a third prose site the handoff did not name** — `ReopensFieldTests`'s **class**
  docstring, *"`reopens` comes from the JOURNAL"*, which fix B falsifies outright. This is why
  "check both sites, do not assume deletion covers them" was the right instruction; I extended it
  to a repo-wide sweep and fixed three, not two.
- **`_rework_total()` was folded into `reopen_total()`** rather than kept as a private helper.
  The handoff says "`reopen_total()` uses `_rework_total()` alone"; with one witness left, two
  names for one sum is indirection with no reader. Behaviour is identical, the public name is
  unchanged, and no test referenced `_rework_total`. Flagging it because it is a shape choice
  the handoff's literal wording did not make.
- **Nothing else.** I did not touch the seam placement, the episode store, the eleven-field
  group, `#327`/`#362`/`#359`, the engine, the main checkout, or any sibling worktree. Nothing
  is committed.

---

## Map Impact

- **Structural anchors touched:** `struct:episode_capture.mechanical_fields` — lost its
  `spine_path` parameter; the module lost `find_spine_path` and `journal_reopens` entirely.
  `reopen_total` is now a pure function of the checklist, with no filesystem dependency at all.
- **Capabilities affected:** `capability:mechanical-capture` — `reopens` no longer fabricates on
  an escalated reopen. Behaviour changed: **yes**, and only for that field.
- **Constraints honored:** `constraint:frozen-field-group` — the group is unchanged, eleven
  fields in, eleven out. The fix stayed inside `episode_capture.py`.
- **Decisions:** `decision:refuse-never-fabricate` — this was the breach; it is closed, with the
  residual under-count named in the docstring rather than left to be discovered.
- **Claims/evidence produced:** the two-witness reconciliation now has a discriminating test at
  both seams; the surviving mutation M5 is dead by construction.
- **Triage candidates:** reviewer's item 2 (`find_spine_path`'s untested multi-match branch) is
  **resolved by deletion**, not deferred. Item 1 (refusal attribution) is documented here and
  filed by the Commander as `#367`. Item 3 (shotgun surgery on the field group) is untouched and
  still latent.

## Workflow Feedback

- **Handoff gaps:** one wrong file path (TASK 3 site 2, above), and TASK 3 named two prose sites
  where there are three. Both were cheap to find *because* the handoff told me to check rather
  than assume — that instruction earned its keep.
- **Context rediscovered:** none material. The handoff's "read the review §1, §2, §3-refusals"
  pointer was exact, and the committed `hunt1_reopens_overcount.py` saved me building a fixture
  driver from scratch — it is the single highest-leverage artifact in this gate.
- **Instructions improvised around:** `constellation-implementer` has **no sanctioned resume or
  rework path** — it opens by telling you to build a plan and claim a lease as your first
  command, which is exactly wrong for an attempt-2 that must not re-plan. The dispatch had to
  override the skill in prose ("your handoff IS your plan input"). This is the third rework in
  this epic to hit it. A `rework` clause in the skill — *inherit the prior plan's gate anchors,
  cut items only for the named defects* — would remove a per-dispatch workaround.
- **What would have made this easier:** the plan template's postcondition `check` field invites
  a shell/regex "absence of bad string" check for prose tasks, and mine (`m4`) nearly failed on
  its own corrected text because the correction has to *mention* the phrase it retires. A note in
  the template that prose postconditions are usually better as `check: null` manual attests
  would have saved a reword.
