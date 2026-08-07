# tests.test_gauge_writer:test_top_level_record_keeps_exactly_the_frozen_four_fields
function, tests/test_gauge_writer.py:1230, 10 lines

```python
def test_top_level_record_keeps_exactly_the_frozen_four_fields(proj)
```

The fifth field is additive and OPTIONAL, and it appears only on the

dispatched-agent path: a payload with no agent_id must stay byte-identical
to today's behavior, and the frozen 4-field record is what the reader and
the pre-existing tests pin. There is no identity to resolve for a
top-level agent, so there is nothing to report.

calls internal: _bound_work, _hook_data
calls stdlib: builtins.set, json.loads
reads internal: _FIXTURE, gw
reads stdlib: json (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
