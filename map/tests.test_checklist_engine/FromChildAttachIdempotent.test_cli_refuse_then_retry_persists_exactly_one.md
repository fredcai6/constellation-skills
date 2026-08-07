# tests.test_checklist_engine:FromChildAttachIdempotent.test_cli_refuse_then_retry_persists_exactly_one
method, tests/test_checklist_engine.py:3147, 20 lines

```python
def test_cli_refuse_then_retry_persists_exactly_one(self)
```

HOLE: no docstring

calls internal: FromChildAttachIdempotent.assertEqual x7, FromChildAttachIdempotent._review_results x3, FromChildAttachIdempotent._review_gate, FromChildAttachIdempotent._write_child
calls stdlib: builtins.str x6, builtins.len x3, pathlib.Path, tempfile.TemporaryDirectory
reads internal: E x7
reads stdlib: tempfile (module)
unresolved: 7 calls (dispatch-unknown-base)

referenced by: none found
