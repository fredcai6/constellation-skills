# tests.test_checklist_engine:Inv3AmendSubOpEnumeration
class, tests/test_checklist_engine.py:2258, 60 lines

```python
class Inv3AmendSubOpEnumeration(TestCase)
```

Same GENERATED-grid rigor as `Inv3RecoveryEnumeration`, applied to

`amend`'s status-guarded sub-ops (Reviewer BLOCK, g3-review rework 1:
these were the actual hole in the original exclusion claim). The grid is
amend's own op-kind -> required-status(es) mapping (read directly off
`amend()`'s own guards, the same way `STATUS_GUARDED_VERBS` records
start/advance/resume/reopen's) crossed with `E.STATUS_VALUES`.

```python
AMEND_OP_REQUIRED_STATUSES = {'drop': ('pending',), 'rescope': ('pending',), 'retext-check': ('pending', 'in-progres...
```

- [_delta_for](Inv3AmendSubOpEnumeration._delta_for.md) method: HOLE: no docstring
- [_fixture](Inv3AmendSubOpEnumeration._fixture.md) method: HOLE: no docstring
- [test_generated_amend_grid_every_refusal_is_non_generic_or_honest](Inv3AmendSubOpEnumeration.test_generated_amend_grid_every_refusal_is_non_generic_or_honest.md) method: HOLE: no docstring

writes internal: Inv3AmendSubOpEnumeration.AMEND_OP_REQUIRED_STATUSES

referenced by: none found
