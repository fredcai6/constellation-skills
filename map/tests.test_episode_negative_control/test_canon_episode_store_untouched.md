# tests.test_episode_negative_control:test_canon_episode_store_untouched
function, tests/test_episode_negative_control.py:1129, 22 lines

```python
def test_canon_episode_store_untouched(seeded_store)
```

Belt and braces (b): the tracked store's blob OIDs are READ and compared, not

assumed. Empty-vs-empty passes a naive equality check, so the store's NON-emptiness
is asserted first — this repo's `episodes/active/` carries real episodes plus
`.gitkeep`, and that is what makes the comparison meaningful.

calls stdlib: builtins.str x2, subprocess.run x2, builtins.any, builtins.len
reads internal: REPO_ROOT x3
reads stdlib: subprocess (module) x2
unresolved: 6 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
