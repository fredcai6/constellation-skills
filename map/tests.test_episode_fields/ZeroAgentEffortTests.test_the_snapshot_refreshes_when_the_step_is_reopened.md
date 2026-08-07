# tests.test_episode_fields:ZeroAgentEffortTests.test_the_snapshot_refreshes_when_the_step_is_reopened
method, tests/test_episode_fields.py:801, 8 lines

```python
def test_the_snapshot_refreshes_when_the_step_is_reopened(self)
```

Unlike the manifest, the snapshot OVERWRITES: it carries counters, and a

stale counter is a wrong fact rather than a preserved record.

calls internal: ZeroAgentEffortTests.assertEqual x3, ZeroAgentEffortTests.snapshot_file
calls stdlib: json.loads
reads internal: ZeroAgentEffortTests.spine x2
reads stdlib: json (module)
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
