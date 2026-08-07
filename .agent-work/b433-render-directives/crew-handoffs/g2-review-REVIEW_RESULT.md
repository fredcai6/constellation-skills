# Review Result

## Assigned Gate
`g2-review` (execute.json, work-id `b433-render-directives`, issue #433)

## Result
`APPROVE`

Survey: `.agent-work/b433-render-directives/g2-review/review.json` — 16 checks, all pass, no fail, no
blocker, consolidated `verdict=APPROVE`. Fowler pass:
`.agent-work/b433-render-directives/g2-review/fowler-pass.json`, `verify_fowler_pass.py` EXIT=0.

I accepted none of the implementer's captures. I broke the tree myself four times, watched the specific
red, and restored to a byte-identical file each time.

---

## Close criteria — one finding each, with how I verified it

### 1. Reproduce red-proof R2 — extractor blind to dicts

**PASS.** I replaced `_leaf_texts`' dict branch with `return []  # REVIEWER-R2-BREAK` and confirmed by
grep that the break landed (line 4230) before running anything.

```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py; echo "EXIT=$?"
```
```
tests\test_checklist_engine.py:4291: in _assert_every_populated_field_renders
    self.assertEqual(
E   AssertionError: Items in the second set but not the first:
E   'anchors'
E   'directives' : populated field(s) ['anchors', 'directives'] were carried by the loop but asserted NOTHING -- _leaf_texts read no text out of them, so current()'s output was never checked against their content
=========================== short test summary info ===========================
FAILED tests/test_checklist_engine.py::TaskFieldCompleteness::test_every_populated_field_renders_for_a_fully_populated_gate
1 failed, 348 passed, 30 subtests passed in 9.72s
EXIT=1
```

RED, and it is the **ledger set-mismatch naming the fields** — not green, and not some unrelated red.
Restored; `git hash-object` back to `a70bbb2f`.

### 2. Reproduce red-proof R4 — a populated field that flattens to nothing

**PASS.** I added `t["reviewer_r4_field"] = {"nested": None}` to `_fully_populated_gate()` — truthy, so it
enters the loop; yields no leaves. Grep confirmed the break at line 4263 before running.

```
tests\test_checklist_engine.py:4293: in _assert_every_populated_field_renders
    self.assertEqual(
E   AssertionError: Items in the second set but not the first:
E   'reviewer_r4_field' : populated field(s) ['reviewer_r4_field'] were carried by the loop but asserted NOTHING -- _leaf_texts read no text out of them, so current()'s output was never checked against their content
=========================== short test summary info ===========================
FAILED tests/test_checklist_engine.py::TaskFieldCompleteness::test_every_populated_field_renders_for_a_fully_populated_gate
1 failed, 348 passed, 30 subtests passed in 10.19s
EXIT=1
```

Fails **by name**. This red is also the decisive proof for criterion 4: the field yields zero leaves, so
the inner `assertIn` never runs, and only the per-field set comparison can catch it. Restored; hash back
to `a70bbb2f`.

### 3. Reproduce red-proof R5 — an engine field forgotten in the fixture

**PASS.** I added `"reviewer_r5_field": op.get("reviewer_r5_field")` to `_build_amend_task` in
`scripts/checklist_engine.py`. Grep confirmed the break at line 2118 before running.

```
        missing = set(built) - set(self._fully_populated_gate())
>       self.assertEqual(
E       AssertionError: Items in the first set but not the second:
E       'reviewer_r5_field' : the engine's Task builder _build_amend_task now emits ['reviewer_r5_field'], which this class's fixture does not carry, so the completeness loop would never see the field -- add it to _fully_populated_gate() with content the briefing should show, or to _EXCLUDED_FIELDS with a stated reason. append() mirrors the same shape (scripts/checklist_engine.py)

tests\test_checklist_engine.py:4326: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_checklist_engine.py::TaskFieldCompleteness::test_fixture_carries_every_field_the_engines_task_builder_builds
1 failed, 348 passed, 30 subtests passed in 10.16s
EXIT=1
```

Fails **by name**, in the superset assertion, which proves that test is wired to the live builder rather
than to a re-listed copy of its keys. Restored; engine hash back to `ef979b43`.

### 4. The ledger is per-field, not one flag

**PASS.** `tests/test_checklist_engine.py:4276-4298`: two sets, `expected` (every populated non-excluded
field) and `asserted` (the fields `_leaf_texts` actually produced text for), compared with `assertEqual`.
There is no boolean variable in the loop body. `grep checked_any` returns two hits, both **prose** — the
class docstring at 4152 and the explanatory comment at 4290 naming what the ledger replaces. My R4
reproduction is the behavioural confirmation: a single flag could not have caught that field.

### 5. The test's leaf extractor is not the renderer's

**PASS.** `_leaf_texts` (4206-4235) is a self-contained recursion over `str` / `dict` / `list` / `tuple` /
scalar; it calls only itself. Grepping the whole `TaskFieldCompleteness` body for `_directive_leaf`,
`_render_directive_lines` and `_render_anchor_lines` returns exactly two hits, both inside the docstring at
4219-4220 — no code reference. Grepping the whole test module for `E._directive_leaf`,
`E._render_directive_lines` and `from scripts` returns nothing. A shared bug therefore cannot render
nothing and assert nothing in agreement.

### 6. The class docstring states the residual limit

**PASS.** `tests/test_checklist_engine.py:4162-4166` states it plainly:

> RESIDUAL LIMIT, stated rather than implied: the superset assertion closes the hole for fields the ENGINE
> introduces. A field introduced only by a template — carried in a shipped checklist JSON but built by
> neither `_build_amend_task` nor `append()` — is still invisible to this property and needs a human to add
> it to the fixture.

I checked that this is true rather than decorative: reading both builders in the working tree,
**neither `_build_amend_task` (~2105) nor `append()` (~2317) emits `anchors`**, so the fixture's own
`anchors` key is a live instance of the stated residual. The docstring also names the three properties
that make the loop capable of failing and says outright that #420's version had none of them, so it claims
less coverage than the property has, not more.

One non-blocking observation: the docstring states the residual as a class but does not name `anchors` as
today's live example. That detail lives only in the IMPLEMENTER_RESULT's out-of-scope observations, where
a future reader of the test is less likely to meet it. Recorded as observation 1 below.

### 7. Every remaining `_EXCLUDED_FIELDS` entry keeps its stated reason; only `directives` removed

**PASS**, both halves verified.

- `git show HEAD:tests/test_checklist_engine.py` carries the 14-name set `{id, status, preconditions,
  postconditions, status_detail, rework_count, result, finding, evidence, why_exempt, child_checklist,
  context_refs, title, directives}`. The working tree carries the same set minus `directives`. Nothing
  added.
- All 13 survivors keep a reason in the comment block at 4172-4194. I checked them off one at a time
  against the set literal: `id`/`status`, `preconditions`/`postconditions`, `status_detail`,
  `rework_count`, `result`/`finding`, `evidence`, `why_exempt`, `child_checklist`, `context_refs`,
  `title`. No orphan entry.
- The removed entry's `KNOWN GAP` paragraph is replaced by a note saying why the field is now ordinary
  rendered content, so the removal is documented rather than silent.

### 8. The negative self-test drives the real assertion path

**PASS.** `tests/test_checklist_engine.py:4336-4353` builds the fixture, deep-copies it, sets
`directives = None` on the **copy**, and takes a genuine render — `out = E.current(gated(g1=unrendered))` —
then calls `self._assert_every_populated_field_renders(t, out)`, the same helper the positive test calls at
4303. It is not a hand-rolled copy of the assertion, and it does not assert against edited output text: the
briefing is one `current()` really emits for a gate with no directives, which is exactly the pre-#433
output. It wraps the call in `assertRaises(AssertionError)` and asserts `"directives"` appears in the
message, so it pins the by-name property too.

### 9. The flat-list carry-over is total and has a test

**PASS.** The branch is `return [f"  {_directive_leaf(item)}" for item in directives]` — no `isinstance`
filter, every item rendered, matching `_render_anchor_lines`' unfiltered list branch and the helper's own
docstring rule. `test_flat_list_with_a_non_string_item_renders_every_item` (4055-4070) pins
`["file REPLAN_INPUT.json before advancing", 17, False]` to three lines with `False` spelled `false`.

I did not take that on faith. I reverted the branch to the pre-g2 filter
`[f"  {item}" for item in directives if isinstance(item, str)]` and ran the suite:

```
E       AssertionError: 'ACTI[48 chars]LAN_INPUT.json before advancing\nnext: start g1' != 'ACTI[48 chars]LAN_INPUT.json before advancing\n  17\n  false\nnext: start g1'
E         ACTIVE g1 [pending] - do g1
E         directives:
E           file REPLAN_INPUT.json before advancing
E       +   17
E       +   false
E         next: start g1

tests\test_checklist_engine.py:4068: AssertionError
FAILED tests/test_checklist_engine.py::RenderDirectives::test_flat_list_with_a_non_string_item_renders_every_item
1 failed, 348 passed, 30 subtests passed in 11.44s
EXIT=1
```

The test really guards the line. Restored; engine hash back to `ef979b43`. This closes the g1 reviewer's
carry-over exactly as raised (`g1-review-REVIEW_RESULT.md:271-272` names the same string).

### 10. Suite, real exit code, and no residual break

**PASS.** Run with `python`, never `py` (#454, `docs/agents/CREW_CONTEXT.md`):

```
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py; echo "EXIT=$?"
349 passed, 30 subtests passed in 11.56s
EXIT=0
```

349 against a 346 baseline, +3 as claimed (superset test, negative self-test, flat-list carry-over test).
My own pre-review baseline run of the same command also gave `349 passed, 30 subtests passed`, `EXIT=0`.

Tree left exactly as found:

- `git hash-object scripts/checklist_engine.py tests/test_checklist_engine.py` → `ef979b43…` /
  `a70bbb2f…`, byte-identical to the backups I took before the first break.
- `git status --porcelain -- scripts tests docs` → only the two expected ` M` lines.
- `git diff --stat -- scripts tests docs` → unchanged at 67 / 373, 394 insertions / 46 deletions.
- Break-marker sweep `grep -rn "REVIEWER-R2-BREAK\|REVIEWER-R4-BREAK\|REVIEWER-R5-BREAK\|REVIEWER-R9-BREAK\|reviewer_r4_field\|reviewer_r5_field" scripts tests docs skills` → **no matches, exit 1**. The
  only hits anywhere in the worktree are inside my own survey findings, which describe the reproductions
  in prose.

---

## Handoff compliance

All five mandated changes plus the carry-over are present, and I found nothing asked for missing:
`directives` out of `_EXCLUDED_FIELDS` (4200-4204); `_flatten` replaced by the total `_leaf_texts`
(4206-4235); `checked_any` replaced by the `expected`/`asserted` per-field ledger (4276-4298); the new
superset test against `E._build_amend_task` (4310-4334); the negative self-test driving the shared helper
(4336-4353); and the engine flat-list branch routed through `_directive_leaf`.

Test mode was test-first in the strong sense the handoff meant — the red-proofs are the deliverable, and
all three reproduce independently.

## Scope drift

None. `git status --porcelain` shows exactly two modified deliverable files, `scripts/checklist_engine.py`
and `tests/test_checklist_engine.py`.

- `docs/CHECKLIST_SCHEMA.md` untouched (g3-schema owns it).
- `scripts/collect_feedback.py` (#464), `episodes/` (#460),
  `scripts/verify_worktree_precondition_coverage.py` (#436) all untouched.
- I read `_build_amend_task` (~2105) and `append()` (~2317) in the working tree directly: **both
  unchanged**, as the exclusions require. The engine diff's only hunks are `state()` ~1611, the g1 helper
  block ~1674, and `render_human()` ~1737/~1774 — all g1 — plus the single g2 list-branch line.
- The one g2 engine line matches the exact string the g1 review flagged as a carry-over, so it is the
  authorized change and not an expansion.

I did not re-litigate g1.

## Evidence verdict

Sound, and independently reproduced. I ran a baseline before touching anything, reproduced R2, R4 and R5
each with the break asserted applied by grep first (per `CREW_CONTEXT`'s rule that a mutation which
silently matched nothing leaves a green suite reading exactly like a passing guard), reverted between
each, and added a fourth red-proof of my own for the flat-list carry-over. Every red was the *specific*
red the criterion names, not an incidental failure elsewhere.

The claimed wiring is real: R5 going red is behavioural proof that `_build_amend_task` is called at test
time, which is stronger than the implementer's grep count.

## Code/doc quality

Minimal and idiomatic. No new dependency in either file (`copy` was already imported at line 1 of the test
module). The failure messages name the offending field and state both remedies, replacing "the loop
asserted nothing" as required. Comment density and docstring shape match the surrounding classes
(`RenderAnchorsAndConstraints`, `Inv1CompletenessOracle`). The rewrite reduces duplication rather than
adding it: the fixture and the assertion path are extracted so all three tests drive the same objects.

Fowler pass (`.agent-work/b433-render-directives/g2-review/fowler-pass.json`, `verify_fowler_pass.py`
EXIT=0): 12 smells, **0 flagged**, 5 overridden with a logged standard and reason —
`large-class`, `feature-envy`, `shotgun-surgery`, `speculative-generality`, `comments-as-deodorant`. The
interesting ones:

- `feature-envy` — the test reaches into the private `E._build_amend_task`. Overridden by
  `CREW_CONTEXT`'s "define a guard by its consumer's behaviour, not by a hand-maintained list": the
  builder *is* the canonical enumeration, and the only public alternative (the schema table) is
  hand-authored prose that is currently stale on the very row at issue.
- `shotgun-surgery` — a new engine Task field now demands a second edit here. Overridden: the forced
  second edit *is* the guard, and the failure message directs it.
- `speculative-generality` — `_leaf_texts` handles tuples no Task field carries. Overridden: totality is
  the specified contract, and narrowing the branches back to the shapes in use today is precisely the
  #420 defect.

## Map impact verdict

- **Evidence supports claimed change:** yes. Each claimed property has a red I produced myself.
- **Constraints not violated:** `constraint:a-check-that-cannot-fail` is honored three ways and proven,
  not asserted. No new dependency. The `directives` passthrough and rendering are g1's and were not
  disturbed.
- **Notes match the diff:** yes, and they are not overstated. I spot-checked the two claims most likely to
  be flattering — that `_leaf_texts` shares nothing with the renderer, and that neither builder emits
  `anchors` — and both hold.
- **Decision candidates surfaced:** `decision:per-field-ledger-is-the-class-fix` is settled by the R4
  red-proof I reproduced; `decision:independent-extractor` is honored. Nothing required authority the
  implementer lacked.
- **Durable context routed:** yes. Three triage candidates are recorded in the survey
  (`triage_candidates` tc1-tc3) rather than fixed silently, and they match the ones the IMPLEMENTER_RESULT
  raised.

## Reconciliation check

No divergence needing Commander reconciliation. `docs/CHECKLIST_SCHEMA.md` is still stale on the
`directives` row (declares `[string] | null`; all 8 populated corpus blocks are `{name: {contract}}`), but
that is `g3-schema`'s and was correctly left alone. Worth noting for the Commander: this change deliberately
cuts the property against the **builder** instead of that table, so the table's staleness no longer silently
weakens the guard.

## Blockers

- None.

## Out-of-scope observations

1. **The residual limit is stated as a class but its live instance is not named where the reader is.** The
   class docstring says a template-only field is invisible to the superset assertion; it does not say that
   `anchors` is such a field today. I verified that it is — neither builder emits it. Adding four words to
   the docstring ("`anchors` is one today") would put the fact in front of the next person who edits the
   fixture. Non-blocking; the docstring as written is honest, not glossed.
2. **`append()` and `_build_amend_task` duplicate the Task shape by hand** (`scripts/checklist_engine.py`
   ~2105 and ~2317). They agree today, but the superset assertion reads only `_build_amend_task`, so a
   field added to `append()` alone stays invisible. One shared constructor removes the class of drift.
   (Survey `tc1`.)
3. **A field carried only by a shipped template is invisible to the property** — the stated residual. A
   check that walks the shipped templates' task objects for keys neither builder emits would close it
   mechanically. (Survey `tc2`.)
4. **Nothing checks `docs/CHECKLIST_SCHEMA.md`'s Task table against what the engine builds.** The new
   assertion binds the fixture to the builder, not the doc to the builder. A doc-vs-builder check would
   have caught the stale `directives` row itself. (Survey `tc3`.)

Observations 2-4 are pre-existing and match what the implementer raised; I confirmed each at its source
rather than repeating the claim.

## Workflow Feedback

- **Handoff gaps:** the close criteria are excellent and I would not change them, but criterion 6 and the
  **Evidence Produced** section ask for two different things about the same docstring. Criterion 6 asks
  that the residual limit be *stated*; Evidence Produced asks me to "confirm `anchors` is stated honestly
  in the docstring rather than glossed". The docstring states the general rule and not the `anchors`
  instance, so those two readings give different verdicts on the same text. I resolved it in favour of the
  numbered criterion, which is the binding one, and reported the gap as an observation. If a specific fact
  must appear in a specific artifact, say which artifact in the criterion itself.
- **Context rediscovered:** nothing material — the Map Anchors carried the symbol names and the two
  builder line numbers, and both were accurate after the line drift the handoff warned about. I did have
  to derive independently that neither builder emits `anchors`, which is the fact criterion 6 turns on;
  the implementer's own workflow feedback asks for exactly that line to be carried, and I second it.
- **Instructions improvised around:** a real conflict, worth fixing. `constellation-reviewer/SKILL.md`
  says to drive the survey through "the absolute path to this installed skill's bundled engine", while
  workbench `references/checklist-engine.md` §"Dogfooding on the skill-source repo" says that when the
  repo *is* the constellation-skills source you should drive from the repo's own vendored
  `scripts/checklist_engine.py`. This review is the case where that matters most: the repo's engine is the
  thing under review, and criterion 3 required me to **break it mid-run**. I drove the survey from the
  installed copy so my own engine state could not be corrupted by my R5 break, and I confirmed the two
  copies differ (installed also differs from `HEAD`). Neither document anticipates "the engine you drive
  is the engine you are breaking". One sentence in the dogfooding section — "if the review requires
  mutating the vendored engine, drive from the installed copy" — would settle it.
- **What would have made this easier:** the survey template hardcodes
  `"config_ref": "docs/agents/engine-config.json"`, which does not exist in this repo; the engine never
  complains. The g1 reviewer left it too. Either the engine should refuse an unresolvable `config_ref` or
  the template should stop naming a file nothing reads — right now it looks load-bearing and is not. This
  is the same friction the g2 implementer reported for `IMPLEMENTER_PLAN.template.json`, so it is now
  independently observed twice.

## Return status
`complete`
