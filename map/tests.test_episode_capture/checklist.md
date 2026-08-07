# tests.test_episode_capture:checklist
function, tests/test_episode_capture.py:58, 36 lines

```python
def checklist(work_id='wk', items=None, declaration=None, statuses=None)
```

A minimal gated checklist. `declaration` lands on the first item.

calls stdlib: builtins.list x2
writes internal: checklist.items, checklist.statuses
unresolved: 1 calls (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: 2 sites, this module only
