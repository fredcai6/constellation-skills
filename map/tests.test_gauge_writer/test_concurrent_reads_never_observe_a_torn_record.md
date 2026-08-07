# tests.test_gauge_writer:test_concurrent_reads_never_observe_a_torn_record
function, tests/test_gauge_writer.py:1267, 57 lines

```python
def test_concurrent_reads_never_observe_a_torn_record(proj)
```

Hammer writes and reads of the same gauge.json concurrently. Every

read that returns content must be complete, valid JSON with exactly the
frozen 4 keys -- never a JSONDecodeError, never a partial/truncated
record. This is the atomic tmp+rename guarantee (TF9), exercised under
real thread scheduling rather than asserted only by code inspection.

- [writer](test_concurrent_reads_never_observe_a_torn_record.writer.md) method: HOLE: no docstring
- [reader](test_concurrent_reads_never_observe_a_torn_record.reader.md) method: HOLE: no docstring

calls stdlib: threading.Thread x2, threading.Event
reads stdlib: threading (module) x3
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found
