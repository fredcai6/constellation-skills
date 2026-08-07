# tests.test_episode_capture:FailSoft.test_failsoft_a_fully_terminal_checklist_does_not_change_any_exit_code
method, tests/test_episode_capture.py:367, 5 lines

```python
def test_failsoft_a_fully_terminal_checklist_does_not_change_any_exit_code(self)
```

HOLE: no docstring

calls internal: FailSoft.assertEqual x2, engine x2, work_area
calls stdlib: tempfile.TemporaryDirectory
reads stdlib: tempfile (module)
unresolved: 2 reads (dispatch-unknown-base)

referenced by: none found
