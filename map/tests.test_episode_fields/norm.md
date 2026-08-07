# tests.test_episode_fields:norm
function, tests/test_episode_fields.py:58, 3 lines

```python
def norm(path)
```

Compare paths the way the filesystem does, not the way strings do.

calls stdlib: builtins.str, os.path.normcase, os.path.realpath
reads stdlib: os (module) x2, os.path x2

referenced by: 2 sites, this module only
