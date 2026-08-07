# tests.test_spine_rail:test_post_release_empty_set_cleanup_deletes_composite_key_not_bare
function, tests/test_spine_rail.py:412, 23 lines

```python
def test_post_release_empty_set_cleanup_deletes_composite_key_not_bare(proj)
```

The single line where a wrong substitution deletes a live parent's whole

binding. Parent and subagent both hold an entry for the SAME spine path
under different keys; the subagent's release empties ITS key set, and the
cleanup must delete that composite key while the bare key's entries stay.

calls internal: _real_post_tool_use x3, _claim_cmd x2, _abs_spine, _real_parent_payloads, _real_subagent_payloads, _release_cmd
calls stdlib: builtins.list x2, builtins.set x2, json.dumps x2
reads internal: sr x6
reads stdlib: json (module) x2
unresolved: 9 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
