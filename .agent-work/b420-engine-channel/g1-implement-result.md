# Implementation Result

## Assigned gate
`g1-implement` (issue #420, epic #418 workstream B)

## Completed slice
Fixed both defects in `scripts/checklist_engine.py`'s `current`/RAIL projection and added the
required regression coverage:

1. **RAIL echo de-duplication, `current` verb only.** `_rail(point, cl)` now substitutes a short
   pointer (`"the ACTIVE line above"`) for the `{imperative}` token in the mid-flight rail **only**
   when `point == "current"`. Every other railed verb (`claim`, `start`, `advance`, `attest`,
   `attach`) is untouched — same code path, same full-imperative substitution as before.
2. **Render `anchors` and `constraints`.** `state()` now reads `t.get("anchors")` and
   `t.get("constraints")` into the `active` dict (pure passthrough, no side effect). `render_human()`
   renders a `constraints:` block (list of strings) and an `anchors:` block when populated; emits
   nothing when absent/empty.
3. **Completeness property test.** Added `TaskFieldCompleteness` — enumerates a fully-populated
   fixture task's own dict keys minus a documented, justified exclusion set, and asserts every
   remaining populated field's content appears in `current()`'s output. A genuinely new field added
   to `Task` later and left unrendered is caught by default (not opted in by name).

**Rework 1/3 (post-integrate-attempt, Commander's independent verification):** the Commander
reproduced a real defect against my first landing: `_render_anchor_lines()` handled `{category:
[str]}` and flat `[str]`, but not the THIRD live-corpus shape, `{category: "<plain string>"}` (a
dict whose value is a bare string) — used by `skills/commander/templates/EXECUTE_PLAN.template.json`'s
own shipped `g1-review` gate (`"anchors": {"inherits": "g1-implement anchors — review verifies..."}`).
`for item in (items or [])` iterated the string's *characters*, exploding one sentence into ~80 lines
of one-letter-per-line garbage — worse than the pre-#420 silent drop, since it actively rendered
noise instead of nothing. Fixed via a new `_anchor_category_items()` helper (treats a bare string as
one item, not an iterable); added `test_anchors_render_when_dict_value_is_a_plain_string`, sourced
verbatim from the shipped template's g1-review anchors text per the Commander's request. See the
rework TDD evidence below.

## Scope
**Files changed:**
- `scripts/checklist_engine.py` — `_rail()` (verb-aware dedup), `state()` (+anchors/+constraints
  passthrough), `render_human()` (+`_render_anchor_lines()` + `_anchor_category_items()` helpers,
  +constraints/anchors rendering, docstring citation fixed)
- `tests/test_checklist_engine.py` — `DoctrineRail.test_rail_mid_flight` updated for the new dedup
  behavior + 1 sibling non-current assertion + 1 dispatch-level dedup test; new
  `RenderAnchorsAndConstraints` class (6 tests, including the rework 1/3 regression test for the
  dict-with-string-value anchor shape); new `TaskFieldCompleteness` class (1 test)

**Specific exclusions touched:** no — `_check_condition`/invariant-evaluation code untouched
(confirmed via `git diff scripts/checklist_engine.py | grep _check_condition`, no hits); workstream
C's relocation work untouched; the DIGEST-staleness observation not investigated; RAIL-echo
compliance-neutrality not evaluated.

`tests/test_spine_rail.py` — read, not touched. It exercises a different "mid-flight" concept
(`scripts/hooks/spine_rail.py`'s Stop-hook nudge state), unrelated to `_rail_position()`/
`_RAIL_STRINGS`; confirmed by grep (no `_rail`/`RAIL_STRINGS`/`E._rail` references in that file).

## Behavior changed
Yes. On the `current` verb, the active gate's imperative now appears exactly once in the combined
CLI-wrapped output (was twice). All other railed verbs are byte-identical to before. `current`'s
output now includes populated `constraints`/`anchors` content when present on the active gate; output
is unchanged when those fields are absent or empty.

## Map Impact
- **Structural anchors touched:** `scripts/checklist_engine.py: _rail()` (~266-296, now verb-aware),
  `state()` (~1548-1591, +anchors/+constraints), `render_human()` (~1600-1651, +`_render_anchor_lines()`
  helper, +constraints/anchors rendering blocks) — matches the inbound structural anchor exactly;
  `_rail_position()`/`_rail_prefix()`/`dispatch()`'s `RAIL_VERBS` call site were read but needed no
  changes (the verb name was already threaded through to `_rail()` via `_rail_prefix(v, cl)` →
  `_rail(point, cl)`, so no new plumbing was required).
- **Capabilities added/changed/affected:** the `current` projection's completeness contract
  (`docs/CHECKLIST_ENGINE_DESIGN.md` INV-1) — `current` is now closer to a true superset of gate
  content; the RAIL dedup makes `current`'s own output non-redundant.
- **Constraints/assumptions touched:** `_RAIL_STRINGS` dict values verified byte-identical (only the
  substituted value changed, only for `point == "current"`); `state()` purity (INV-2) honored — the
  new reads are `dict.get()` passthroughs, no side effect, no check re-run.
- **Decision candidates / resolved decisions:** none reopened. The vestigial-fields and verb-aware-
  dedup-shape decisions from the handoff were followed as given, not revisited.
- **Claims/evidence produced:** all three "Evidence expectations" claims from the handoff's Map
  Anchors are now backed by the tests below (RAIL dedup exact-once, anchors/constraints render when
  populated, completeness property holds for a fully-populated fixture).
- **Triage candidates:** (1) `directives` is in the same unrendered-defect class as
  anchors/constraints — `state()`/`render_human()` never surface it either — but it was outside this
  issue's authorized fix scope ("the two new fields"); flagged in-code
  (`TaskFieldCompleteness._EXCLUDED_FIELDS` comment) and here. (2) `anchors` is real, documented-only-
  in-prose (`commander-core.md`) Task content not listed in `docs/CHECKLIST_SCHEMA.md`'s Task field
  table — the doc gap the handoff already named; still open.

## Test mode
**Required:** `test-first (TDD)`
**Satisfied:** yes — both slices were red before green (see below), each driven through the
implementer's own engine plan (`m1-rail-red` → `m2-rail-green`, `m3-render-red` → `m4-render-green`),
with the RED runs captured and attested as evidence before any fix code was written.

## Evidence

```bash
cd C:/Programs/constellation-skills-wt/epic418-b-420 && python -m pytest tests/test_checklist_engine.py tests/test_spine_rail.py -q
```
```
........................................................................ [ 18%]
........................................................................ [ 31%]
........................................................................ [ 49%]
.................................................................. [ 66%]
........................................................................ [ 84%]
.............................................................            [100%]
397 passed, 24 subtests passed in 14.94s
```
**Result:** pass. (Pre-change baseline, independently re-run this session: 388 passed, 24 subtests.
Net +9 new tests, 0 regressions — the +8 from the initial landing plus +1 from the rework 1/3
regression test below.)

## TDD evidence

### Slice 1 — RAIL dedup

**RED** (`python -m pytest tests/test_checklist_engine.py -k "DoctrineRail" -q`, against unmodified
`_rail()`):
```
.F...F......                                                             [100%]
FAILED tests/test_checklist_engine.py::DoctrineRail::test_dispatch_current_shows_imperative_exactly_once_mid_flight
  AssertionError: 2 != 1 : RAIL: A working solution is the MIDDLE of this run ... Next: do g2. Run it.

  ACTIVE g2 [in-progress] ... do g2
  next: advance g2
FAILED tests/test_checklist_engine.py::DoctrineRail::test_rail_mid_flight
  AssertionError: 'do g2' unexpectedly found in '\n\nRAIL: ... Next: do g2. Run it.'
2 failed, 10 passed, 320 deselected in 1.09s
```
The third new assertion (`test_rail_mid_flight_non_current_verb_keeps_full_imperative`) already
passed pre-fix — confirming the duplication is real only on `current`, exactly as the handoff's
constraints stated.

**GREEN** (`python -m pytest tests/test_checklist_engine.py -k "DoctrineRail or RailPositionOrdering" -q`):
```
..................                                                       [100%]
18 passed, 314 deselected in 1.10s
```

### Slice 2 — anchors/constraints rendering + completeness

**RED** (`python -m pytest tests/test_checklist_engine.py -k "RenderAnchorsAndConstraints or TaskFieldCompleteness" -q`,
against unmodified `state()`/`render_human()`):
```
.FFF.F                                                                   [100%]
FAILED ...::test_anchors_render_when_present_dict_shape - 'scripts/foo.py: bar()' not found in ...
FAILED ...::test_anchors_render_when_present_list_shape - 'a flat anchor note' not found in ...
FAILED ...::test_constraints_render_when_present - 'stay pinned to X' not found in ...
FAILED ...::test_every_populated_field_renders_for_a_fully_populated_gate
  AssertionError: 'CONSTRAINT_UNIQUE_TEXT' not found in ...
4 failed, 2 passed, 332 deselected in 1.07s
```
The 2 pre-existing passes were the "absent/empty renders unchanged" goldens (correctly unaffected).
`TaskFieldCompleteness` failed specifically on the constraint/anchor markers — its `PRECOND_UNIQUE_TEXT`
/`POSTCOND_UNIQUE_TEXT` dedicated assertions already passed, confirming the loop mechanics were sound
and the only real gap was anchors/constraints.

**GREEN** (`python -m pytest tests/test_checklist_engine.py -k "RenderAnchorsAndConstraints or TaskFieldCompleteness or GoldenOutputBriefing" -q`):
```
..............                                                           [100%]
14 passed, 324 deselected in 0.44s
```

### Rework 1/3 — dict-with-string-value anchor shape (Commander's independent verification finding)

**RED** (`python -m pytest tests/test_checklist_engine.py -k "test_anchors_render_when_dict_value_is_a_plain_string" -q`,
against the code as first landed — i.e. `_render_anchor_lines()` before adding
`_anchor_category_items()`):
```
F                                                                        [100%]
FAILED ...::test_anchors_render_when_dict_value_is_a_plain_string
  AssertionError: 'inherits: g1-implement anchors — review verifies the change against the same
  structural/capability/constraint/decision/evidence anchors' not found in 'ACTIVE g1-review
  [pending] — do g1-review\nanchors:\n  inherits: g\n  inherits: 1\n  inherits: -\n  inherits: i\n
  inherits: m\n  ... [character-by-character explosion, ~90 lines total] ...\nnext: start g1-review'
1 failed, 338 deselected in 0.65s
```
Reproduced exactly the Commander's report: the fixture is `{"anchors": {"inherits":
"g1-implement anchors — review verifies the change against the same structural/capability/
constraint/decision/evidence anchors"}}` — verbatim from the shipped
`skills/commander/templates/EXECUTE_PLAN.template.json`'s g1-review gate (line 41) — and the old
`for item in (items or [])` iterated the string's characters.

**GREEN** (`python -m pytest tests/test_checklist_engine.py -k "RenderAnchorsAndConstraints or TaskFieldCompleteness or GoldenOutputBriefing" -q`,
after adding `_anchor_category_items()`):
```
...............                                                          [100%]
15 passed, 324 deselected in 0.46s
```

**Refactor while green:** no — change stayed minimal; nothing warranted restructuring.

## Load-bearing samples (Close Criteria)

**`current`-through-`dispatch()`, mid-flight fixture (g1 complete, g2 in-progress, g3 pending),
post-fix:**
```
RAIL: A working solution is the MIDDLE of this run — you are 2 steps from done. Next: the ACTIVE line above. Run it.

ACTIVE g2 [in-progress] — do g2
next: advance g2
```
Imperative substring (`"do g2"`) count: **1** (was 2 before the fix).

**`E._rail("start", cl)`, same fixture, post-fix:**
```
'\n\nRAIL: A working solution is the MIDDLE of this run — you are 2 steps from done. Next: do g2. Run it.'
```
Full imperative (`"do g2"`) present, unchanged.

## `git diff --stat`
```
 scripts/checklist_engine.py    |  76 ++++++++++++-
 tests/test_checklist_engine.py | 244 ++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 314 insertions(+), 6 deletions(-)
```
(Updated post-rework 1/3; only the two allowed files changed.) `tests/test_spine_rail.py` untouched
(confirmed unaffected by inspection — no `_rail`/`RAIL_STRINGS` reference in that file).

## Docs/contracts touched
- `scripts/checklist_engine.py`'s `render_human()` docstring — fixed the stale
  `tests/test_checklist_engine.py:818` citation (an unrelated `require_session` lease test) to point
  at `GoldenOutputBriefing` (~3779 on), per the handoff's fix-if-convenient item. It fit naturally in
  the same docstring edit that documented the new anchors/constraints behavior, so no separate pass
  was needed.

## Assumptions
- The short pointer text for the deduped `current` mid-flight rail is `"the ACTIVE line above"` — the
  handoff graded the exact wording a `guess`/implementation-slice call (mission frame decision
  anchors), settled here by landing it and confirming the pinned + new rail tests pass.
- `anchors` rendering now handles all three shapes confirmed in the live corpus (`{category: [str]}`
  dict, flat `[str]`, and `{category: str}` dict — the last one added in rework 1/3, see below); an
  unrecognized fourth shape renders nothing rather than guessing at a format the corpus doesn't use
  (documented in `_render_anchor_lines()`).
- The `TaskFieldCompleteness` exclusion set (`id`, `status`, `preconditions`, `postconditions`,
  `status_detail`, `rework_count`, `result`, `finding`, `evidence`, `why_exempt`, `child_checklist`,
  `context_refs`, `title`, `directives`) is a judgment call, documented in-code with per-field
  reasoning — not authorized by the handoff to be settled any other way, and no handoff text
  contradicted it.

## Stop conditions hit
None. No need to touch `_check_condition`; all RED runs (including the rework 1/3 regression test)
failed for the intended reason; the verb-aware dedup shape held up exactly as the handoff specified
(no other verb needed the pointer); no decision outside the Authority section was required. The
rework itself (below) was a real defect fixed via the engine's `reopen` rework mechanism, not a stop
condition — it stayed within the same allowed-scope files and required no new authority.

## Out-of-scope observations
- **`directives` is in the same unrendered-defect class as anchors/constraints.** `state()` never
  reads it either, and it is documented in `docs/CHECKLIST_SCHEMA.md` as `"forced primitive
  specifics handed down"` — semantically similar to `constraints`. Not fixed here because the handoff
  explicitly caps this fix's scope to "the two new fields" (anchors + constraints). Recommend a
  follow-up issue for `directives` rendering, same shape as #420.
- **`anchors` is still absent from `docs/CHECKLIST_SCHEMA.md`'s Task field table** (documented only in
  `commander-core.md` prose) — the handoff already named this doc gap as out of scope; still open,
  worth a Cartographer/Triage follow-up now that the engine itself treats `anchors` as first-class
  content.

## Workflow Feedback

- **Handoff gaps:** none of substance. The handoff was unusually complete — it even pre-empted the
  exact `directives` ambiguity I hit (the "negative/partial result... reportable as a scoped, honest
  finding" clause in Constraints told me exactly how to handle discovering a third unrendered field
  mid-run instead of guessing).
- **Context rediscovered:** the concrete `anchors` shape (dict-of-category-lists vs. flat list) — the
  handoff said "real corpus content" but didn't give the shape; I derived it directly from this run's
  own `execute.json` g1-implement gate plus a quick grep across archived `execute.json` files
  (`dict:structural,capability,constraint,decision,evidence`, `dict:inherits`, and bare `list`
  variants all appear). Worth citing the concrete shape(s) in a future handoff's Map Anchors section
  if the pattern recurs.
- **Process gap, self-identified honestly:** my own shape-survey grep (used to write the assumption
  above) reported `dict:inherits` as one of the observed shapes — I saw that label and treated it as
  "a dict shape, same handling as the others," but never actually dereferenced the VALUE at
  `dict:inherits`'s key to check whether it was a list or a bare string. It was a bare string
  (`skills/commander/templates/EXECUTE_PLAN.template.json`'s g1-review gate). My own evidence surfaced
  the exact clue and I didn't chase it one level deeper — the Commander's independent verification
  caught what my own survey should have. Lesson for future shape-inventory work: when a grep reports a
  shape label, open at least one concrete example and inspect its actual value type, not just the
  label, before calling a rendering path "covers the corpus."
- **Instructions improvised around:** none — `_rail_prefix(v, cl)` already threads the triggering verb
  name into `_rail(point, cl)` as `point`, so no new plumbing was needed to make the dedup verb-aware;
  I confirmed this by reading `dispatch()`'s call site before assuming I'd need to change signatures.
- **What would have made this easier:** nothing significant. The mission frame's cold-critic notes
  (in the Commander's `notes-b420.md`, which I read for context though it wasn't formally part of the
  handoff) were genuinely useful — they pre-solved the verb-aware-dedup design question before I even
  reached it.

## Return status
`complete`
