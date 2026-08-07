# tests.test_gauge_writer:test_ambiguous_binding_with_three_candidates_fans_out_to_all_three
function, tests/test_gauge_writer.py:556, 16 lines

```python
def test_ambiguous_binding_with_three_candidates_fans_out_to_all_three(proj)
```

N candidates, not just two -- the fan-out is unbounded in N.

calls internal: _bind, _hook_data
calls stdlib: json.loads
reads internal: gw x2, _FIXTURE
reads stdlib: json (module)
unresolved: 5 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
