# tests.test_episode_negative_control:test_red_proof_sharp_drops_exactly_one_derivation
function, tests/test_episode_negative_control.py:948, 10 lines

```python
def test_red_proof_sharp_drops_exactly_one_derivation(control, monkeypatch)
```

R2: drop EXACTLY ONE derivation. The control must name EXACTLY that field.

`failed_command_count` is forced to a constant `0` — a value the store's validator
accepts without complaint and no downstream reader can tell from a real one.

calls internal: compare_fields
reads third-party: episode_capture (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
