# tests.test_checklist_engine:TaskFieldCompleteness
class, tests/test_checklist_engine.py:3958, 113 lines

```python
class TaskFieldCompleteness(TestCase)
```

Issue #420, defect 3: a real enumeration of the fields a Task may

carry (docs/CHECKLIST_SCHEMA.md's Task table, plus `anchors` -- documented
only in commander-core.md prose, not the schema table) asserting every
POPULATED field's content appears somewhere in current()'s rendered
output for a fixture that carries every field. Built as a loop over the
fixture's own keys minus a documented, justified exclusion set -- NOT a
hardcoded check of only anchors/constraints by name -- so a genuinely new
field added to Task later and forgotten in render_human() fails this test
by default, exactly the way anchors/constraints failed before this fix.

```python
_EXCLUDED_FIELDS = {'id', 'status', 'preconditions', 'postconditions', 'status_detail', 'rework_count', 'r...
```

- [_flatten](TaskFieldCompleteness._flatten.md) static method: Best-effort text extraction for str / [str] / {category: [str]}
- [test_every_populated_field_renders_for_a_fully_populated_gate](TaskFieldCompleteness.test_every_populated_field_renders_for_a_fully_populated_gate.md) method: HOLE: no docstring

reads stdlib: builtins.staticmethod
writes internal: TaskFieldCompleteness._EXCLUDED_FIELDS

referenced by: none found
