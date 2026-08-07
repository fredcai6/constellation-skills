# tests.test_checklist_engine:RenderAnchorsAndConstraints
class, tests/test_checklist_engine.py:3874, 82 lines

```python
class RenderAnchorsAndConstraints(TestCase)
```

Issue #420, defect 2: `anchors` and `constraints` are real, populated

corpus content on execute.json gates (Commander mission-frame anchors,
per-gate constraints) -- confirmed live against 20+ archived execute.json
gates -- but `state()` never read them, so `current()` silently dropped
them even when populated. `current` is documented as a COMPLETE briefing
(INV-1, docs/CHECKLIST_ENGINE_DESIGN.md); this closes that gap.

- [test_constraints_render_when_present](RenderAnchorsAndConstraints.test_constraints_render_when_present.md) method: HOLE: no docstring
- [test_anchors_render_when_present_dict_shape](RenderAnchorsAndConstraints.test_anchors_render_when_present_dict_shape.md) method: HOLE: no docstring
- [test_anchors_render_when_present_list_shape](RenderAnchorsAndConstraints.test_anchors_render_when_present_list_shape.md) method: HOLE: no docstring
- [test_anchors_render_when_dict_value_is_a_plain_string](RenderAnchorsAndConstraints.test_anchors_render_when_dict_value_is_a_plain_string.md) method: HOLE: no docstring
- [test_absent_constraints_and_anchors_render_unchanged](RenderAnchorsAndConstraints.test_absent_constraints_and_anchors_render_unchanged.md) method: HOLE: no docstring
- [test_empty_constraints_list_and_no_postconditions_renders_unchanged](RenderAnchorsAndConstraints.test_empty_constraints_list_and_no_postconditions_renders_unchanged.md) method: HOLE: no docstring

referenced by: none found
