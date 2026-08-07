# tests.test_episode_negative_control:seeded_store
function, tests/test_episode_negative_control.py:1030, 24 lines

```python
@pytest.fixture(scope='module')
def seeded_store(tmp_path_factory)
```

A temp store seeded through the SANCTIONED WRITER, never by hand-placing files.

The cluster joins on a shared `artifact-ref`; the outsider shares neither join key.
`role+spine-step` is ALWAYS a join key, so every member carries a distinct role/step
pair — otherwise the cluster would link on that instead and the fixture would prove
nothing about `artifact-ref`.

calls internal: _create_op x4
calls third-party: apply_episode_delta.apply_delta, apply_episode_delta.ensure_store_layout
reads third-party: apply_episode_delta (module) x2
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
