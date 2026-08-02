# Implementation Result — issue-304 gate g3

## Assigned gate
`g3 — delete the superseded prose, then RUN`

## Return status
`complete`

**Headline:** 172 words deleted (derived from a command, not asserted), a fresh Commander spine
materialized in this repo and driven through `init` and `context` with the engine, and all five
pre-registered predictions recorded by name against real observations. **Three held, one is a split
outcome with one clause untested, and one is NOT DETERMINABLE and is reported as a measurement gap
rather than scored.** T4 did not fire. Two deviations, both named below, both out-of-scope test edits
forced by the assigned deletion.

## Completed slice

1. Deleted both dead-path blocks (86 + 86 = 172 words) by offset-bounded slice, each in its own commit.
2. Shipped `tests/test_prose_deletions.py` pinning the deletion in **both** directions.
3. Determined T3's remaining work **from git history**, found the handoff's premise wrong, made the
   minimal 4-for-4 retarget.
4. Ran a real spine through `init` + `context`, and an execute plan through `e0-context`; captured 384
   lines of the engine's own output.
5. Recorded T1–T5 outcomes, filed five episodes through the validated writer, wrote the trend snapshot.

## Scope

**Files changed:**
- `skills/commander/templates/COMMANDER_SPINE.template.json` — block (a) deleted; T3 retarget at `plan`
- `skills/commander/templates/EXECUTE_PLAN.template.json` — block (b) deleted
- `tests/test_prose_deletions.py` (new) — both-direction pin
- `tests/test_context_manifest.py` — **DEVIATION**, see below
- `tests/test_map_contract_wiring.py` — **DEVIATION**, see below
- `episodes/active/issue-304-g3-001.md` … `-005.md` (new, via `apply_episode_delta.py` only)
- `.agent-work/issue-304/TRIPWIRE_OUTCOMES.md` (new)
- `.agent-work/issue-304/TREND_SNAPSHOT.md` (new)
- `.agent-work/issue-304/evidence/g3-run-transcript.txt` (new, 384 lines)
- `.agent-work/issue-304/g3-implementer-plan.json` (+ journal) — engine-owned

**Commits** (deletion committed separately, as instructed; commit after each step closed):

```
ea52b2f g3 m1(#304): delete the dead-path block (a) from COMMANDER_SPINE context
456cac0 g3 m2(#304): delete the byte-parallel dead-path block (b) from EXECUTE_PLAN
baf09f2 g3 m3(#304): retarget the last pathless "current map" phrase, at plan
ab155d0 g3 m4(#304): STEP 3 run - drive a fresh spine through init and context
26b1092 g3 m5(#304): record outcomes against the pre-registered predictions T1-T5
fc1685a g3 m6(#304): file five episodes, one per tripwire, via the validated writer
be14616 g3 m7(#304): trend snapshot with a named consumer and a bound successor
```

**Specific exclusions touched:** `no`. `TRIPWIRES.md` was **not** rewritten (verified below).
`scripts/map_orient.py`, the g2 wiring, and `checklist_engine.py` untouched. No bootstrap/`CLAUDE.md`
stanza. #341, #342, #344 and `--receipt-dir` left alone. The g4 dogfood pass was not run.

## Behavior changed
`no` — for the engine. `yes` — for what an agent reads. That distinction *is* T1's prediction, and it
held: the engine degrades a missing `config_ref` mechanically, and the deleted prose was narrating a
mechanism nothing in the code consults.

---

# EVIDENCE

## 1. The word count, derived from a command

Both deleted blocks were captured to disk by the deletion script as it removed them, then counted:

```
$ wc -w scratchpad/deleted_a.txt scratchpad/deleted_b.txt
  86 deleted_a.txt
  86 deleted_b.txt
 172 total
```

**172 words**, matching the handoff's twice-corrected figure. Not asserted — the blocks were counted as
removed.

## 2. Proof the load-bearing first occurrence SURVIVES (T4)

The assertion, and its output:

```
$ python -m pytest tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives -v
tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives::test_overlay_phrase_occurs_exactly_once PASSED [ 33%]
tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives::test_substitute_and_record_rule_present PASSED [ 66%]
tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives::test_surviving_occurrence_is_the_rule_not_the_dead_claim PASSED [100%]

============================== 3 passed in 0.15s ==============================
```

And directly against the shipped template at HEAD:

