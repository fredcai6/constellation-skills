# REVIEW_RESULT — g3-review (issue #308, epic-298)

**Verdict: ACCEPT** (engine verdict `APPROVE`)

Change under review: commit `6a7dcbd` — *feat(#308): drop the 20-entry hard cap from the lessons writer (g3)*, on branch `epic-298/308` in `C:/Programs/constellation-skills-wt/e298-308`.

Survey driven through the engine at `.agent-work/issue-308/g3-review/review.json`
(lease `g3-review-rev1`, claimed as the first command, 11 checks: the 7 template items plus
`r7-cap-renamed`, `r8-test-can-fail`, `r9-grammar`, `r10-suite` appended for this context).
Fowler pass record at `.agent-work/issue-308/g3-review/fowler-pass.json`.

Interpreter: `python` throughout. `py` was never used.

---

## Headline

Both defect classes the Commander named were hunted and **neither was found**. The cap is gone
behaviourally, not just textually, and the replacement test was proven able to fail against three
separate renamed-cap mutants — none of which the gate's own grep catches.

**No blockers. Three observations and one triage candidate.**

---

## The two hunted classes

### Class 1 — a cap renamed rather than removed: **SEARCHED FOR, NOT FOUND**

I treated the gate's own check as necessary-only and proved it insufficient before relying on
anything else. All three renamed-cap mutants I built pass it cleanly:

```
$ python mutate_308_writer.py <scratch>/mut-refusal refusal
mutation refusal: APPLIED and asserted present in <scratch>/mut-refusal/scripts/apply_lessons_delta.py
  gate grep 'DEFAULT_CAP|active cap' on mutant -> NO MATCH (gate grep still passes)
```

So the sufficient condition had to be behavioural and unbounded. `probe_unbounded.py` drives the
**real** writer in-process (never the file under review — everything copies into a temp dir):

```
$ python C:/.../scratchpad/probe_unbounded.py
[PASS] A fresh file, 300 adds: active=300 expected=300 refusals=[]
[PASS] B legacy cap=20 header seeded at 20, +200 adds: active=220 expected=220 refusals=[]
[PASS] B rendered header dropped cap= | header=<!-- playbook-state: run-tick=40 dormancy-runs=10 apply-recurrences=1 apply-confirmed=3 ticked-work-ids=issue-...
[PASS] C single delta of 500 adds (rc=0): active=500 expected=500 refusals=[]
[INFO] D parsed Playbook int fields: {'run_tick': 0, 'dormancy_runs': 10, 'apply_recurrences': 1, 'apply_confirmed': 3}
[PASS] D no cap-shaped int field on Playbook: suspicious=[]

OVERALL: PASS
exit=0
```

Case B starts from the **real** 20/20 fixture whose header still carries `cap=20`. Every case asserts
`count == adds issued`, not merely `rc == 0`, so a cap implemented as **silent truncation** rather
than refusal would have surfaced too (and it does — see the `truncate` mutant below).

Case D is the sufficient-condition backstop for "under any name": the complete int field set on the
parsed `Playbook` is `{run_tick, dormancy_runs=10, apply_recurrences=1, apply_confirmed=3}`. The three
surviving thresholds are pre-existing **per-lesson maturity clocks** (apply-ripeness, dormancy),
none keyed to active-entry count. Static sweep agrees — no comparison against `len(book.active)`
survives anywhere in the writer:

```
$ grep -nEi 'cap|limit|max|threshold|throttl|len\(book\.active\)' scripts/apply_lessons_delta.py
# 12 hits: 6 are comment/preamble prose about the removal, 1 is the tolerated non-capturing
# group in STATE_RE, 4 are the pre-existing per-lesson apply-ripeness threshold, and 1 is the
# `len(book.active)` in the summary print. No comparison of len(book.active) against a limit.
```

And nothing outside the writer ever consumed the field:

```
$ git grep -nIE '\.cap\b|DEFAULT_CAP' 752a62f -- scripts skills tests | wc -l
4                       # all four inside scripts/apply_lessons_delta.py
$ git grep -nIE '\.cap\b|DEFAULT_CAP' HEAD -- scripts skills tests | wc -l
0
$ git grep -nI 'Playbook(' HEAD -- scripts tests | wc -l
1                       # one construction site
```

### Class 2 — a test passing vacuously because its refusal path was deleted: **SEARCHED FOR, NOT FOUND**

Determined **by construction**, not by observing a pass. I built three mutant *copies* of the writer
(the file under review was never modified; `git checkout` was never used), asserted each mutation
present before running, and ran the **HEAD** test module against each:

| mutant | what it reintroduces | gate grep catches it? | result |
|---|---|---|---|
| `refusal` | hard cap as `_BANK_BUDGET = 20` raising `"bank budget exhausted"` — a cap **renamed** | no | `1 failed, 69 passed` |
| `render` | `cap=20` round-tripped back into the rendered header | no | `2 failed, 68 passed` |
| `truncate` | adds past 20 silently **dropped**, `rc` stays 0 — a cap that never refuses | no | `1 failed, 69 passed` |

```
$ cd <scratch>/mut-refusal && python -m pytest tests/test_apply_lessons_delta.py -q
error: add lesson-20: bank budget exhausted
FAILED tests/test_apply_lessons_delta.py::ApplyLessonsDeltaTests::test_add_past_twenty_succeeds_and_retire_still_deletes
1 failed, 69 passed in 1.29s

$ cd <scratch>/mut-render && python -m pytest tests/test_apply_lessons_delta.py -q
E       AssertionError: 'cap=' unexpectedly found in '...run-tick=7 cap=20 dormancy-runs=10...'
FAILED ...::test_add_past_twenty_succeeds_and_retire_still_deletes
FAILED ...::test_legacy_cap_header_parses_and_is_dropped_on_render
2 failed, 68 passed in 1.32s

$ cd <scratch>/mut-truncate && python -m pytest tests/test_apply_lessons_delta.py -q
FAILED ...::test_add_past_twenty_succeeds_and_retire_still_deletes
1 failed, 69 passed in 1.28s
```

Baseline at HEAD for comparison, run by me:

```
$ python -m pytest tests/test_apply_lessons_delta.py -q
70 passed in 1.15s
```

`test_add_past_twenty_succeeds_and_retire_still_deletes` detects a **renamed** cap, a **grammar-level**
cap, and a **non-refusing** cap. It is not vacuous, and the refusal path was inverted rather than deleted.

---

## The Commander's specific uncertainty: the `playbook-state` grammar

Both halves confirmed by **running code**, not by reading the regex.

**Legacy tolerance is real.** A header carrying `cap=N` parses without raising, no cap-named
attribute survives on the parsed object, and `render_playbook` drops the field; re-parsing the
rewritten text yields the same values. Confirmed on the real corpus shape as well — the actual
`.agent-work/LESSONS.md` header (`run-tick=40 cap=20 … ticked-work-ids=<20 ids>`) round-tripped
through +200 adds and came back cap-free (probe case B above).

**The renumbering is correct.** I enumerated **all 2⁴ = 16** presence combinations of the four
optional fields (`cap` / `apply-recurrences` / `apply-confirmed` / `ticked-work-ids`), asserting each
of `run_tick` / `dormancy_runs` / `apply_recurrences` / `apply_confirmed` / `ticked_work_ids` against
**distinct** sentinels (11 / 22 / 33 / 44 / `w-alpha,w-beta`) so any swap or off-by-one is detectable,
then re-asserting after a render round-trip. The absent-optional rows — where an off-by-one would
hide — are included.

```
$ python C:/.../scratchpad/probe_grammar.py
combinations exercised: 16 (expected 16)
failures: 0
negative control (dormancy=77 must NOT read as 22): dormancy_runs=77 apply_recurrences=33 -> comparison is live: True
exit=0
```

The negative control is there because a comparison that cannot fail proves nothing: feeding
`dormancy-runs=77` reads back 77, so the assertions are live.

---

## Evidence reproduced independently

Nothing below was accepted on the implementer's word.

**`cap_is_gone.py`, red and green, in my hands.** Green at HEAD; red reproduced *without* reverting
the writer — `git show 752a62f:scripts/apply_lessons_delta.py` (plus its `agent_work_root` dependency)
staged into a scratch root, and the check run there:

```
$ cd <scratch>/pre && python .agent-work/issue-308/checks/cap_is_gone.py
FAIL: the cap still refuses the add at 20 entries:
error: add cap-removal-behavioural-check: active cap 20 reached — retire before adding
exit=1

$ cd C:/Programs/constellation-skills-wt/e298-308 && python .agent-work/issue-308/checks/cap_is_gone.py
PASS: add accepted at 20 active entries — the cap is gone
exit=0
```

The fixture is asserted at the cap (`grep -c '^### lesson:' .agent-work/issue-308/fixtures/LESSONS-at-cap.md` → `20`),
and the check re-asserts `n >= 20` itself before running, so it cannot pass over an empty set.

**Full suite, counts I observed:**

```
$ python -m pytest -q
1621 passed, 2 skipped, 543 subtests passed in 414.22s (0:06:54)
exit code 0
```

Identical to the implementer's claimed counts — reproduced, not asserted.

**Scope, derived by command:**

```
$ git show HEAD --name-only --format="" | grep -v '^\.agent-work/'
scripts/apply_lessons_delta.py
skills/workbench/templates/LESSONS.template.md
tests/test_apply_lessons_delta.py
count=3
```

Exactly the allowed set. All named exclusions verified untouched by `HEAD`:
`.agent-work/LESSONS.md` (still 20 active, still `cap=20` — g4's job),
`skills/lessons-auditor/SKILL.md`, `docs/EPISODE_STORE.md`.

---

## Findings

No blockers.

### Observations (non-blocking)

**O1 — `primitive-obsession` (Fowler): the grammar is parsed by positional group index.**
`STATE_RE` (`scripts/apply_lessons_delta.py:51-55`) is consumed as `state.group(1..5)` in
`load_playbook:236-241`. This diff had to hand-renumber five indices (`group(2..6)` → `group(2..5)`)
purely because one group changed capture-ness — and an off-by-one there would have silently swapped
two integers rather than raising. Python's `re` supports named groups
(`(?P<dormancy_runs>\d+)` / `state.group("dormancy_runs")`), which makes that entire failure class
impossible and would have reduced this edit to deleting one group. The renumbering **as landed is
correct** (16/16 combinations verified); the finding is about the next such edit, not this one.

```
$ grep -n "state.group" scripts/apply_lessons_delta.py
```

**O2 — `duplicated-code` (Fowler): the lessons preamble is twinned.**
`_default_preamble()` (`scripts/apply_lessons_delta.py:140-164`) and
`skills/workbench/templates/LESSONS.template.md` are two hand-maintained copies of the same
retention story. Both had to be edited here, and they now state it in **different words** with
nothing checking them against each other. Kept in sync correctly this time (verified: neither
renders a `cap=` header).

**O3 — `shotgun-surgery` (Fowler): one concept, many hand-maintained sites.**
"There is no cap" required edits at 8 sites in the writer, the writer's own preamble prose, the
workbench template, and **6 raw `playbook-state` header string literals** in
`tests/test_apply_lessons_delta.py` that each spelled `cap=20` inline. Every site was in fact caught
(`git grep -nIE '\.cap\b|DEFAULT_CAP' -- scripts skills tests` → `0` at HEAD vs `4` at `752a62f`).
Related to O1: the fixtures duplicate the grammar's shape rather than building it from the writer's
own renderer.

**O4 — test-corpus note.** Migrating those 6 fixtures to drop `cap=20` means the legacy-tolerance
path is now exercised by exactly **one** test (`test_legacy_cap_header_parses_and_is_dropped_on_render`)
rather than incidentally by many. Adequate — and I independently covered all 16 combinations — but
the tolerance rests on a single test in-repo.

**O5 — commit hygiene, sanctioned by the handoff.** The commit also lands 468 lines of **g4**
migration code (`.agent-work/issue-308/build_migration_delta.py`, `migration_records.py`) alongside
the g3 change. The handoff explicitly scopes `.agent-work/issue-308*` out of review, so this is noted,
not charged.

### Triage candidate

**TC1 — `docs/RECURSIVE_IMPROVEMENT_DESIGN.md:402, 414-415` still describes the apply script as
enforcing a hard cap** ("enforcing cap"; "hard cap (start 15–20, enforced by the apply script);
retire-before-add beyond the cap"). This file was **not** in the handoff's enumerated out-of-scope
list (which named only `skills/lessons-auditor/SKILL.md` and `docs/EPISODE_STORE.md`), so it is
unclaimed residue after #308. Flagged to the engine as `tc1`.

---

## Fowler refactoring pass

Record: `.agent-work/issue-308/g3-review/fowler-pass.json`.

```
$ python C:/Users/fredc/.claude/skills/constellation-reviewer/scripts/verify_fowler_pass.py \
    .agent-work/issue-308/g3-review/fowler-pass.json
fowler pass ok: ... (smells=12, flagged=['duplicated-code', 'primitive-obsession', 'shotgun-surgery'],
                     overridden=['long-method', 'comments-as-deodorant'])
rail_exit=0
```

All 12 baseline smells visited. Two overrides, each with a named documented standard and a reason:

- **`long-method` — overridden.** `apply_delta()` is **220 lines** (ast-measured,
  `scripts/apply_lessons_delta.py:425-644`). Standard: `global-crew.md` — *"Make the minimal change
  that satisfies the handoff; no speculative abstraction"*, reinforced by the g3 handoff's surgical
  scope. Reason: the smell is pre-existing and the diff **shrinks** the method by 4 lines;
  decomposing it here would be unrequested refactoring that enlarges the diff a reviewer must reason
  about for the cap question.
- **`comments-as-deodorant` — overridden.** A 5-line comment on a 1-line regex
  (`apply_lessons_delta.py:46-50`). Standard: `global-crew.md` — *"Match the surrounding code's
  naming, labeling, and in-file documentation conventions"*; the file's convention is exactly this
  (`TICKED_WORK_ID_RETENTION:40-43` carries a 4-line why-comment on one constant). Reason: it records
  **why** the group must stay non-capturing — an intent the code cannot express and that the next
  editor would otherwise "fix" into a capture group. That is a decision record, not a deodorant.

The rail was itself red-proved, since a rail that cannot refuse proves nothing:

```
$ python verify_fowler_pass.py fowler-ctl-dropped.json     # feature-envy removed
REFUSED: the Fowler pass skipped baseline smell(s) ['feature-envy'] — ...
exit=1
$ python verify_fowler_pass.py fowler-ctl-unlogged.json    # long-method override block stripped
REFUSED: OVERRIDE-LOG: smell 'long-method' is overridden with no override block — ...
exit=1
```

---

## Map impact

Verified against the diff and the evidence, and it holds. The change is confined to one module with a
**single** construction site and **zero** external consumers of the removed field. No caller-visible
interface changed shape: the CLI, the delta schema and the file format are unchanged except that one
header field is now tolerated-and-dropped instead of required. `docs/CONSTELLATION_OVERVIEW.md:104`
already carries the removal rationale (landed earlier in this epic by `1dd83a1`), so the recorded
architecture and the code agree. Nothing here requires Commander reconciliation.

---

## What I did NOT test (scoped null)

- The **g4 migration** of `.agent-work/LESSONS.md` itself, and the `build_migration_delta.py` /
  `migration_records.py` that landed in this commit — out of scope per the handoff.
- The lessons **read** path (launch orders, spine templates) — gate g5.
- CI. Per `docs/agents/CREW_CONTEXT.md`, neither local interpreter reproduces CI, so a local green is
  evidence, never the gate. My suite run is `python` 3.14.x, not CI's 3.12 pin.
- Concurrent/multi-writer behaviour of the writer, and playbooks whose header places `cap=` in a
  **different position** than the legacy corpus does (e.g. after `dormancy-runs`). The regex would
  reject those; no such file exists in the repo, so this is a hypothetical, not a defect.

---

## Workflow Feedback

- **The handoff was unusually good on the one thing that matters here:** it named the two defect
  classes *and* pre-emptively told me the gate's own grep was necessary-but-not-sufficient. That
  single sentence is what pushed me to build the three renamed-cap mutants instead of trusting a
  green grep. Worth keeping as a handoff-template field.
- **Gap: the handoff gave no "Survey State Location".** The reviewer SKILL specifies
  `.agent-work/<work-id>/<gate>-review/review.json`; I improvised `issue-308/g3-review/review.json`
  from that. If the Commander expects a specific path for closeout, it should say so.
- **Gap: `docs/agents/engine-config.json` does not exist in this worktree**, though the survey
  template's `config_ref` points at it (`docs/agents/` holds only `CREW_CONTEXT.md` and
  `ORCHESTRATOR_CONTEXT.md`). The engine tolerated the dangling ref silently — so the rework cap and
  rigor settings came from defaults, not from project config, and nothing said so. Worth a visible
  warning, or worth creating the file.
- **Engine friction:** setting the survey's `work_id` to `issue-308-g3-review` made the engine create
  a sidecar tree at `.agent-work/issue-308/issue-308-g3-review/{context,mechanical}/`, which reads as
  orphan untracked scratch next to the survey itself at `.agent-work/issue-308/g3-review/`. Two
  directories for one review is confusing at closeout; the sidecar should live under the survey's own
  directory.
- **No blockers on the handoff itself.** The instruction not to `git checkout` the writer for the red
  arm was correct and load-bearing — it is what let me red-prove three separate mutants without ever
  putting the file under review at risk.
