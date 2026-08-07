# tests.test_episode_capture:FailSoft.test_failsoft_an_unmapped_root_token_does_not_change_the_exit_code
method, tests/test_episode_capture.py:373, 9 lines

```python
def test_failsoft_an_unmapped_root_token_does_not_change_the_exit_code(self)
```

HOLE: no docstring

calls internal: FailSoft.assertEqual x2, engine, work_area
calls stdlib: json.loads, tempfile.TemporaryDirectory
reads stdlib: json (module), tempfile (module)
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