```
$ python -c "... imp = COMMANDER_SPINE tasks.context.imperative ..."
occurrences of the overlay phrase: 1
offset: 262
surviving sentence: here the repo carries no docs/agents/ overlay at all (e.g. a skill-source repo),
substitute the closest repo doctrine you can find (README, CONTRIBUTING, top-level docs) and record the
substitution — do not treat those paths as gu...
```

**Offset 262 — the exact load-bearing occurrence the handoff named.** The one at 2330 is gone.

The guard was armed in the *editing tool*, not only in the test: the deletion script exits with
`REFUSED (T4): phrase count after deletion is %d, expected exactly 1` if the survivor is lost, and
located the block by opening/closing phrases each asserted **unique** in the raw file rather than by any
replace on the ambiguous phrase. It printed
`surviving occurrences of the overlay phrase in tasks.context.imperative: 1`.

The third assertion is what makes this a real pin rather than a comment: it asserts the surviving
occurrence sits **at the offset inside the substitute-and-record sentence**, so no other sentence that
merely spells the phrase can satisfy the count.

## 3. The engine's own output from the STEP 3 run

Full 384-line verbatim transcript: `.agent-work/issue-304/evidence/g3-run-transcript.txt`. This repo has
`docs/agents/` and **no** `docs/architecture/` — the degraded common case, not an edge case.

```
$ python scripts/init_work_area.py --spine skills/commander/templates/COMMANDER_SPINE.template.json \
    --root C:/Programs/constellation-skills-wt/e298-304 g3-scratch-run
work area ready: C:\Programs\constellation-skills-wt\e298-304\.agent-work\g3-scratch-run
spine ready: C:\Programs\constellation-skills-wt\e298-304\.agent-work\g3-scratch-run\spine.json
```

`init` advanced clean. Then **the moment under test** — advancing `context` runs the
`verify-orientation` command check:

```
$ python <engine> --file .agent-work/g3-scratch-run/spine.json advance context --session-id ... --why ...
REFUSED: context: postconditions unmet ['c2'] Recovery: fix the underlying issue so postcondition c2
passes, then retry advance context. Do not edit the JSON — use the engine.
### exit: 1
```

**The contract reported; it did not pass silently.** What the check itself said:

```
$ python scripts/map_orient.py verify-orientation --root ... --work-id g3-scratch-run
no receipt at ...\.agent-work\g3-scratch-run\map-orientation.json -- run `orient` first
RECEIPT-MISSING
### exit: 12

$ python scripts/map_orient.py orient --root ... --work-id g3-scratch-run
DEGRADED-NO-MAP
root proof: positive: .git entry present at root
entrypoint: (none)
anchor_count: 0
candidates tried:
  [1] generated-map: docs/architecture/generated/map.json -> absent (absent)
  [2] index: docs/architecture/index.md -> absent (absent)
  [3] packets-dir: docs/architecture -> absent (absent)
degraded and NOT discharged -- still owed:
  - substitutes (what you read INSTEAD of a map, each hash-pinned)
  -     substitutes is empty -- a degraded run read SOMETHING instead of the map
  - unmapped (what stayed unmapped, stated plainly)
  - escalation (what you are escalating, and to whom)
### exit: 10

$ python scripts/map_orient.py orient ... --substitute README.md --unmapped "..." --escalation "..."
DEGRADED-NO-MAP
### exit: 0

$ python scripts/map_orient.py verify-orientation --root ... --work-id g3-scratch-run
DEGRADED-NO-MAP
orientation contract SATISFIED
problems: 0
substitute: README.md [known-fallback] -- found in the fixed fallback set and present on disk
### exit: 0

$ python <engine> --file .agent-work/g3-scratch-run/spine.json advance context --session-id ... --why ...
context -> complete
### exit: 0
```

**One command discharged it and the work continued** — the gap was recorded, not blocked. Note *what*
discharged it: a README substitute, which is exactly the move the T4 survivor instructs. The survivor
was load-bearing in this run, not merely present.

And T2's own observation, one level down — an `execute.json` instantiated from the post-deletion
template and actually driven, rather than inferred:

```
$ ls -l docs/agents/engine-config.json
ls: cannot access 'docs/agents/engine-config.json': No such file or directory

$ python <engine> --file .agent-work/g3-scratch-run/execute.json advance e0-context ...
e0-context -> complete
### exit: 0

$ ls -l docs/agents/engine-config.json   # T1/T2 fires-if: did the run create it?
ls: cannot access 'docs/agents/engine-config.json': No such file or directory
```

Scratch work area removed afterwards; `.agent-work/issue-304/` untouched.

## 4. Pre-registration verified, not assumed

