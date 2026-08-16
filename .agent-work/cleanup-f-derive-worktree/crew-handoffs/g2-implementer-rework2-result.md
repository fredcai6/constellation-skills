# Implementation Result — g2, reworks 1 and 2 as one gate result

Written by `constellation/cleanup-f-derive-worktree/g2/implementer/attempt-3`.

**What is mine and what is not.** Rework 2 (everything under "Rework 2" below) I
performed and measured in this session. Rework 1's code and prose were landed by
the attempt-2 implementer, which died before writing its result; I reconstructed
its half from its surviving evidence under `g2-implement-rework/` and from the
diff, and I say against each item whether I re-ran it or am reporting its
measurement. **Nothing in the "reconstructed" column is presented as my own
measurement.** One piece of rework 1 was *not* finished by that crew and I
completed it here (its C4 — see "Rework 1, the unfinished half").

## Assigned gate

`g2`, rework 2 — delete the engine-side worktree derivation
(`ADMIRAL_RULING-2` N2, road 1), and write the gate's missing result.

## Completed slice

**(A)** `checklist_engine.worktree_from_spine_path` and the `AGENT_WORK_DIR`
constant it was the only user of are deleted. The engine now has no location
logic at all — neither ambient nor derived. The case table in
`tests/test_worktree_derivation.py` survives whole, re-scoped to the one live
implementation, `spine_rail._worktree_from_spine`. Every prose claim that the
engine derives a worktree is repaired in the three copies that hold it, and the
one assertion that depended on the deleted symbol has a new positive anchor.

**(B)** This result, covering both reworks.

## Scope

**Files changed (committed):**

- `scripts/checklist_engine.py` — the derivation and the constant deleted; module
  header repaired. **81 lines changed: 68 removed, 13 added, all 13 comments.**
- `tests/test_worktree_derivation.py` — re-scoped to the hook; module docstring
  rewritten; `test_the_two_copies_agree` removed.
- `tests/test_spine_origin_isolation.py` — module docstring repaired; the stale
  assertion replaced with a new anchor; the test renamed.
- `docs/CHECKLIST_SCHEMA.md` — the same repair.
- `map/INDEX.md` — regenerated, never hand-edited.

**Files changed (work area, for the Commander to commit):**

- `.agent-work/cleanup-f-derive-worktree/crew-handoffs/g2-implementer-result.md`
  — rework 1's C4 amendment, which its own implementer never reached.
- `.agent-work/cleanup-f-derive-worktree/g2-implement-rework2/**` — this run's
  plan, checks and evidence.

**Specific exclusions touched:** no. `scripts/hooks/spine_rail.py`,
`tests/test_spine_rail.py`, `scripts/verify_worktree_isolation.py`,
`scripts/run_crew.py`, lane A's and lane E's files, every template, and
`.agent-work/rulings/` are all untouched (`git status --porcelain --
.agent-work/rulings/` → 0 lines). `scripts/hooks/spine_rail.py` was mutated and
restored **byte-identical** twice, as measured evidence; both restorations are
proven by sha256 below.

## Behavior changed

**No.** The change is a pure deletion of an uncalled definition plus prose. The
deleted symbol had zero production call sites — that is why it was deleted. No
refusal is added anywhere (C9), measured three ways:

- 0 non-comment lines added under `scripts/` (68 removed, 13 added, all comments);
- at AST level `checklist_engine.py`'s top-level names went 122 → 120, removing
  exactly `{AGENT_WORK_DIR, worktree_from_spine_path}`, adding none, with **no
  other top-level node changed**;
- the refusal vocabulary is unchanged in count: `REFUSED` 8 → 8,
  `raise EngineError` 82 → 82, `sys.exit` 1 → 1.

## Rework 2 — close criteria, each with the check I ran

### C1 — no reference to the deleted symbol

**This criterion cannot be satisfied as literally worded, and the handoff says so
itself.** C1 asks for `grep -rn "worktree_from_spine_path" --include=*.py
scripts/` to return **zero** lines; but `scripts/hooks/spine_rail.py` is under
`scripts/`, its docstring names the symbol, and both Specific Exclusions and the
Wiring Grep section say that file's repair is **g3's, not mine**. The literal
grep can only reach zero by editing a fenced file.

I applied C1's intent and stated every count instead
(`check_c1_c2_scope.py`):

