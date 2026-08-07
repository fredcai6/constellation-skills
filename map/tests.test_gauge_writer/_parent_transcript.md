# tests.test_gauge_writer:_parent_transcript
function, tests/test_gauge_writer.py:882, 10 lines

```python
def _parent_transcript(proj, source=None, name='sess-1')
```

A copy of a fixture transcript at a path INSIDE tmp_path, so the

derivation's `<parent>/subagents/agent-<id>.jsonl` sibling can be planted
without ever writing into the repo's own fixtures directory.

reads internal: _FIXTURE
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 7 sites, this module only
