# Implementer Handoff — g2-implement REWORK (attempt 2)

## This is a REWORK, not a fresh build

`g2-implement` was **complete**; I reopened it after `g2-review` returned **BLOCK**. The
composer you (or your predecessor) built is **good work and is staying** — 6 of 7 independent
call-site mutations were caught, all eleven fields traced to real engine state, and the wiring
was proven **not** ceremonial. Do **not** redesign it.

**Read the review first — it is the authority on what is wrong:**
`.agent-work/issue-305/crew/g2-review-result.md` (351 lines; §1, §2, and §3's
`refusals` subsection are the ones that generate work).

Your predecessor's own result — `.agent-work/issue-305/crew/g2-implement-result.md` — has the
build context. `constellation-implementer` has no sanctioned resume path; treat this handoff as
your plan input and proceed. Do not re-plan the whole gate.

## Where things stand

- Branch `epic-298/305`, worktree `C:/Programs/constellation-skills-wt/e298-305`, all committed.
- Suite baseline: **1470 passed / 2 skipped / 472 subtests** (`python -m pytest -q`, ~70s).
- The g2 implementer's commit is `baf9f16`. `git diff baf9f16~1..baf9f16 -- scripts/ tests/ docs/`.

---

# THE FOUR TASKS

## TASK 1 — `reopens`: take fix shape **B**. **This is ADJUDICATED; it is not your call.**

**The defect** (proven; one command, exits 1 today and 0 when fixed):

```
python .agent-work/issue-305/evidence/hunt1_reopens_overcount.py
```

`reopen()`'s escalation branch (`checklist_engine.py:1870-1879`) returns a normal string
**without** incrementing `rework_count`, does **not** raise — so `main()` takes the success path
(`:2634`) and `reopen` is in `MUTATING_VERBS`, so it is journalled as a `reopen` **anyway**.
`journal_reopens()` counts it, `_rework_total()` does not, and `reopen_total()`'s `max(...)`
takes the **over-counting** witness. A run with exactly ONE reopen emits `"reopens": 2`.

**THE FIX — shape B: `reopen_total()` uses `_rework_total()` alone. Delete the journal
witness.** That means removing `journal_reopens()` **and** `find_spine_path()` (~60 lines) and
the now-dead `spine_path` plumbing through `mechanical_fields()`, plus any tests that exist only
to exercise them.

