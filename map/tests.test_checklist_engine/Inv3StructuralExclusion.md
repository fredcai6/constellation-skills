# tests.test_checklist_engine:Inv3StructuralExclusion
class, tests/test_checklist_engine.py:2227, 29 lines

```python
class Inv3StructuralExclusion(TestCase)
```

The remaining `MUTATING_VERBS` members (`record`, `consolidate`,

`append`, `flag-candidate`) are excluded from the (status, verb) grid for
a STRUCTURAL reason, not because nobody checked: `record`/`append`
refuse on a checklist-TYPE mismatch before ever inspecting a task's
status; `consolidate`/`flag-candidate` take no task `id` argument at
all. Verified by running them against a gated, single-task fixture
across every status (record/append) or with no id supplied at all
(consolidate/flag-candidate).

- [test_record_and_append_refuse_on_type_before_touching_task_status](Inv3StructuralExclusion.test_record_and_append_refuse_on_type_before_touching_task_status.md) method: HOLE: no docstring
- [test_consolidate_and_flag_candidate_never_touch_a_task_id](Inv3StructuralExclusion.test_consolidate_and_flag_candidate_never_touch_a_task_id.md) method: HOLE: no docstring

referenced by: none found
