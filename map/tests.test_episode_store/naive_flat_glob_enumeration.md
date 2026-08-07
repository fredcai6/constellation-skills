# tests.test_episode_store:naive_flat_glob_enumeration
function, tests/test_episode_store.py:1890, 18 lines

```python
def naive_flat_glob_enumeration(root)
```

Trap 1 — a glob that misses a subdirectory.

This is the pre-g4 enumeration, unchanged: scan `episodes/*.md`. It was correct under
the flat layout and is now silently, totally wrong — every episode lives one level
down, so this returns NOTHING (or, worse, only strays) and reports no error at all.
An empty candidate set is indistinguishable from "the store is empty", which is why
this failure mode ships instead of getting caught.

The naivety being modelled is the FLAT GLOB and nothing else, so non-episode files
are excluded through the store's real classifier rather than by a filename this
fixture knows — an inline comparison against the literal README filename here would
quietly make the fixture immune to the very defect it is supposed to model.

calls internal: classifier
calls stdlib: builtins.sorted, pathlib.Path
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
