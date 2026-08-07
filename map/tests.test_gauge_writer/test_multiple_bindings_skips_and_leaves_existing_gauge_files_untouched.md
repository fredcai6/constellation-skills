# tests.test_gauge_writer:test_multiple_bindings_skips_and_leaves_existing_gauge_files_untouched
function, tests/test_gauge_writer.py:316, 23 lines

```python
def test_multiple_bindings_skips_and_leaves_existing_gauge_files_untouched(proj)
```

Same 2-binding ambiguity, but each spine already carries a prior

reading -- proves 'skip' means the prior content survives byte-identical,
not merely 'no crash'.

calls internal: _bind x2, _hook_data
calls stdlib: json.dumps x2
reads internal: _FIXTURE, gw
reads stdlib: json (module) x2
unresolved: 9 calls (dispatch-unknown-base)

referenced by: none found
