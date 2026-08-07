# tests.test_gauge_writer:test_spine_directly_in_agent_work_root_skips_no_write
function, tests/test_gauge_writer.py:221, 12 lines

```python
def test_spine_directly_in_agent_work_root_skips_no_write(proj)
```

`.agent-work/spine.json` (no <work_id> dir) is also outside the

contract -- writing there would collide across every run that made the
same mistake, so it skips rather than guessing a work_id.

calls internal: _bind, _hook_data
reads internal: _FIXTURE, gw
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
