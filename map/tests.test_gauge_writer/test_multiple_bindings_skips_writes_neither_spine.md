# tests.test_gauge_writer:test_multiple_bindings_skips_writes_neither_spine
function, tests/test_gauge_writer.py:283, 31 lines

```python
def test_multiple_bindings_skips_writes_neither_spine(proj)
```

One session_id bound to TWO spines, ONE PostToolUse event with a

realistic main-chain transcript -- (decision:gauge-write-skips-on-
multiple-bindings, supersedes decision:gauge-write-fans-out-on-ambiguity).

Live production evidence (epic-226 / #261) proved fan-out wrong: when two
genuinely different top-level agents share one session_id, find_latest_usage
cannot tell whose activity produced the latest usage record, and fanning the
same wrong-source record out to every bound spine SPREADS the
misattribution instead of fixing it. So 2+ candidates must now be treated
as uncertainty -- write NOTHING to either spine, exactly like the existing
zero-candidate (unbound) case. Before/after comparison: neither
gauge.json existed before the call, and neither exists after -- the
strongest form of "unchanged" for a file that was never there.

calls internal: _bind x2, _hook_data
reads internal: _FIXTURE, gw
unresolved: 9 calls (dispatch-unknown-base)

referenced by: none found
