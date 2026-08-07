# Implementation Result

## Assigned gate
`g2-implement` (execute.json, work-id `b433-render-directives`, issue #433)

## Completed slice

`class TaskFieldCompleteness` in `tests/test_checklist_engine.py` can now FAIL for the shapes the corpus
really carries. All five handoff changes are in, plus the g1-review carry-over in the engine's
`_render_directive_lines` flat-list branch.

1. **Un-excluded the field.** `"directives"` is out of `_EXCLUDED_FIELDS`; its `KNOWN GAP` comment is
   replaced by a note that as of #433 `state()` reads it and `render_human()` prints it, so the generic
   loop carries it like anchors/constraints. The other 13 exclusions keep their stated per-entry reasons
   verbatim — none dropped, none added.
2. **`_flatten` -> `_leaf_texts`, total.** Recurses dicts, lists and tuples to any depth and stringifies
   scalars. Returns `[]` only for `None` and empty containers. Independent of the renderer's
   `_directive_leaf` / `_render_directive_lines` — no import, no shared call.
3. **`checked_any` -> a per-field ledger.** The loop records the fields it actually asserted on and
   `assertEqual`s that set against the set of populated non-excluded fields. The message names the
   offending field(s): `populated field(s) ['directives'] were carried by the loop but asserted NOTHING`.
4. **Superset assertion against the engine's own builder.**
   `test_fixture_carries_every_field_the_engines_task_builder_builds` calls `E._build_amend_task(...)`
   live and asserts `set(built) - set(fixture) == set()`. The builder is asked for its keys rather than
   having them re-listed, so the enumeration cannot drift. The class docstring states the residual limit:
   this closes the hole for fields the ENGINE introduces; a field introduced only by a template and built
   by neither `_build_amend_task` nor `append()` still needs a human to add it to the fixture.
5. **In-suite negative self-test.** `test_the_property_fails_when_a_populated_field_is_unrendered` drives
   `_assert_every_populated_field_renders` — the same helper the positive test drives, not a copy —
   against a real `E.current()` render of the same gate with `directives` set to `None`, inside
   `assertRaises(AssertionError)`, and asserts the message contains `directives`.

Supporting change inside the class: the fixture's `directives` moved from a flat `[str]` to the nested
contract-dict shape all 8 populated corpus blocks carry, so the recursion is load-bearing. The fixture and
the assertion path are factored into `_fully_populated_gate()` and
`_assert_every_populated_field_renders()` so the positive test, the superset test and the negative test all
work the same objects.

**Carry-over (the only engine edit).** `_render_directive_lines`'s flat-list branch was
`[f"  {item}" for item in directives if isinstance(item, str)]` — a non-string item was silently dropped,
contradicting the helper's own docstring rule and diverging from `_render_anchor_lines`, which does not
filter its list branch. It is now `[f"  {_directive_leaf(item)}" for item in directives]`, total, with the
docstring's rule statement updated to match. TDD red observed first (below).

## Scope

**Files changed:**
- `C:/Programs/constellation-skills-wt/r418-433/tests/test_checklist_engine.py`
- `C:/Programs/constellation-skills-wt/r418-433/scripts/checklist_engine.py`

**Specific exclusions touched:** no. `docs/CHECKLIST_SCHEMA.md` untouched (g3-schema owns it, and it is
still wrong about the `directives` type — see out-of-scope observations). No other engine change:
`git diff -U0 scripts/checklist_engine.py` shows hunks only at `state()` ~1611, the g1 helper block
~1674, and `render_human()` ~1737/~1774. `_build_amend_task` (~2102) and `append()` (~2314) are untouched.
`scripts/collect_feedback.py`, `episodes/`, `scripts/verify_worktree_precondition_coverage.py`, and the
gate schema were not touched.

## Behavior changed

Yes, in two places.

- Test-side: the completeness property now asserts on `directives` and on any nested shape, and fails by
  name when a populated field asserts nothing or when the engine's Task shape outgrows the fixture.
- Engine-side: a flat `directives` list carrying a non-string item now renders every item instead of
  dropping the non-string ones. `["file X", 17, False]` renders `  file X` / `  17` / `  false`.

The `ACTIVE` first line is byte-identical; `GoldenOutputBriefing` and `ShippedTemplates` are green.

## Map Impact

- **Structural anchors touched:** `tests/test_checklist_engine.py` — `class TaskFieldCompleteness`
  (rewritten in full: `_EXCLUDED_FIELDS`, `_flatten` -> `_leaf_texts`, new `_fully_populated_gate`,
  `_assert_every_populated_field_renders`, plus two new tests), `class RenderDirectives` (one added test).
  `scripts/checklist_engine.py` — `_render_directive_lines` list branch and docstring only.
- **Capabilities added/changed/affected:** the Task field contract is now checked against the **engine's
  own builder** rather than only against `docs/CHECKLIST_SCHEMA.md`'s hand-authored Task table. That
  substitution (cold-plan-critic finding 1) is now mechanical: `_build_amend_task` is called at test time.
  Engine-side, `_render_directive_lines` is total over the flat-list shape.
- **Constraints/assumptions touched:** `constraint:a-check-that-cannot-fail` — honored and now enforced
  three ways (total extractor, per-field ledger, superset assertion) with an in-suite negative self-test
  as the durable proof.
- **Decision anchors:** `decision:per-field-ledger-is-the-class-fix` — settled by the R4 red-proof below,
  which fails by name for a populated field whose value flattens to nothing.
  `decision:independent-extractor` — honored; `_leaf_texts` shares no code with the renderer.
- **Claims/evidence produced:**
  `claim:the-completeness-property-fails-when-a-populated-field-is-unrendered` — proven twice: in-suite by
  `test_the_property_fails_when_a_populated_field_is_unrendered`, and by hand by the R2/R4/R5 captures.
- **Trust limitations:** `docs/CHECKLIST_SCHEMA.md`'s Task table remains stale on the `directives` row;
  nothing checks that table against what runs. The property is deliberately not cut against it.
- **Triage candidates:** see out-of-scope observations.

## Test mode

**Required:** test-first (strong sense — the red-proofs are the deliverable)
**Satisfied:** yes. Three by-hand red-proofs run against the real suite with each break reverted before the
next, plus a TDD red observed for the carry-over before the engine line was changed.

## Evidence

### R2 — extractor returns `[]` for dicts (the old `_flatten` behaviour)

Break: `tests/test_checklist_engine.py`, `_leaf_texts` dict branch -> `return []`.

```bash
cd C:/Programs/constellation-skills-wt/r418-433
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
1 failed, 348 passed, 30 subtests passed in 13.69s
EXIT=1
```

RED, and it is the **ledger set-mismatch** that fired, not a green run — which is what the handoff
required. Capture: `.agent-work/b433-render-directives/evidence/g2-r2-extractor-blind-to-dicts.txt`.
Break reverted before R4.

### R4 — a populated fixture field whose value flattens to nothing

Break: `_fully_populated_gate()` += `t["throwaway_field"] = {"nested": None}` (truthy, yields no leaves).

```bash
cd C:/Programs/constellation-skills-wt/r418-433
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py; echo "EXIT=$?"
```

```
tests\test_checklist_engine.py:4293: in _assert_every_populated_field_renders
    self.assertEqual(
E   AssertionError: Items in the second set but not the first:
E   'throwaway_field' : populated field(s) ['throwaway_field'] were carried by the loop but asserted NOTHING -- _leaf_texts read no text out of them, so current()'s output was never checked against their content
=========================== short test summary info ===========================
FAILED tests/test_checklist_engine.py::TaskFieldCompleteness::test_every_populated_field_renders_for_a_fully_populated_gate
1 failed, 348 passed, 30 subtests passed in 17.84s
EXIT=1
```

RED, **by name**. Capture:
`.agent-work/b433-render-directives/evidence/g2-r4-populated-field-flattens-to-nothing.txt`.
Break reverted before R5.

### R5 — a field added to `_build_amend_task` and NOT to the fixture

Break: `scripts/checklist_engine.py`, `_build_amend_task()` +=
`"escalation_notes": op.get("escalation_notes")`.

```bash
cd C:/Programs/constellation-skills-wt/r418-433
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py; echo "EXIT=$?"
```

```
        missing = set(built) - set(self._fully_populated_gate())
>       self.assertEqual(
E       AssertionError: Items in the first set but not the second:
E       'escalation_notes' : the engine's Task builder _build_amend_task now emits ['escalation_notes'], which this class's fixture does not carry, so the completeness loop would never see the field -- add it to _fully_populated_gate() with content the briefing should show, or to _EXCLUDED_FIELDS with a stated reason. append() mirrors the same shape (scripts/checklist_engine.py)

tests\test_checklist_engine.py:4326: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_checklist_engine.py::TaskFieldCompleteness::test_fixture_carries_every_field_the_engines_task_builder_builds
1 failed, 348 passed, 30 subtests passed in 12.62s
EXIT=1
```

RED, **by name**, and the failing test is the superset assertion. Capture:
`.agent-work/b433-render-directives/evidence/g2-r5-engine-field-forgotten-in-fixture.txt`.
Break reverted.

### Final green, every break reverted

```bash
cd C:/Programs/constellation-skills-wt/r418-433
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py; echo "EXIT=$?"
```

```
349 passed, 30 subtests passed in 16.85s
EXIT=0
```

Baseline before this gate was 346; +3 tests (the superset test, the negative self-test, the flat-list
carry-over test).

### Working tree clean of the breaks

```bash
cd C:/Programs/constellation-skills-wt/r418-433 && git diff --stat -- scripts tests docs
```

```
 scripts/checklist_engine.py    |  67 +++++++-
 tests/test_checklist_engine.py | 373 ++++++++++++++++++++++++++++++++++++-----
 2 files changed, 394 insertions(+), 46 deletions(-)
```

Only the two intended source files; `docs/` shows nothing. `git diff --stat` across the whole tree adds
only the engine work files this gate's own run wrote
(`.agent-work/b433-render-directives/execute.json`, `spine.json`, `spine.json.journal`).
Residual-break sweep is empty:

```bash
grep -rn "RED-PROOF BREAK\|throwaway_field\|escalation_notes" scripts tests   # -> no matches
```

### Wiring grep

```bash
grep -rn "_build_amend_task" --include=*.py C:/Programs/constellation-skills-wt/r418-433/tests
```

**Count: 5** — one live call site (`tests/test_checklist_engine.py:4300`, `built = E._build_amend_task({...})`),
one in the assertion message, one in a comment, two in the class docstring. Non-zero, so change (4) really
reaches the engine's builder. R5's red is the behavioural confirmation that it does.

### Confirmatory

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py \
  -k "GoldenOutputBriefing or ShippedTemplates or RenderDirectives or TaskFieldCompleteness"
# 20 passed, 329 deselected, 24 subtests passed in 0.32s ; EXIT=0
```

`GoldenOutputBriefing` and `ShippedTemplates` green, so the `ACTIVE` first line is unchanged.

### Deliverable path check

`git check-ignore -v` exits **1** (not ignored) for `tests/test_checklist_engine.py`,
`scripts/checklist_engine.py`, and the evidence captures under
`.agent-work/b433-render-directives/evidence/`. Nothing committed, per the handoff.

## TDD evidence, if required

- **Failing test observed (carry-over):**
  `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py -k test_flat_list_with_a_non_string_item_renders_every_item`
  -> `1 failed, 348 deselected`, `EXIT=1`. `AssertionError` at `tests/test_checklist_engine.py:4068`; the
  diff shows the rendered output missing both non-string items (`+   17`, `+   false`) — the silent drop
  the g1 reviewer named.
- **Passing test observed:** after routing the branch through `_directive_leaf`, full suite
  `349 passed, 30 subtests passed`, `EXIT=0`.
- **Refactor while green:** yes — the fixture and the assertion path were extracted into
  `_fully_populated_gate()` / `_assert_every_populated_field_renders()` with the suite green.

## Docs/contracts touched
- None. `docs/CHECKLIST_SCHEMA.md` is g3-schema's, deliberately untouched.
- One engine docstring changed: `_render_directive_lines`'s flat-list rule statement, so the prose matches
  the now-total branch.

## Assumptions

- **The fixture's `directives` should be the nested contract-dict shape.** The handoff says the total
  extractor "is what makes the nested-dict shape assertable at all"; a flat `[str]` fixture would have
  passed under a non-recursive extractor and proved nothing, and R2 would not have gone red on
  `directives`. Changed accordingly.
- **The negative self-test strips `directives` by re-rendering, not by editing the output text.** It sets
  `directives` to `None` on a copy and takes a real `E.current()` render, then feeds that output together
  with the still-populated task. That is a genuine pre-#433 briefing rather than line surgery on a string.
- **`_leaf_texts` uses `str()` for scalars, not JSON spelling.** The one divergence from the renderer is a
  bool leaf (`True` vs `true`). No field currently reachable by the loop carries one, and the divergence
  would surface as a loud red rather than a silent green — the safe direction. Noted in the method
  docstring so the next reader is not surprised.
- **`_leaf_texts` recurses dict *values*, not keys.** Keys are structure, not content; including them
  would assert the renderer prints every key name, which is a stricter contract than the handoff asked
  for.
- **`_fully_populated_gate` / `_assert_every_populated_field_renders` were extracted at the first slice**
  rather than at the negative-self-test slice, because the superset test needs the fixture helper. Same
  end state, one less round of churn.

## Stop conditions hit
- None. Allowed scope was not exceeded, no exclusion was touched, all three red-proofs produced real reds,
  and the wiring grep count is non-zero.

## Out-of-scope observations

- **`docs/CHECKLIST_SCHEMA.md` is wrong about the `directives` type** — it declares `[string] | null`
  while all 8 populated corpus blocks are `{name: {contract}}`. Left for `g3-schema` as the handoff
  directs. Noting only that the superset assertion now makes the *builder* the checkable enumeration, so
  the schema table's staleness no longer silently weakens this property.
- **Nothing checks `docs/CHECKLIST_SCHEMA.md`'s Task table against `_build_amend_task`.** The new
  assertion binds the fixture to the builder, not the doc to the builder. A doc-vs-builder check would
  close the remaining drift, and would have caught the `directives` row itself. Triage candidate.
- **`append()` and `_build_amend_task` duplicate the Task shape by hand** (`scripts/checklist_engine.py`
  ~2102 and ~2314). They agree today, and the new assertion only reads `_build_amend_task`, so a field
  added to `append()` alone would still be invisible. One shared constructor would remove the class of
  drift. Triage candidate.
- **The residual limit is real, not theoretical.** A field carried only by a shipped template JSON —
  `anchors` is exactly such a field today; neither builder emits it — is invisible to the superset
  assertion. `anchors` is in the fixture only because a human put it there. A check that walks the shipped
  templates' task objects for keys neither builder emits would close that too. Triage candidate.

## Workflow Feedback

- **Handoff gaps:** the **Test Mode** section names R2, R4 and R5 with no R1 or R3. Whatever those were,
  they were dropped somewhere upstream and the numbering was left with holes, so I could not tell whether
  two red-proofs had been deliberately cut or accidentally lost from the list I was meant to run. I ran the
  three that are named. If the numbering carries meaning across gates, say so; if not, renumber.
- **Handoff gaps (second):** **Test Mode** says "break the world three ways *by hand*" while **Close
  Criteria** says only "R2, R4 and R5 each produced a real, pasted red". The in-suite negative self-test
  of change (5) covers the same ground as one of the by-hand reds, and it was not obvious whether the
  negative self-test was meant to substitute for a by-hand proof or sit alongside it. I did both. One
  sentence saying "the in-suite test is the durable proof, the by-hand reds are this gate's evidence"
  would have removed the question.
- **Context rediscovered:** the engine CLI requires `--session-id <id>` on every mutating verb after
  `claim`. Neither the implementer skill nor `references/global-everyone.md`'s "Engine verbs" section
  mentions it; I learned it from three consecutive `REFUSED: checklist is owned by active session` errors.
  The refusal message is good — it names the fix — but the doctrine that tells you to `claim` first should
  say what `claim` hands you.
- **Instructions improvised around:** `templates/IMPLEMENTER_PLAN.template.json` hardcodes
  `"config_ref": "docs/agents/engine-config.json"`, which does not exist in this repo. The engine did not
  complain, so I mirrored the g1 plan and left it. Either the template should not name a file the engine
  never reads, or the engine should refuse a `config_ref` that does not resolve — right now it is a field
  that looks load-bearing and is not.
- **What would have made this easier:** the handoff's **Map Anchors** gave the fixture's key set as the
  thing to compare against `_build_amend_task`, but not the fact that **`anchors` is in neither builder**.
  That is the single most load-bearing detail for sizing change (4)'s residual limit honestly, and I had to
  derive it by reading both builders. One line — "the fixture's `anchors` key comes from a template, not
  from either builder" — would have carried it.

## Return status
`complete`