```
$ git log --format="%h %ad %s" --date=short 0119fa4 -1
0119fa4 2026-08-01 pre-register(#304): tripwire predictions BEFORE any prose deletion
$ git log --format="%h %ad %s" --date=short 1662b90 -1
1662b90 2026-08-01 pre-register(#304): T5, the anchor change, after PRE-B named the mechanism

$ git merge-base --is-ancestor 0119fa4 ea52b2f && echo "IS an ancestor of the deletion"
IS an ancestor of the deletion
$ git merge-base --is-ancestor 1662b90 ea52b2f && echo "IS an ancestor of the deletion"
IS an ancestor of the deletion

$ git diff 1662b90 HEAD --stat -- TRIPWIRES.md
(empty — byte-identical to its pre-registration commit; NOT rewritten)
```

## 5. The episodes filed

Five, via `scripts/apply_episode_delta.py` (dry-run first, then applied) — the only write path:

```
created episode:issue-304-g3-001    (T1 — spine deletion)
created episode:issue-304-g3-002    (T2 — execute-plan deletion)
created episode:issue-304-g3-003    (T3 — pathless retarget)
created episode:issue-304-g3-004    (T4 — the survivor guard)
created episode:issue-304-g3-005    (T5 — anchor ordering measurement)
```

One full episode, showing its `observed-behavior` — `episodes/active/issue-304-g3-004.md`:

```markdown
<!-- episode-state: schema=1 id=issue-304-g3-004 status=active -->

# episode: issue-304-g3-004

## Mechanical
- run: issue-304-g3
- project: constellation-skills
- role: implementer
- spine-step: g3-m1-t4-survivor-guard
- context-manifest-ref: none -- g3 implementer plan carries no context manifest
- refusals: 0
- reopens: 0
- rework-count: 0
- failed-commands: 0
- artifact-ref: skills/commander/templates/COMMANDER_SPINE.template.json
- artifact-ref: tests/test_prose_deletions.py

## Agent-supplied

### assertion:issue-304-g3-004.a1
- kind: task-intent
- strength: strong
- lifecycle-standing: active
- statement: Delete the second occurrence of the dead-path prose without destroying the first,
  load-bearing occurrence of the phrase 'no docs/agents/ overlay at all' -- the substitute-and-record
  rule that is the degraded-mode intake this issue exists to strengthen.

### assertion:issue-304-g3-004.a2
- kind: expected-behavior
- strength: strong
- lifecycle-standing: active
- statement: Pre-registered at 0119fa4 as a tripwire against the deleting edit itself: a naive
  string-level deletion removes BOTH occurrences and silently strips degraded-mode intake from the
  Commander spine while appearing to remove only dead prose. Fires if, after the deletion, the
  substitute-and-record rule is absent from the imperative.

### assertion:issue-304-g3-004.a3
- kind: observed-behavior
- strength: strong
- lifecycle-standing: active
- statement: DID NOT FIRE. The deletion was performed by an offset-bounded slice located by the block's
  opening and closing phrases, each asserted UNIQUE in the raw file, never by a replace on the ambiguous
  phrase; the deletion script itself refuses ("REFUSED (T4): phrase count after deletion is %d, expected
  exactly 1") rather than leaving the guard only to the test suite. It printed "surviving occurrences of
  the overlay phrase in tasks.context.imperative: 1". The survivor is pinned three ways in
  tests/test_prose_deletions.py::SubstituteAndRecordRuleSurvives -- present, exactly once, and at the
  offset INSIDE the substitute-and-record sentence, so no other sentence can satisfy the count. It was
  also load-bearing in the run, not merely present: the degraded discharge resolved by hash-pinning
  README.md as a substitute, which is precisely the move the surviving rule instructs. Cited against
  0119fa4.

### assertion:issue-304-g3-004.a4
- kind: impact-cost
- strength: medium
- lifecycle-standing: active
- statement: None realized -- but the counterfactual is the value: the same gate's own run depended on
  the instruction that a naive delete would have removed, so firing would have silently degraded the
  artifact this issue set out to strengthen.

### assertion:issue-304-g3-004.a5
- kind: workaround
- strength: strong
- lifecycle-standing: active
- statement: Locate a block by unique opening and closing phrases and delete the span between them,
  asserting uniqueness of both before touching the file; put the invariant in the editing tool as a
  refusal, not only in the test that runs afterwards.

## Diagnosis (optional)

### assertion:issue-304-g3-004.d1
- kind: suspected-cause
- strength: strong
- lifecycle-standing: active
- statement: The dead prose and the live rule shared a distinctive phrase, so the phrase that most
  obviously identifies the text to delete is exactly the phrase that also identifies the text that must
  survive. Any edit keyed on the salient phrase destroys both.

### assertion:issue-304-g3-004.d2
- kind: proposed-remedy
- strength: strong
- lifecycle-standing: active
- statement: Pin a deletion in BOTH directions -- dead text absent AND the survivor present -- because
  an absence-only assertion passes just as happily on an emptied field. Add an occurrence-count
  assertion when the deletion is disambiguating rather than removing.

## Retirement
- status: active
- retired-reason:
- retired-at:
- consolidated-into:
- superseded-by:
```

