# tests.test_gauge_writer:test_ambiguous_binding_skip_flags_do_not_clobber_existing_gauge_files
function, tests/test_gauge_writer.py:662, 21 lines

```python
def test_ambiguous_binding_skip_flags_do_not_clobber_existing_gauge_files(proj)
```

Same 'byte-identical survival' proof the existing multi-binding tests

make for gauge.json, extended to confirm the NEW skip-flag write doesn't
disturb a prior reading at either candidate path.

calls internal: _bind x2, _hook_data
calls stdlib: json.loads x2, json.dumps
reads internal: gw x3, _FIXTURE
reads stdlib: json (module) x3
unresolved: 9 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
