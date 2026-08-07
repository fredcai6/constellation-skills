# tests.test_agent_work_root:WiringExplicitWinsTests.test_collect_feedback_explicit_inbox_wins
method, tests/test_agent_work_root.py:258, 28 lines

```python
def test_collect_feedback_explicit_inbox_wins(self)
```

HOLE: no docstring

calls internal: WiringExplicitWinsTests.assertEqual, WiringExplicitWinsTests.assertFalse, WiringExplicitWinsTests.assertTrue, _load
calls stdlib: builtins.str x2, os.chdir x2, os.getcwd, pathlib.Path, pathlib.Path.cwd
reads internal: WiringExplicitWinsTests.dir x6
reads stdlib: os (module) x3, pathlib.Path
unresolved: 5 calls (dispatch-unknown-base), 2 reads (unbound-name), 1 writes (dispatch-unknown-base)

referenced by: none found