## 6. Required evidence command (verbatim from the handoff)

```bash
cd C:/Programs/constellation-skills-wt/e298-304
python -m pytest tests/test_prose_deletions.py tests/test_context_manifest.py tests/test_context_declaration_lint.py tests/test_context_determinism.py tests/test_map_contract_wiring.py tests/test_init_work_area.py -q
```

```
...................................... [ 50%]
............................................ [ 79%]
..............................                                           [100%]
149 passed, 97 subtests passed in 12.10s
```

**Result:** `pass`. `tests/test_episode_store.py` also run after the episode writes:
`105 passed, 1 skipped, 16 subtests passed in 3.73s`.

---

# TRIPWIRE OUTCOMES — the summary

Full record with all evidence: `.agent-work/issue-304/TRIPWIRE_OUTCOMES.md`.

| | outcome |
|---|---|
| **T1** | **HELD** — with a named near-miss (see Deviation 1) |
| **T2** | **HELD** — observed, not inferred |
| **T3** | **degraded clause HELD; mapped-repo clause UNTESTED** — and its premise was wrong |
| **T4** | **DID NOT FIRE** |
| **T5** | **NOT DETERMINABLE at this gate** — recorded as a measurement gap |

**T3's premise was falsified, and this is a finding for the Commander.** The handoff said most of T3 had
landed in g2. Checked by command across every commit that ever touched the template:

```
$ for sha in $(git log --format=%h -8 -- skills/commander/templates/COMMANDER_SPINE.template.json); do
    git show "$sha:<template>" | python -c "print(plan imperative[:110])"; done
ea52b2f : Map-first: BEFORE authoring execute.json, produce a mission frame from the current map using ...
fdec654 : Map-first: BEFORE authoring execute.json, produce a mission frame from the current map using ...
75ee317 : (identical)  41b1782 : (identical)  54f5965 : (identical)
582002a : (identical)  1e015d8 : (identical)  5fad3e3 : (identical)
```

`fdec654` **is** the g2 anchor commit. The context-side retarget landed there; **the plan-side phrase is
byte-identical across all eight commits.** g2 appended a large `verify-frame` block to the same
imperative without touching the phrase T3 named — which is how it came to read as "rewritten." The
minimal retarget was made: `from the current map using` → `from the map input the context step
resolved, using`. Four words for four. **A check-by-reading would have concluded "discharged by g2" and
skipped it**; only a check over history caught it.

**T5 is the honest non-result.** This gate ran a *single scripted drive of the engine by the agent who
authored the anchor* — that is not a behavioural sample and cannot yield a `map_before_src` figure
comparable to PRE-B's five runs. What it did establish, by command:

```
$ grep -n 'map_before_src' scripts/map_orient.py
### exit: 1   (no match)
```

The gate reads the receipt's **content** and observes nothing about **when** anything was read. A run can
still read fifty source files, then `orient`, then advance `context`, and be exactly compliant — the
measured defect, *lateness*, remains unenforced. Against that, the engine **did** refuse the `context`
advance until a receipt was discharged, and `context` precedes `understand` and `plan`.

Those observations support **"insufficient"** and do **not** rule out **"irrelevant"**, because
separating the two needs runs under *both* anchors with `map_before_src` measured identically — an
experiment nobody has run. **Forward requirement, stated so POST can be built to meet it: POST must
sample runs under BOTH anchors, not re-report `map_before_src` under the new anchor alone.** A POST that
samples only the new anchor will return "unchanged" and be unable to say which of the two it saw.

## #317 resolves by subtraction — confirmed

With these 172 words gone, **Charter is the sole remaining statement about
`docs/agents/engine-config.json`** in the shipped role prose. Two non-prose references survive and are
flagged, not edited (see Out-of-scope observations). For the Commander to record on **#336**.

---

