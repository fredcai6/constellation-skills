# tests.test_gauge_writer:test_spine_outside_agent_work_skips_no_write
function, tests/test_gauge_writer.py:201, 18 lines

```python
def test_spine_outside_agent_work_skips_no_write(proj)
```

A binding whose spine path resolved to a CHECKOUT ROOT rather than a

work dir (observed live: an untracked gauge.json in the repo root) must
produce NO write at all. Only `.agent-work/` is gitignored, so a gauge
record dropped beside it is untracked debris in the user's tree.

Drives the real handler against a real transcript with a real binding --
the only thing wrong is the spine location -- so a regression that removes
the containment check fails here rather than passing on a mocked path.

calls internal: _bind, _hook_data
calls stdlib: builtins.list
reads internal: _FIXTURE, gw
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
