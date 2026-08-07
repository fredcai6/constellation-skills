# tests.test_episode_capture:norm
function, tests/test_episode_capture.py:53, 3 lines

```python
def norm(path)
```

Compare paths the way the filesystem does, not the way strings do.

calls stdlib: builtins.str, os.path.normcase, os.path.realpath
reads stdlib: os (module) x2, os.path x2

referenced by: 24 sites, this module only
