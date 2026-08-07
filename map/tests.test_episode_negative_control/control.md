# tests.test_episode_negative_control:control
function, tests/test_episode_negative_control.py:623, 36 lines

```python
@pytest.fixture(scope='module')
def control(tmp_path_factory)
```

One real parent->child gated run, driven once for the whole module.

The parent's `g1` carries `child_checklist`, so the child is reached the way
production reaches it, and the child is driven WITHOUT a lease — which is what
production does, not a shortcut taken here.

calls internal: _git x6, _ControlRun x2, _ControlRun.drive x2, _plan x2, _write_json x2
reads internal: PARENT_ROLE
unresolved: 5 calls (dispatch-unknown-base)

referenced by: none found