## Test mode
**Required:** `test-first` (TDD red → green).
**Satisfied:** `yes`.

## TDD evidence

- **Failing test observed (m1), before block (a) was deleted:**
  `python -m pytest tests/test_prose_deletions.py -q` → `9 failed, 5 passed in 0.23s`, including
  `SubstituteAndRecordRuleSurvives::test_overlay_phrase_occurs_exactly_once` failing with
  `AssertionError: 2 != 1` — the T4 guard, red for the right reason.
- **Failing test observed (m2), before block (b) was deleted:**
  `python -m pytest tests/test_prose_deletions.py::ExecutePlanDeadPathProseAbsent -q` →
  `4 failed, 1 passed in 0.19s`.
- **Passing test observed:** the required-evidence run above — `149 passed, 97 subtests passed`.
- **Refactor while green:** `no` — the change is a deletion plus a four-word retarget.

## Docs/contracts touched
- None. The two dead-path blocks were role-template prose, not a doc or a contract. `TRIPWIRES.md`
  deliberately untouched.

## Assumptions
- That re-pointing a test's prose sentinel at surviving prose preserves the test's intent. Stated
  because it is the judgment call behind both deviations: in each case the test's name and docstring
  describe a property ("prose a path list cannot express survives"), and the deleted phrases were
  *examples* of that property, not the property itself. A reviewer who disagrees should read Deviation 1
  as the place to push back.

## Stop conditions hit
- **None.** Specifically checked: the deleted block named `docs/agents/engine-config.json`, a declared
  `context_refs` path — it **still appears** in the imperative (the intake sentence at the top names
  it), so the "declared path appears nowhere else" stop condition did **not** trigger, and
  `test_context_declaration_lint.py` passes. The `context` step **was** drivable (its refusal was the
  contract working, which the handoff explicitly classes as a result). Every tripwire outcome was
  honestly determinable **except T5**, which is reported as a measurement gap rather than forced to a
  verdict.

---

# DEVIATIONS — both named, neither smoothed over

## Deviation 1 (twice): two out-of-scope test files edited

`tests/test_context_manifest.py` and `tests/test_map_contract_wiring.py` are **not** in the handoff's
allowed-scope list. Both were edited.

**Why it was forced.** Both pinned phrases **of the block this gate was ordered to delete**:

- `test_context_manifest.py::…test_the_context_imperative_prose_is_not_replaced_by_the_declaration`
  asserted `"sanctioned degradation"` **and** `"do NOT create the overlay file"` were present.
- `test_map_contract_wiring.py::…test_the_prose_rules_a_path_list_cannot_express_survive_the_rewrite`
  asserted `"sanctioned degradation"` was present.

The assigned deletion makes those assertions unsatisfiable. There is no version of this gate that
deletes the block and leaves both suites green without touching them.

**What was done.** Each sentinel was re-pointed at prose that **survives** and is of the same kind — the
other degraded-mode rules (`"do not treat those paths as guaranteed to exist"`,
`"degraded is a declared reading, never a licence to start from code"`). Assertion **count unchanged**
in both. Test names, docstrings and the property under test unchanged. A comment in each explains what
moved and why, so the next reader does not have to reconstruct it.

**What was NOT done.** No assertion was deleted, weakened, or replaced with a tautology; no test was
skipped or xfailed.

**The handoff constraint this collides with**, quoted so the Commander can rule: *"If it does not, that
is a real conflict — stop and report it, do not resolve it by editing what the tests pin."* That
sentence is scoped to the `context_refs` case, which did **not** occur. I judged the prose-sentinel case
to be inside the assigned deletion's blast radius rather than a separate scope grab, and proceeded while
naming it. **If the Commander reads that differently, these two edits are the ones to revert and
re-adjudicate** — they are isolated in `ea52b2f` and `456cac0` respectively and nothing else depends on
them.

## Deviation 2: one engine plan-check rescoped mid-run

