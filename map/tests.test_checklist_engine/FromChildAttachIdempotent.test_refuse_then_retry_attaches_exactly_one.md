# tests.test_checklist_engine:FromChildAttachIdempotent.test_refuse_then_retry_attaches_exactly_one
method, tests/test_checklist_engine.py:3129, 17 lines

```python
def test_refuse_then_retry_attaches_exactly_one(self)
```

HOLE: no docstring

calls internal: FromChildAttachIdempotent.assertEqual x5, FromChildAttachIdempotent._review_results x3, FromChildAttachIdempotent.assertRaises x2, FromChildAttachIdempotent._review_gate, FromChildAttachIdempotent._write_child
calls stdlib: builtins.len x3, builtins.str x3, pathlib.Path x3, tempfile.TemporaryDirectory
reads internal: E x5
reads stdlib: tempfile (module)
unresolved: 3 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
