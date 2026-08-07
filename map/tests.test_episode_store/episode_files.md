# tests.test_episode_store:episode_files
function, tests/test_episode_store.py:84, 11 lines

```python
def episode_files(root)
```

Every episode file in the store, by name, across BOTH directories. Replaces the

pre-g4 `root.glob("*.md")` idiom, which under the ratified layout would silently
match nothing — trap 1, in the tests' own vocabulary. Non-episode files are excluded
by the store's classifier, never by a name this helper knows.

calls internal: classifier
calls stdlib: builtins.sorted, pathlib.Path
writes internal: episode_files.root
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 6 sites, this module only