**Why B and not "subtract the escalations" (which also works arithmetically):** subtracting
requires string-matching engine-authored, human-readable blocker text *from
`episode_capture.py`* — a new cross-module coupling in the module explicitly ruled not to change
engine behaviour, which silently regresses the moment someone rewords the message. **B removes
the class; the alternative fixes the instance.** B also deletes an untested silent-`None`
disambiguation branch (see TASK 4's note).

**B's honest cost, which you must DOCUMENT rather than hide:** it loses the
`amend`-drops-a-gate recovery the `max` existed for, so `reopens` can now **under**-count on
that narrow path. That is acceptable and deliberate — **under-counting is the direction this
field's doctrine already concedes; over-counting fabricates.** Say exactly that in the docstring.

**The gate's own imperative still says "reopens from the journal's reopen entries." That
instruction is now SUPERSEDED by this ruling** — it was written before the defect was known.
The engine text will not update; this handoff wins.

**CONSTRAINT: the fix must live entirely in `episode_capture.py`.** The engine diff is ruled
**zero logic** (import shim, two call lines, `base_dir` threading). Do **not** change how
`reopen()` or `main()` journal.

## TASK 2 — the discriminating test. **THIS IS THE REAL DELIVERABLE, not TASK 1's arithmetic.**

The reviewer's mutation **M5 SURVIVED**: replacing the entire two-witness `max` with
`_rework_total` alone left **all 63 episode tests green**. The reconciliation has **no test that
discriminates it**. So whichever way `reopen_total` is written, it currently sits on
**unconstrained** code — and your fix would land there too, unprotected against being silently
reverted.

**Ship a test that FAILS on the pre-fix behaviour.** The bar, stated exactly:

- It must **fail** against the old `max(journal, rework)` implementation and **pass** against
  yours. **Prove both halves.** Do not assert this — demonstrate it: temporarily restore the old
  expression, show the test red, restore yours, show it green, and **paste both outputs** in
  your result. A test that passes both ways is worth nothing here and is exactly what M5 exposed.
- It must reach the failing condition through a **real escalated reopen**, not by hand-editing a
  journal. The repro script above shows the reachable route; `skip` is the **only** continuation
  after a rework-cap escalation (`resume` refuses by design at `:1811-1817`, `reopen` refuses a
  blocked gate, `start` refuses because `active_id()` keeps returning the blocked gate).
- **Cover BOTH seams.** The reviewer measured that the over-count is `E` at a **`start`** seam
  but `E−1` at a **`reopen`** seam — the in-flight verb's own journal line is not yet written, so
  a single escalation is exactly **cancelled** at a `reopen` seam. A test that only exercises the
  `reopen` seam **passes on the broken code**. This is the same shape as the `project` defect that
  shipped because it was only tested in a plain checkout.

`.agent-work/issue-305/evidence/hunt1_reopens_overcount.py` is a working, committed reference for
driving a fixture through the real CLI to an escalation. Reuse its approach; it is not itself a
pytest test.

## TASK 3 — correct the falsified invariant wherever it is still asserted in prose

**A wrong comment is a correctness defect, not a nit** — and this is the very invariant this gate
falsified. Both of these still claim it:

1. `scripts/episode_capture.py:365-369` — *"Both can only ever UNDER-count ... Neither can
   over-count."*
2. `tests/test_episode_capture.py`, `test_a_missing_journal_is_covered_by_the_second_witness`'s
   docstring — same claim.

Replace with what is now **measured**: the journal witness **can** over-count, because an
escalated `reopen` journals as a successful `reopen` without incrementing `rework_count`. If fix
B removes the code these describe, the prose goes with it — but **check both sites**, do not
assume deletion covers them.

## TASK 4 — `docs/CHECKLIST_SCHEMA.md`: three corrections

The schema doc was an explicit **condition** of the `refusals` counter being in scope, so a stale
doc is a shipped defect here. All three are measured, not inferred:

1. It says the counter *"is written by the CLI boundary alone, never by a verb function"* — but
   the arming write `cl.setdefault("refusals", 0)` is **inside `claim()`, a verb function**. The
   doc contradicts itself one bullet later ("Armed by `claim`"). Fix the claim, not the code —
   the arming placement is **correct** (it sits after `claim`'s idempotent-resume early return,
   so a same-session re-claim cannot backdate a `0` over real refusals).
2. It justifies run-scoping by citing *"an unknown item id, a lease conflict, **a malformed
   verb**"* — but a malformed verb **exits through argparse with code 2 before the checklist is
   ever loaded**, so it is never counted. Measured: `checklist_engine.py frobnicate a` → exit 2,
   counter unmoved. Drop or correct that example.
3. **"run-scoped" must become "checklist-scoped"**, with the caveat stated plainly. Measured: a
   **foreign** session's lease-conflict refusal increments the owning run's tally
   (`start b --session-id SOMEONE-ELSE` → `refusals: 1 → 2`). Make the same correction to the
   composer comment at `scripts/episode_capture.py:452-455`, which also asserts "run-scoped".

**ADJUDICATED — do NOT change the counting semantics.** I ruled this a **documentation** fix, not
a code fix: the number is honest once it is labelled honestly, and a session-filter guard would
introduce a *new* under-count (refusals where `--session-id` was forgotten while a lease is held
are genuinely this run's) that deserves its own design pass rather than a rushed guard inside a
closing gate. I have filed the attribution question as a follow-up issue. **If you disagree, say
so in your result and proceed with the doc fix anyway** — do not implement the guard.

---

## Out of scope — do NOT do these

- **Do not** touch the seam placement, the episode-store location, `#327`, `#362`, or `#359`.
- **Do not** redesign the eleven-field group — `constraint:frozen-field-group`, it is not yours
  to redesign.
- **Do not** implement session-filtered refusal counting (TASK 4).
- **The shotgun-surgery finding** (the field group spelled out in five places with no mechanism
  that fails when one is missed) is **filed as a follow-up, not fixed here** — it is latent while
  the group is frozen.
- `find_spine_path`'s untested multi-match branch: **moot if you take B**, because the function
  goes away. If for some reason it survives, tell me — do not paper it over.

## Gate Anchors (verbatim from the plan)

```
structural:
  struct:episode_capture.mechanical_fields — the composer
  struct:apply_episode_delta._validate_create — :866, the frozen allowlist this feeds
  struct:query_episodes._FIELD_READERS — :240, the eleven fields, frozen
capability:
  capability:mechanical-capture — the deliverable
constraint:
  constraint:frozen-field-group — the group is not mine to redesign
decision:
  decision:zero-agent-effort-is-literal — a field an agent can omit by forgetting is not
    mechanically captured  @grade: settled/human
  decision:episode-store-is-301s — write into episodes/active/ as shipped; no second store
    @grade: settled/inherited
  decision:refuse-never-fabricate — a field that cannot be honestly sourced REFUSES rather
    than emitting a silent 0. This is the doctrine TASK 1 is a breach of.
```

## Standing Constraints

- **`python -m pytest`, not `py`.** `py` is 3.12.13 (CI's pin) but has **no pytest**; `python` is
  3.14.3 with pytest 9.0.2. **Neither reproduces CI** — a local green is never the gate.
  `Path.read_text(newline=...)` is **3.13+** and will fail CI; `Path.write_text(newline=...)` is
  3.10+ and is safe. This cost PR #320 thirty-nine failures.
- **Windows:** explicit `encoding='utf-8', newline='\n'` on every write.
- Compare **normalized content or git blob OIDs, never raw working-tree bytes** (#319).
- **Do not touch `C:/Programs/constellation-skills`** (the main checkout) or any sibling worktree.
- Edit canonical `skills/_shared/global-*.md`, **never** the `skills/<role>/references/` copies.
- `--finding` text with backticks is shell-mangled and silently drops words.

## Protocol if something here proves wrong

**Tell me (the Commander) in your result, and PROCEED with the rest.** Do not stop the gate and do
not silently re-scope. **If the code contradicts this handoff, the code wins — say so.** Two
handoffs earlier in this run carried errors that cost a crew a cycle each, and both were things a
Commander asserted rather than measured. TASK 1's defect and TASK 4's three items are **measured**;
TASK 2's both-seams claim is the reviewer's measurement, not mine.

## Return Shape

Write your result to **`.agent-work/issue-305/crew/g2-implement-rework-result.md`**:

1. TASK 1 — the fix, and the repro script now exiting **0**.
2. TASK 2 — the discriminating test, with **both** pasted outputs (red on old, green on new) and
   confirmation it covers **both** seams.
3. TASK 3 — both prose sites, before/after.
4. TASK 4 — the three doc corrections; say if you disagreed with the adjudication.
5. Full suite via `python -m pytest`, with the delta from 1470/2/472 explained.
6. Anything you deviated on, and why.
