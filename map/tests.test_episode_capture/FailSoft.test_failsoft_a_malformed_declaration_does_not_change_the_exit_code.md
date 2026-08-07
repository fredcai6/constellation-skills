# tests.test_episode_capture:FailSoft.test_failsoft_a_malformed_declaration_does_not_change_the_exit_code
method, tests/test_episode_capture.py:391, 4 lines

```python
def test_failsoft_a_malformed_declaration_does_not_change_the_exit_code(self)
```

HOLE: no docstring

calls internal: FailSoft.assertEqual, engine, work_area
calls stdlib: tempfile.TemporaryDirectory
reads stdlib: tempfile (module)
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
