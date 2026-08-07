# tests.test_episode_fields:LiveSpine.__init__
method, tests/test_episode_fields.py:279, 30 lines

```python
def __init__(self, root: Path, work_id='wk-live', items=('s1', 's2'), checks=None, in_repo=False)
```

HOLE: no docstring

calls internal: LiveSpine.run, init_repo
calls stdlib: builtins.list, json.dumps
reads internal: LiveSpine.dir x2, LiveSpine.SESSION, LiveSpine.path
reads stdlib: json (module)
writes internal: LiveSpine.__init__.checks, LiveSpine.dir, LiveSpine.path
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
