# tests.test_checklist_engine:FromChildAttachIdempotent
class, tests/test_checklist_engine.py:3099, 68 lines

```python
class FromChildAttachIdempotent(TestCase)
```

#191 — the `advance --from-child` seam is dedup-idempotent: a refused advance

(which `main()` persists) followed by a retry must NOT double-attach the child
consolidation. The attach stays BEFORE the postcondition/why guards; the fix is
a dedup, not a reorder.

- [_review_gate](FromChildAttachIdempotent._review_gate.md) method: HOLE: no docstring
- [_write_child](FromChildAttachIdempotent._write_child.md) method: HOLE: no docstring
- [_review_results](FromChildAttachIdempotent._review_results.md) method: HOLE: no docstring
- [test_refuse_then_retry_attaches_exactly_one](FromChildAttachIdempotent.test_refuse_then_retry_attaches_exactly_one.md) method: HOLE: no docstring
- [test_cli_refuse_then_retry_persists_exactly_one](FromChildAttachIdempotent.test_cli_refuse_then_retry_persists_exactly_one.md) method: HOLE: no docstring

referenced by: none found