```
C1: `worktree_from_spine_path` under scripts/ -- 1 line(s) total: 0 outside the fenced g3 file, 1 inside it
    | scripts/hooks/spine_rail.py:743:    `checklist_engine.worktree_from_spine_path` -- duplicated because this module
C1: of the 1 fenced hit(s), 0 are a definition or a call
C2: `AGENT_WORK_DIR` across scripts/ tests/ docs/ skills/ -- 0 line(s)
OK: no live reference to the deleted derivation, and the constant is gone.
```

**Zero references outside the fenced file; the one fenced hit is prose, not a
definition or a call.** I did not touch it. This is reported, not resolved on my
own authority — if the Commander reads C1 strictly, the repair belongs to g3's
handoff, which the Admiral's sequence already assigns it to.

### C2 — `AGENT_WORK_DIR` is gone, and nothing else referenced it

Re-measured rather than taken on trust, as the handoff asked: **0 lines** across
`scripts/`, `tests/`, `docs/` and `skills/`. Nothing else ever referenced it —
the engine's own derivation was its only user.

### C3 — the table drives the hook copy, and still fails loudly

`tests/test_worktree_derivation.py` now names one implementation. `_require` and
`IMPLEMENTATIONS` are kept exactly so a missing implementation fails collection
of the whole file. The deletion test, applied by hand
(`check_deletion_test.py`, `m3-deletion-test.txt`):

