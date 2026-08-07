# tests.test_episode_negative_control:test_red_proof_blunt_hardcoded_composer
function, tests/test_episode_negative_control.py:920, 26 lines

```python
def test_red_proof_blunt_hardcoded_composer(control, monkeypatch)
```

R1: the composer returns plausible constants. The control must name EVERY field.

Every constant below passes `apply_episode_delta._validate_create` (isinstance plus
non-empty), which is exactly why the validator cannot be the oracle and this control
has to exist.

calls internal: compare_fields
calls stdlib: builtins.list
reads internal: MECHANICAL_GROUP
reads third-party: episode_capture (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
