# tests.test_gauge_writer:test_no_usable_record_single_candidate_writes_skip_flag_no_candidate_count
function, tests/test_gauge_writer.py:574, 18 lines

```python
def test_no_usable_record_single_candidate_writes_skip_flag_no_candidate_count(proj, tmp_path)
```

Single resolved candidate, transcript exists and is readable, but

compute_record finds nothing usable -- the second positively-localized
cause. No candidate_count key (this is a single-path outcome, unlike
ambiguous-binding).

calls internal: _bound_work, _hook_data
calls stdlib: json.dumps, json.loads
reads internal: gw x2
reads stdlib: json (module) x2
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
