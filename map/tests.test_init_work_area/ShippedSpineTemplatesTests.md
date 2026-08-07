# tests.test_init_work_area:ShippedSpineTemplatesTests
class, tests/test_init_work_area.py:271, 54 lines

```python
class ShippedSpineTemplatesTests(TestCase)
```

Every shipped spine template must materialize with no residual work-id

placeholder the resolver is responsible for. Regression guard for the
ADMIRAL_SPINE `<epic-id>` bug: the resolver substitutes `<work-id>` only, so
an admiral spine authored with `<epic-id>` left literal placeholders in the
execute.p2 / closeout.c2 command checks and refused `start`.

- [_materialize](ShippedSpineTemplatesTests._materialize.md) method: HOLE: no docstring
- [test_admiral_spine_resolves_work_id_cleanly](ShippedSpineTemplatesTests.test_admiral_spine_resolves_work_id_cleanly.md) method: HOLE: no docstring
- [test_admiral_spine_resolves_admiral_skill_dir_and_session_id_cleanly](ShippedSpineTemplatesTests.test_admiral_spine_resolves_admiral_skill_dir_and_session_id_cleanly.md) method: HOLE: no docstring
- [test_commander_and_explorer_spines_resolve_work_id_cleanly](ShippedSpineTemplatesTests.test_commander_and_explorer_spines_resolve_work_id_cleanly.md) method: HOLE: no docstring

referenced by: none found
