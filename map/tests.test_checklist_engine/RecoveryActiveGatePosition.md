# tests.test_checklist_engine:RecoveryActiveGatePosition
class, tests/test_checklist_engine.py:2554, 75 lines

```python
class RecoveryActiveGatePosition(TestCase)
```

Reviewer BLOCK (g3-review rework 2): before this gate, `_next_verbs()`

had exactly ONE caller (`state()`), always invoked on the checklist's own
active gate. `recovery_for()` is the first caller to invoke it on an
ARBITRARY refusing task -- which need not be active. `start()`, and only
`start()`, additionally refuses a non-active gate on a GATED checklist, so
the `pending` sub-case's bare "start {tid}" suggestion could itself
refuse. Scope is precise: only `pending` (not `in-progress` --
`advance`/`resume`/`reopen` carry no active-gate check), only `GATED`
(`SURVEY` has no active-gate ordering at all).

- [_two_gate](RecoveryActiveGatePosition._two_gate.md) method: HOLE: no docstring
- [test_non_active_pending_recovery_does_not_suggest_start_and_names_active_gate](RecoveryActiveGatePosition.test_non_active_pending_recovery_does_not_suggest_start_and_names_active_gate.md) method: HOLE: no docstring
- [test_non_active_pending_recovery_full_sequence_resolves_the_original_problem](RecoveryActiveGatePosition.test_non_active_pending_recovery_full_sequence_resolves_the_original_problem.md) method: HOLE: no docstring
- [test_in_progress_non_active_task_has_no_equivalent_hole](RecoveryActiveGatePosition.test_in_progress_non_active_task_has_no_equivalent_hole.md) method: HOLE: no docstring

referenced by: none found