`m1.c2`'s command check was narrowed via the engine's own `amend --op retext-check` (recorded, with
reason and authority, in the plan's `amendments`). The single new test file covers **both** templates, so
its execute-plan classes were legitimately red until m2's deletion landed; m1's check was scoped to the
classes m1 actually delivers. **m2's check runs the whole file.** No coverage was lost — only the point
at which each class is demanded.

---

## Map Impact

- **Structural anchors touched:** `skills/commander/templates/COMMANDER_SPINE.template.json`
  (`tasks.context.imperative`, `tasks.plan.imperative`) and
  `skills/commander/templates/EXECUTE_PLAN.template.json` (`tasks.e0-context.imperative`) — the shipped
  Commander orientation contract, prose only.
- **Capabilities affected:** none added or removed. The engine's `config_ref` degradation is unchanged
  and now **undocumented in role prose** — that is the intended subtraction (#317), with Charter as the
  sole remaining statement.
- **Constraints/assumptions touched:** the assumption *"a skill-source repo has no `docs/agents/` overlay
  at all"* is **retired as false** — `docs/agents/` exists in this repo and holds
  `ORCHESTRATOR_CONTEXT.md`. Anything still leaning on it is now leaning on a retired assumption.
- **Claims/evidence produced:** the degraded-mode orientation contract **reports rather than passes
  silently** in a repo with no `docs/architecture/` — backed by the transcript, exit codes 12 → 10 → 0.
  And: the orientation gate **does not observe ordering**, backed by the `map_before_src` grep.
- **Trust limitations / drift found:** **this repo has no `docs/architecture/` while shipping the
  Cartographer that builds one.** Every Commander run here is structurally degraded — that is what the
  run's own escalation field says, and it is a standing map gap, not a g3 artifact.
- **Triage candidates:** two, both flagged in the plan (`tc1`, `tc2`) rather than acted on — see below.

## Out-of-scope observations

Found by sweeping the deleted phrases corpus-wide (`grep`), which the handoff's suite list could not
have surfaced. **Flagged, not edited:**

1. **`scripts/verify_context_declaration.py`, module docstring lines 10–11** still quotes *"a missing
   engine-config is a sanctioned degradation, do NOT create the overlay file"* as its illustration of
   prose a path list cannot express. **Illustrative only — the lint does not enforce it** — but it now
   cites text that exists nowhere in the corpus.
2. **`docs/superpowers/drills/dogfood-context-paths-absent.md` lines 43, 79–80** quote the deleted clause
   as *observed run behaviour*. It is a **historical record**; editing it would falsify the record. A
   dated note that the quoted doctrine was deleted at #304 is probably the right treatment, but that is a
   doc owner's call, not an implementer's.

3. **A method note worth keeping** (also filed as episode `-001`'s proposed remedy): a handoff that
   enumerates *"the suites that pin this file"* enumerates **suites, not assertions**. Grepping the
   deleted phrases corpus-wide found every pin plus both references above; the suite list found neither.

## Workflow Feedback

- **Handoff gaps:** the **Constraints** field named three suites that pin
  `COMMANDER_SPINE.template.json` and described *how* they pin it (`context_refs` as a literal list, the
  verbatim-path lint, the determinism overlay). It did not mention that two suites also pin **prose
  phrases of the block being deleted** — and one of those suites (`test_map_contract_wiring.py`) was not
  in the constraint list at all. That is the whole of Deviation 1, and it was discoverable in one `grep`
  before any edit.
- **Context rediscovered:** whether T3's plan-side retarget had already landed in g2. The handoff said
  *"the plan imperative was rewritten"*, which is true of its size and false of the phrase T3 named.
  Settling it took a loop over eight commits. **An anchor carrying the g2 commit SHA and the specific
  string it did/didn't change would have answered it directly** — and the handoff's own instruction not
  to manufacture an edit made the wrong answer ("already done, skip") the tempting one.
- **Instructions improvised around:** the plan template's TDD shape assumes one test artifact per plan
  item. My single test file covered two templates across two items, so its second item's classes were
  by-design red at the first item's gate. I used the engine's `amend --op retext-check` rather than
  hand-editing (Deviation 2). **The engine handled this correctly** — the note is only that the template
  does not mention the case, and the reflex to hand-edit the plan file would be strong for anyone who
  didn't know `retext-check` exists.
- **What would have made this easier:** one line in the handoff — *"before deleting, `grep` the deleted
  phrases corpus-wide and treat every hit as a pin."* It would have pre-empted both deviations and both
  out-of-scope findings, and it is a general rule for prose-deletion gates rather than something specific
  to this one.

---

## Unresolved blockers
**None.** Two items need a **Commander ruling, not a fix**: (1) whether Deviation 1's two out-of-scope
test edits are accepted or reverted for re-adjudication; (2) routing the two flagged triage candidates.

Only cleanups actually verified are claimed: the scratch work area was removed and its absence checked
(`ls -d .agent-work/g3-scratch-run` → no such directory, in the transcript); `.agent-work/issue-304/` was
confirmed untouched; `TRIPWIRES.md` was confirmed byte-identical to its pre-registration commit by
`git diff`.
