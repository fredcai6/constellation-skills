# tests.test_episode_store:naive_select_dict_collapse
function, tests/test_episode_store.py:895, 23 lines

```python
def naive_select_dict_collapse(root, field, value)
```

A NAIVE select, written the way a reasonable person writes one: read each

episode's ## Mechanical block into a dict of `- key: value` lines, then compare.

It is wrong, and wrong in the worst available way. artifact-ref is REPEATED — one
line per ref — so folding the block into a dict keeps only the LAST occurrence and
silently discards every earlier one. Query for a ref that is not an episode's final
ref and that episode simply is not in the answer: no exception, no warning, no
partial-result flag, just a candidate set one or more records short. This function
exists so the store's own test suite can DEMONSTRATE the omission rather than
assert that it was avoided.

calls stdlib: builtins.sorted x2, pathlib.Path
unresolved: 8 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
