# tests.test_checklist_engine:LegacySpineBackwardCompat
class, tests/test_checklist_engine.py:4184, 49 lines

```python
class LegacySpineBackwardCompat(TestCase)
```

#227 g2 constraint 5: a REAL captured, organically-evolved spine (no

why_trail key at all, no why_exempt on any task) must render through
current()/state() WITHOUT EVER RAISING. This engine drives live runs right
now, including the one that dispatched this change; a KeyError on real
data would break work in flight. The fixture is a read-only COPY of a real
explorer spine.json (constellation-skills .agent-work archive) — never
mutated with a live/mutating engine verb; any status flip below is a
plain in-memory dict edit on the copy, not an engine call.

```python
FIXTURE = ROOT / 'tests' / 'fixtures' / 'legacy_spine_organic.json'
```

- [test_fixture_is_genuinely_legacy_shaped](LegacySpineBackwardCompat.test_fixture_is_genuinely_legacy_shaped.md) method: HOLE: no docstring
- [test_all_terminal_shape_renders_done_without_raising](LegacySpineBackwardCompat.test_all_terminal_shape_renders_done_without_raising.md) method: HOLE: no docstring
- [test_state_projection_renders_on_all_terminal_shape](LegacySpineBackwardCompat.test_state_projection_renders_on_all_terminal_shape.md) method: HOLE: no docstring
- [test_status_flip_renders_active_branch_on_real_condition_data](LegacySpineBackwardCompat.test_status_flip_renders_active_branch_on_real_condition_data.md) method: HOLE: no docstring
- [test_reopened_gate_with_unmet_condition_renders_kind_and_real_statement](LegacySpineBackwardCompat.test_reopened_gate_with_unmet_condition_renders_kind_and_real_statement.md) method: HOLE: no docstring

reads internal: ROOT
writes internal: LegacySpineBackwardCompat.FIXTURE

referenced by: none found
