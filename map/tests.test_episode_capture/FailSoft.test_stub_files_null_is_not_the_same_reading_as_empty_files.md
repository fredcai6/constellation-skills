# tests.test_episode_capture:FailSoft.test_stub_files_null_is_not_the_same_reading_as_empty_files
method, tests/test_episode_capture.py:460, 43 lines

```python
def test_stub_files_null_is_not_the_same_reading_as_empty_files(self)
```

`files: []` and `files: null` are the two readings that must never

collide. `[]` is a *complete* reading — "this step declared no context
refs". `null` is the *absence* of a reading — "the record could not be
taken". A consumer that conflated them would report a step as having been
delivered nothing when in truth nothing is known about what it was
delivered.

Both sides are produced from real emits and both are read, so this cannot
pass on an empty-vs-empty or missing-vs-missing coincidence — and the last
three assertions pin the trap directly: BOTH values are falsy, so any
consumer discriminating on truthiness loses the distinction. Only
`is None` separates them.

calls internal: FailSoft.assertEqual x3, FailSoft.assertFalse x2, work_area x2, FailSoft.assertIn, FailSoft.assertIsNone, FailSoft.assertIsNot, FailSoft.assertNotEqual, FailSoft.assertNotIn
calls stdlib: builtins.bool x2, json.loads x2, pathlib.Path x2, tempfile.TemporaryDirectory
reads internal: ec x2
reads stdlib: json (module) x2, tempfile (module)
unresolved: 4 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
