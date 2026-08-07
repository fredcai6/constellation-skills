# tests.test_episode_store:naive_layout_listing_as_ids
function, tests/test_episode_store.py:1921, 13 lines

```python
def naive_layout_listing_as_ids(root)
```

Trap 4 — a directory listing read as a list of episode ids.

The shipped defect, in one expression: `{p.stem for p in (root/"active").glob("*.md")}`.
Correct exactly while a layout directory holds nothing but episodes, and silently
wrong the moment it holds anything else — which it always does, because git needs a
tracked file in a directory to keep the directory at all. Every non-episode file then
becomes a phantom id that no record backs, and (when the same name appears in both
directories) trips the half-retirement guard on a store that was never retired.

calls stdlib: pathlib.Path x2, builtins.sorted
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
