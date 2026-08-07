# tests.test_episode_capture:FailSoft.test_failsoft_an_arbitrary_producer_crash_leaves_a_stub_not_silence
method, tests/test_episode_capture.py:437, 22 lines

```python
def test_failsoft_an_arbitrary_producer_crash_leaves_a_stub_not_silence(self)
```

Broad-except is the deliberate choice here, so prove it against something

other than the errors the producer is known to raise — and prove it is
fail-SOFT without being fail-SILENT.

Writing nothing is the easy swallow and the wrong one. A vanished manifest
is indistinguishable from a step nobody ever started, and those are
different facts about the run. So the crash path must still leave the
reading it failed to take: a stub carrying the exception type.

calls internal: FailSoft.assertEqual x2, FailSoft.assertTrue x2, FailSoft.assertIsNone, FailSoft.assertIsNotNone, work_area
calls stdlib: pathlib.Path x2, json.loads, tempfile.TemporaryDirectory
reads internal: ec
reads stdlib: json (module), tempfile (module)
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
