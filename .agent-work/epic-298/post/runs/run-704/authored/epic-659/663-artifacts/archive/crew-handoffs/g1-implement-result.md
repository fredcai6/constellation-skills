# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1-implement (rework — attempt 2)`

## Completed slice
Fixed the `simplification_limits` cyclomatic-complexity BLOCKER from the g1 review by restructuring
the assertion shape of two test functions in `tests/unit/physics/layer2/test_grip_store.py`:
- `test_load_roundtrips_field_values` (was CC=22) — the 18 flat field-by-field asserts are replaced
  by a module-level `_OK_RECORD_EXPECTED_ROW` dict (field → expected value) compared in a single
  loop, plus one explicit `rain_flag` bool check kept separate (sqlite stores it as 0/1, not a
  Python bool, so it needs its own comparison form).
- `test_error_record_never_loses_a_failure` (was CC=20) — the 11 flat `is None` asserts on the
  fit-output fields are replaced by a module-level `_ERROR_RECORD_NULLED_FIELDS` list compared in a
  loop inside a new shared helper `_assert_error_record_shape(rec, expected_error)`, which also
  checks `fit_status`, `error`, and `fitted_at`. The store round-trip half of the test (upsert, has,
  load-by-status) is untouched.

No change to `src/physics/layer2/grip_store.py` — confirmed via `git status --porcelain` (file shows
as pre-existing untracked `??`, no diff, and it was never opened with an edit tool this session).

## Scope
**Files changed:**
- `tests/unit/physics/layer2/test_grip_store.py` (restructured, in place)

**Specific exclusions touched:** no — `src/physics/layer2/grip_store.py` untouched, confirmed by
`git status --porcelain` showing only the test file changed (plus `.agent-work/` workflow scratch).

## Behavior changed
No — this is a pure test-shape refactor. Same fields checked, same values expected, same two test
mechanisms (additive-migration untouched entirely; error-record shape + round-trip; ok-record
load round-trip), only the assertion form changed from a flat sequence to a table/loop. Test count
is unchanged at 9; no assertion coverage was dropped.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — no new structural change; this rework
  only tightens the existing sibling test file (`tests/unit/physics/layer2/test_grip_store.py`)
  added in the g1-implement attempt-1 slice, no production code touched.
- **Capabilities added/changed/affected:** none — `GripStore`/`GripEstimateRecord`/`error_record()`
  behavior is identical to attempt 1; only the test file's internal assertion structure changed.
- **Constraints/assumptions touched:** none newly relied on; `assumption:additive-only-migration`
  is unaffected (`test_migrate_missing_columns_additive_self_heal` was not in scope for this rework
  and was left byte-for-byte unchanged).
- **Decision candidates / resolved decisions:** none.
- **Claims/evidence produced:** `simplification_limits` now PASSes on both files (was 2 violations,
  now 0); `pytest` still 9/9 green.
- **Trust limitations / drift found:** none.
- **Triage candidates:** none beyond what the g1-review already routed (shared SQLite-record-store
  base extraction, `fit_status` literal-enum validation) — not re-litigated here, out of this
  rework's narrow scope.

## Test mode
**Required:** `test-after` — refactor existing tests, re-run to confirm still green + limits pass.
**Satisfied:** yes — no TDD red step was required or taken; the two restructured tests were run to
green immediately after editing, and the project-wide `simplification_limits` gate was run and
confirmed clean before considering the gate done.

## Evidence

```bash
cd /c/Programs/f1brainz-wt/epic659-663
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m src.utils.simplification_limits --paths tests/unit/physics/layer2/test_grip_store.py src/physics/layer2/grip_store.py
```
```
PASS (2 files checked)
```

```bash
cd /c/Programs/f1brainz-wt/epic659-663
"/c/Users/fredc/AppData/Local/Microsoft/WindowsApps/py.exe" -m pytest tests/unit/physics/layer2/test_grip_store.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1brainz-wt\epic659-663
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 9 items

tests\unit\physics\layer2\test_grip_store.py .........                   [100%]

============================== 9 passed in 0.43s ==============================
```

**Result:** pass — `simplification_limits` clean (0 violations, down from the reviewer's reported
`CC=20`/`CC=22`); all 9 tests still pass (same count as attempt 1's evidence, none dropped, none
added).

## TDD evidence, if required
Not applicable — test-after mode, restructuring existing already-green tests; no TDD red step
required or taken. Failing-to-passing wasn't the mechanism here: `simplification_limits` was the
thing driven from FAIL (2 violations) to PASS (0 violations); `pytest` was green before and stayed
green after.

## Docs/contracts touched
- none — pure test-file internal restructuring, no committed doc/contract references this file's
  internal shape.

## Assumptions
- `_approx()` (wraps a value in `pytest.approx` only if it's a `float`) is a new small helper local
  to this test file — used only inside `test_load_roundtrips_field_values`'s loop so integer/string/
  None fields still compare with plain `==` (exact) while float fields keep the same tolerance the
  original flat asserts used (`pytest.approx(...)`).
- Kept `rain_flag` out of the `_OK_RECORD_EXPECTED_ROW` dict and asserted it separately with
  `bool(row["rain_flag"]) is False`, exactly matching the original test's own separate
  `bool(...)`-cast assertion (sqlite round-trips a Python `bool` as an integer 0/1, not a bool, so
  it needs its own cast, not a `==` comparison against `True`/`False` inside the generic loop).
- The additive-migration test (`test_migrate_missing_columns_additive_self_heal`) was not touched at
  all — it was not named as over-limit by the review and the handoff's Constraints section
  explicitly protects its mechanism; confirmed via a diff of the full file that only the two named
  functions (plus their new small module-level helpers) changed.

## Stop conditions hit
None. The fix stayed entirely inside `tests/unit/physics/layer2/test_grip_store.py`; no need arose
to touch `grip_store.py`, and test coverage (field count, value count, mechanism) was preserved, not
reduced.

## Out-of-scope observations
None beyond what the prior g1-review already routed as Triage candidates (shared SQLite-record-store
base extraction; `fit_status` literal-enum validation) — unchanged by this rework, not re-surfaced.

## Workflow Feedback
- **Handoff gaps:** none — the rework handoff's Task, Protected Intent, Test Mode, Close Criteria,
  Allowed Scope, Specific Exclusions, Constraints, Required Evidence, and Verification Commands were
  all concrete and sufficient as given; no field needed inference or improvisation.
- **Context rediscovered:** the WindowsApps `py.exe` full-path requirement (documented explicitly in
  the rework handoff itself, and already known from attempt 1's own Workflow Feedback) was already
  flagged going in — no fresh rediscovery needed this time, the handoff carried it forward correctly.
- **Instructions improvised around:** none. Built a fresh engine plan
  (`.agent-work/663-grip-g/crew-handoffs/g1-implement-rework-plan.json`) scoped to this rework rather
  than reopening attempt 1's already-`complete`/released plan (`g1-implement-plan.json`) — attempt
  1's plan belongs to a finished, released session and reopening it would have cascaded its
  already-satisfied gates back to `pending` for a fix that only concerns one narrow slice; a new
  plan with its own three gates (context, fix, evidence) was the natural fit and the skill template
  supports this directly (a fresh `IMPLEMENTER_PLAN` per implementer dispatch).
- **What would have made this easier:** none — this was a narrow, well-scoped, mechanical fix and
  the handoff's own suggested fix shape (expected-vs-actual dict/loop, or `@pytest.mark.parametrize`)
  matched exactly what `simplification_limits` needed.

## Return status
`complete`
