# tests.test_episode_capture:work_area
function, tests/test_episode_capture.py:96, 12 lines

```python
def work_area(tmp, work_id='wk', **kwargs)
```

Lay a checklist out the way a real run does — `<agent-work>/<work-id>/spine.json`

— and return `(spine_path, checklist)`. The layout is load-bearing: the manifest
root is the checklist directory's parent, so only this shape puts the manifest
beside the spine.

calls internal: checklist
calls stdlib: builtins.open, json.dumps, pathlib.Path
reads stdlib: json (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 21 sites, this module only
