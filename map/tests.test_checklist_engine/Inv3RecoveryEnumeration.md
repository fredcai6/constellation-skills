# tests.test_checklist_engine:Inv3RecoveryEnumeration
class, tests/test_checklist_engine.py:2109, 64 lines

```python
class Inv3RecoveryEnumeration(TestCase)
```

Constraint 2 (issue #227 gate g3, THE TRAP): the enumeration grid must

be GENERATED from MUTATING_VERBS + the engine's own status vocabulary,
not a hand-typed list of the three named refusal families -- a
hand-typed list would pass green while OTHER status-guarded refusals
(e.g. `advance` on a `pending` task, `reopen` on a `blocked` task) fall
through to the old bare message.

```python
STATUS_GUARDED_VERBS = {'start': 'pending', 'advance': 'in-progress', 'resume': 'blocked', 'reopen': 'complete'}
```

- [_argv](Inv3RecoveryEnumeration._argv.md) method: HOLE: no docstring
- [_fixture](Inv3RecoveryEnumeration._fixture.md) method: HOLE: no docstring
- [_is_non_generic](Inv3RecoveryEnumeration._is_non_generic.md) method: HOLE: no docstring
- [test_generated_grid_every_state_caused_refusal_is_non_generic](Inv3RecoveryEnumeration.test_generated_grid_every_state_caused_refusal_is_non_generic.md) method: HOLE: no docstring

writes internal: Inv3RecoveryEnumeration.STATUS_GUARDED_VERBS

referenced by: none found
