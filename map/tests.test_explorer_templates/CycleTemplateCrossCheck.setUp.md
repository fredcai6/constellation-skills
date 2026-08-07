# tests.test_explorer_templates:CycleTemplateCrossCheck.setUp
method, tests/test_explorer_templates.py:153, 7 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: _load
calls stdlib: json.loads, pathlib.Path, tempfile.TemporaryDirectory
reads internal: CYCLE_TEMPLATE, CycleTemplateCrossCheck.root, CycleTemplateCrossCheck.tmp, CycleTemplateCrossCheck.work_area
reads stdlib: json (module), tempfile (module)
writes internal: CycleTemplateCrossCheck.m, CycleTemplateCrossCheck.root, CycleTemplateCrossCheck.tmp, CycleTemplateCrossCheck.tpl, CycleTemplateCrossCheck.work_area
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