```
[1] unmutated collection+run: rc=0 :: 19 passed in 0.02s
[2] excision applied: `def _worktree_from_spine(` present = False
[3] collection with the implementation deleted: rc=2
    | E   AssertionError: spine_rail_for_derivation._worktree_from_spine is missing: the derivation table must
    |     drive EVERY implementation it names, so a missing one fails the whole file rather than silently
    |     checking only the others.
    | !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
    | no tests collected, 1 error in 0.05s
[4] restored byte-identical: True (37cf424e9711)
[5] after restore: rc=0 :: 19 passed in 0.02s
```

The excision is asserted to have applied **before** the measurement, so a
mutation that matched nothing could not leave a green run reading like a passing
guard.

**The cases are unchanged** (`check_cases_unchanged.py`):

```
CASES block, HEAD vs working tree: byte-identical = True (3807 characters)
cases evaluated: HEAD 16, working tree 16
ids and expectations identical = True
```

The second half matters: a byte-identical block whose helper functions changed
would still be a changed specification, so the 16 cases are also compared as they
evaluate.

**One test was removed, deliberately:** `test_the_two_copies_agree`. Over a
single implementation it is a check that cannot fail — one answer is always one
answer. Its removal is recorded in the file where it stood, with the note that it
returns when the second copy does.

### C4 — the module docstring states what is now true

Rewritten. It states one lexical rule; one implementation, in the stdlib-only
hook; the table as the rule's **specification**; and the deletion in #609 g2
under `ADMIRAL_RULING-2` N2, re-landing in #610's wave with #315, which
re-derives against this table. Checked by `check_table_docstring.py` (9 required
clauses, 4 retired ones forbidden), read from the **parsed** module docstring so
a matching sentence elsewhere in the file cannot satisfy it. I proved the check
discriminates by reverting one clause: red, then green on restore, file
byte-identical.

**Three reasons were carried into that docstring** rather than lost with the
deleted copy (`m1-carry-analysis.md`, 13 clauses examined):

1. **What the location is FOR** — "where a check should run and where git should
   be invoked". Nowhere else; it is the consumer's reason, and the consumer is
   #315.
2. **The 2026-08-16 worktree-is-location ruling citation.** `grep -rn
   "worktree-is-location"` outside `.agent-work/` and `map/` returned exactly one
   hit, in the engine copy. The hook carries the sentence but not the citation.
3. **Why the idiom is inlined rather than imported** — importing
   `verify_worktree_isolation.normalize_path` would add an undeclared runtime
   sibling; `agent_work_root._normalize` inlines its own for the same reason.
   Without this, #315 re-lands the copy and "improves" it into an import.

The other 10 clauses were already carried by the hook docstring, the `CASES`
comments, or the per-test docstrings. One — the retired purity argument — was
already recorded as retired and is deliberately not carried.

### C5 — the positive anchor, and why this one

`tests/test_spine_origin_isolation.py` no longer asserts `def
worktree_from_spine_path(` is present. The file does **not** degenerate into pure
absence assertions: the anchor is now `MUTATING_VERBS = {`, and the test is
renamed to
`test_the_retired_predicate_and_its_verb_sets_are_gone_from_a_real_engine`.

**Why that anchor** (recorded in the test's own docstring, as C5 requires):

- it is the surviving **sibling** of the two verb sets asserted absent beside it,
  so the assertion reads as one statement about one subject — which verbs the
  engine gates, and on what;
- it is **load-bearing**: `require_session` gates exactly this set, so it cannot
  quietly disappear the way an unused definition can;
- **nothing in flight moves it.** #609 g3 is `scripts/hooks/spine_rail.py`;
  #610's wave threads `cwd` into `_run_check_command`. Neither touches the verb
  vocabulary. That is the property the previous anchor lacked.

Proven to discriminate (`check_anchor_discriminates.py`) by renaming the anchor
away in the engine and watching the test go red:

```
[1] anchored test, unmutated: rc=0 :: 1 passed in 0.01s
[2] rename applied: `MUTATING_VERBS = {` present = False
[3] with the anchor renamed away: rc=1 :: 1 failed in 0.02s
[4] restored byte-identical: True (e666c1d1ff95)
[5] after restore: rc=0 :: 1 passed in 0.01s
```

The mutation is a rename rather than a deletion on purpose: deleting the set
would break the engine's import and the test would go red for the wrong reason.

### C6/C7/C8 — the three-way agreement, and the drift it caught

All three copies — the `scripts/checklist_engine.py` module header, the
`tests/test_spine_origin_isolation.py` module docstring and
`docs/CHECKLIST_SCHEMA.md` — now carry the same two statements in place of the
sentence that pointed at the deleted symbol:

> The engine now reads no location at all, ambient or derived … because the
> engine no longer asks the question anywhere.
>
> The lexical rule that derives a worktree from a spine's path is **not**
> retired — only the engine's copy of it is. The rule lives in the stdlib-only
> hook, as `spine_rail._worktree_from_spine`, and
> `tests/test_worktree_derivation.py`'s case table is its specification. The
> engine-side copy was deleted in #609 g2 under `ADMIRAL_RULING-2` N2 … It
> re-lands in #610's wave together with #315 — the consumer that threads `cwd`
> into the engine's check runner — and re-derives against that same table.

The three passages are quoted **in full, side by side**, in
`g2-implement-rework2/m5-three-copies-quoted.md` (C7).

Rework 1's leaseless narrowing (R1) is untouched in all three, and so is the
supersession citation of the 2026-08-15 worktree-identity ruling (C8) — both are
still required clauses of the drift check, which passes.

**I updated `check_three_copies.py`, as C6 permits, and say so here.** Its
`derivation-kept` clause required all three copies to name
`checklist_engine.worktree_from_spine_path` — a claim `ADMIRAL_RULING-2` N2 made
false. It is replaced by six clauses covering the repaired sentence, and the old
pointer moved to `FORBIDDEN`. The updated copy lives in
`g2-implement-rework2/check_three_copies.py`; the rework-1 original is left
untouched in its own directory.

**It caught the exact failure it exists for.** First run:

```
DRIFT: scripts/checklist_engine.py: missing required clause 'deleted-under-the-ruling'
DRIFT: tests/test_spine_origin_isolation.py: missing required clause 're-lands-with-its-consumer'
checked 72 clause-assertions across 3 copies
```

The first was **real drift I had introduced**: the engine header said "deleted
here" where the other two cited #609 g2 and the ruling. Repaired.

The second was a **defect in the checker**: its normalizer stripped a leading `#`
as a comment marker, so a docstring line that wrapped with `#610` first was read
as `610` and the clause looked absent. Issue references are part of the claim, so
the normalizer now declines to strip a `#` followed by a digit. No clause was
weakened — the same run still failed on the real drift above. Final:
`checked 72 clause-assertions across 3 copies / OK`.

### C9 — no refusal added

See "Behavior changed". Pure deletion, measured three ways.

### C10 — the suite, and the fall accounted for test by test

| tree | result |
|---|---|
| this tree **before** my change (I re-measured it) | **3204 passed, 5 skipped, 0 failed**, 1183 subtests |
| this tree **after** | **3170 passed, 5 skipped, 0 failed**, 1182 subtests |

The baseline I measured matches the Commander's figure exactly. The fall is
**34**, derived mechanically as a collected-count difference, not read off the
tail (`check_count_delta.py`):

```
tests/test_worktree_derivation.py collected: 53 -> 19 (delta 34)

accounting, test by test:
  - 16  test_derivation[engine-*]                        16 cases x the deleted implementation
  - 16  test_the_two_copies_agree[*]                     the whole drift test
  -  1  test_derivation_is_lexical_not_realpath[engine]
  -  1  test_derivation_never_raises[engine]
  ----  expected drop: 34

whole-suite collection now: 3175; baseline collected 3209 - 34 = 3175
OK: 3204 -> 3170 passed, and every one of the 34 lost tests is accounted for.
```

The last line is the part that rules out coincidence: the **whole suite** is
re-collected and checked against the baseline total, so "some other file also
lost tests" is excluded rather than assumed. Skips and failures are unchanged.

**The one-subtest difference (1183 → 1182) is also accounted for**, located by
per-file comparison against a detached HEAD worktree
(`m6-subtest-delta.txt`): it is `tests/test_context_manifest.py`, 62 → 61.
That file's `rev` tests run one subtest per **clean** tracked target, and
`scripts/checklist_engine.py` is one of its four targets — dirty in my working
tree, so it drops out of the clean list. The test measures cleanliness rather
than assuming it. It returns to 62 once the Commander commits.

**One intermediate red run, and why.** The first full run failed
`test_code_map.py::MapTreeFreshnessTests::test_map_tree_freshness_root_index_matches_a_fresh_build`
— `map/INDEX.md` was stale because the engine had lost an entity. That is C11
firing as designed. I rebuilt the map and re-ran; green.

### C11 — the map is fresh

`py -m scripts.code_map build --root .` → `159 modules, 6132 entities`, and a
real delta committed: `scripts.checklist_engine` 110 → 109 entities (the deleted
function), `tests` 4833 → 4832 (the deleted drift test), with the package totals
following. `map/INDEX.md` is the only map file changed; it was regenerated, never
hand-edited.

## Wiring grep

This slice adds no callable symbol — it removes one, so the grep that matters is
the inverse (C1, above). The handoff's repo-wide grep now returns **4** lines:

```
./scripts/hooks/spine_rail.py:743   -- fenced, g3's
./tests/test_spine_rail.py:904      -- fenced, g3's
./tests/test_spine_origin_isolation.py:448  -- MINE, deliberate
./tests/test_worktree_derivation.py:14      -- MINE, deliberate
```

The two beyond the expected pair are both **mine and intentional**: each names
the symbol in order to say it was *deleted* and where it re-lands. Neither is a
stale claim, and both are in files inside my allowed scope. I found no third
stale reference outside the two fenced files.

## Rework 1 — reconstructed from the dead crew's evidence

I did not perform this work. Its code and prose are in the tree and committed at
`b8557ff4`/rework-1's commits; its evidence is in `g2-implement-rework/`.

| item | what it claimed | how I treated it |
|---|---|---|
| **C1–C3, C6** — narrow the "removed no guard" claim in all three copies | the lease is the guard *wherever a lease exists*; on a spine with no active lease the engine asserts nothing, which is a **widening**, accepted | **re-ran** its check (`check_three_copies.py`, updated) — all R1 clauses still present and required in all three copies today |
| **the leaseless mechanism at source** (`m1-mechanism.txt`) | `require_session` returns early when `lease is None`; `_active_lease` reads a released lease as absent | **reported, not re-measured** — I read both predicates while working and they say what the file records, but the extraction is its measurement, not mine |
| **C5/B2** — the added `_assert_one_answer_for_every_stamp(self.worktree)` call, and the wrong-case row separating (`m3-b2-measurement.txt`) | discriminates from the spine's own worktree, inert from a foreign cwd; mutant red, tree restored byte-identical | **reported, not re-measured.** I confirmed the added call is present and that `tests/test_spine_origin_isolation.py` is green (14 passed, 27 subtests) — I did not re-run its mutant |
| **zero executable change under `scripts/`** (`m4-no-exec-change.txt`) | AST identical with docstrings stripped | **superseded by my own measurement**: rework 2 *does* change executable content (that is the deletion), so I measured the stricter property instead — exactly two named nodes removed, nothing added, nothing else changed |
| **its full suite** (`m4-full-suite.txt`, 3196 passed / 5 skipped) | green | **superseded** by my own baseline of 3204 on the merged tree |

### Rework 1, the unfinished half

Rework 1's **C4** was never applied: its plan shows `m5-result` `in-progress`
with both postconditions unmet, and
`crew-handoffs/g2-implementer-result.md` still carried the understated
behaviour-delta sentence. I completed it, since it is this gate's criterion and
the file is in my allowed scope. The correction is added as a marked **rework
amendment** rather than a silent rewrite, naming the session that applied it and
why it carries a later session's name: every mutating verb, on any spine with no
active lease — never claimed *or* released — and unlike `claim` those verbs write
state into a tree the agent is not standing in.

## Map Impact

- **Structural anchors touched:** `checklist_engine.worktree_from_spine_path` —
  **deleted**. `checklist_engine.AGENT_WORK_DIR` — **deleted**.
  `tests.test_worktree_derivation.IMPLEMENTATIONS` — one entry, `hook`.
  `tests.test_worktree_derivation.test_the_two_copies_agree` — **deleted**.
  `tests.test_spine_origin_isolation.TheEngineTakesNoAmbientReading` — one test
  renamed and re-anchored. `spine_rail._worktree_from_spine` — untouched, three
  live call sites, g3's.
- **Capabilities affected:** the engine's guarded-verb path now reads **no
  location at all**, ambient or derived. Location is no longer a question the
  engine asks.
- **Constraints/assumptions touched:** the case table is now the **specification**
  of the derivation rule rather than a drift detector between two copies. The
  stdlib-only constraint on `spine_rail` is why the rule re-lands as a copy and
  not an import; that reason now lives in the table's docstring, where #315 will
  read it.
- **Decisions:** `two-copies-pinned-by-a-shared-table` — **retired** by
  `ADMIRAL_RULING-2` N2, transcribed here, not re-decided.
  `worktree-is-location-spine-path-is-identity` — **unchanged and now cited in
  the table's docstring**; the rule stands, one implementation of it does not.
  `not-a-weaker-guard` — amended by `ADMIRAL_RULING-1`, rework 1's transcription
  left undisturbed.
- **Evidence produced:** the provenance pin
  (`TheStampIsProvenanceNotADecisionInput`) stays green; the whole
  `tests/test_spine_origin_isolation.py` file is green at 14 passed / 27 subtests.
- **Trust limitations:** `map/ids.jsonl` is 0 bytes and per-module
  `map/<module>/INDEX.md` files are absent repo-wide — inherited as tc1, not
  mine, unchanged by this gate.
- **Triage candidates:** two, below.

## Test mode

**Required:** test-after (a deletion; the tests that had to change are the ones
asserting the deleted symbol exists).
**Satisfied:** yes. I ran both affected files **before** editing them —
`67 passed, 27 subtests passed` — and the transitions are stated: the table went
53 collected → 19 collected and stayed green; the anchored test went green → red
under a renamed anchor → green; the whole-file deletion test went green → hard
collection error → green.

## Evidence

```bash
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework2/check_c1_c2_scope.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework2/check_table_docstring.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework2/check_deletion_test.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework2/check_cases_unchanged.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework2/check_anchor_discriminates.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework2/check_three_copies.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework2/check_no_refusal_added.py
py .agent-work/cleanup-f-derive-worktree/g2-implement-rework2/check_count_delta.py

find . -name __pycache__ -type d -prune -exec rm -rf {} + ; \
  env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT -u CREW_SCRATCH_DIR py -m pytest -q

py -m scripts.code_map build --root . && git status --porcelain -- map/
```

**Result:** all pass. Full suite **3170 passed, 5 skipped, 0 failed** in 127.55s.
Raw output is in `g2-implement-rework2/` (`b0-baseline-suite.txt`,
`m6-full-suite.txt`, `m3-deletion-test.txt`, `m4-anchor-discriminates.txt`,
`m6-no-refusal.txt`, `m6-count-delta.txt`, `m6-map-diff.txt`,
`m6-subtest-delta.txt`, `m5-three-copies-quoted.md`, `m1-carry-analysis.md`).

Every check was run with the documented env scrub. The `CREW_SCRATCH_DIR` caveat
held exactly as the handoff describes: I am running inside a crew session, and
`env -u CREW_SCRATCH_DIR` is what keeps lane E's fenced test from failing on
ambient contamination. I did not touch that test.

## Docs/contracts touched

- `docs/CHECKLIST_SCHEMA.md` — the `origin` section's claim about what answers
  location.

## Assumptions

- **C1's literal wording yields to its intent**, because satisfying it literally
  requires editing a file the same handoff fences. Stated openly above rather
  than silently reinterpreted; the residue is g3's, where the handoff already
  assigns it.
- **`MUTATING_VERBS` is stable through #610's wave.** Based on reading what #315
  changes (`_run_check_command`'s `cwd`) and what g3 changes (`spine_rail.py`).
  If a later wave renames it, the anchor moves with the same reasoning.
- **`test_the_two_copies_agree` should go rather than degrade.** The ruling says
  keep the case table; it does not say keep a test that cannot fail. I removed it
  and recorded where it went and when it returns. If the Commander reads the
  ruling as keeping the file's test set intact, this is the one line to reopen.

## Stop conditions hit

None. No scope was exceeded, no exclusion touched, no required evidence was
unproducible, the suite's fall is fully accounted for, and I do not conclude the
ruling is wrong — the deletion is transcribed as ruled, and the alternative the
Admiral rejected is not re-argued here.

## Out-of-scope observations

- **tc-a — the three-copy prose has no mechanical guard in the repo.** The drift
  check that keeps these three copies honest lives in `.agent-work/`, is written
  fresh by each crew that needs it, and has now been hand-updated twice. It
  caught real drift **both** times. A repo-level test asserting the three copies
  carry one claim would make the guard survive the crew that wrote it. Rework 1
  raised this and was told a mechanical check was not required; I am re-raising it
  as a triage candidate with one more data point rather than building it here.
- **tc-b — `check_three_copies.py`'s normalizer silently renumbered issue
  references.** A `#610` at the start of a wrapped line read as `610`. Fixed in
  my copy. Worth knowing if anyone lifts that normalizer into a repo-level check.

## Workflow Feedback

- **Handoff gaps:** **C1 contradicts Specific Exclusions and the Wiring Grep**,
  and this is the one field that cost real time. C1 demands zero hits under
  `scripts/`; the exclusions forbid touching the only file that produces one; the
  Wiring Grep expects that hit to remain. Two of the three are right and C1's
  wording is the odd one out. A close criterion that cannot be satisfied inside
  the stated scope reads, on first pass, as a stop condition — it should say
  "zero **outside** `scripts/hooks/spine_rail.py`". Second, smaller: C3 says
  "keep the case table … re-scoped" without saying what to do with
  `test_the_two_copies_agree`, which is not a case but is part of the table's
  test set and cannot fail over one implementation. I judged it and said so.
- **Context rediscovered:** that **rework 1's C4 was never applied**. The handoff
  said rework 1's "work is already in the tree and committed" and told me to
  reconstruct its result, but not that one of its close criteria was still
  outstanding. I found it by reading the dead crew's `plan.json` and seeing
  `m5-result` in-progress with both postconditions unmet. A handoff that inherits
  a dead crew's gate should name which of its criteria are **done** and which are
  **open** — that is exactly the state its plan file records.
- **Instructions improvised around:** the implementer skill says a dispatched
  crew's spine is bound before it starts and `spine_status` is the first call. My
  `SPINE_FILE` is my **parent's** spine under my parent's live lease, and my
  `crew-runs.json` entry has `spine: null`; driving it would have advanced someone
  else's gate. I authored my own plan and drove it through the CLI, which is what
  the workbench reference prescribes for exactly this case — but the two texts
  read as contradicting each other at the moment a crew starts, and the crew has
  to know the registry field to tell which applies.
- **What would have made this easier:** reword C1 to exclude the fenced file, and
  add one line to the handoff naming rework 1's open criteria. Both are one-line
  changes and each cost a measurable detour.

## On the Stop hook

**Refused, and recorded as refused.** A `SPINE MID-FLIGHT` hook fired telling me
to reload the commander skill and drive `execute.json` — twice, after this result
was already delivered and my own lease released. `SPINE_FILE` names my parent
Commander's spine (`.../cleanup-f-derive-worktree/spine.json`), whose lease is
held by `commander-cleanup-f-derive-worktree`, and my own registry entry carries
`spine: null` with `parent: .../execute/commander/attempt-3`. Obeying would mean
advancing my parent's gate from a crew session, under a lease that is not mine.

The hook's own escape clause ("if this is an honest stop, use the engine's block
verb") does not apply either: I am not blocked and nothing is out of scope. My
plan reports `DONE: no open items` with its lease released. The gate the hook
calls open is my parent's, and it is open precisely because my parent is waiting
for this file. I drove my **own**
plan (`g2-implement-rework2/plan.json`) under my own lease
(`constellation/cleanup-f-derive-worktree/g2/implementer/attempt-3`) instead, and
I release only that lease. Three crews before me wrote this refusal up; it is
still firing.

**Return status**: complete
