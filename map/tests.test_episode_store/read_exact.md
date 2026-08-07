# tests.test_episode_store:read_exact
function, tests/test_episode_store.py:59, 5 lines

```python
def read_exact(path)
```

Read a store file with newline translation disabled, as the store itself does.

Not Path.read_text(newline=...) — that kwarg is Python 3.13+ and CI pins 3.12.

calls stdlib: pathlib.Path
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 10 sites, this module only
