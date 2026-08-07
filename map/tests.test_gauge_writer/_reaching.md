# tests.test_gauge_writer:_reaching
function, tests/test_gauge_writer.py:1023, 15 lines

```python
def _reaching(monkeypatch, path, agent_id=None)
```

Run find_latest_usage and report how many transcript lines the reverse

scan actually reached -- 'any guard that loops must assert what it looped
over'. A conjunct that was never exercised shows up here as a reach count
that never gets past the first line.

- [counting](_reaching.counting.md) method: HOLE: no docstring

calls stdlib: builtins.len
reads internal: gw x3
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 5 sites, this module only
