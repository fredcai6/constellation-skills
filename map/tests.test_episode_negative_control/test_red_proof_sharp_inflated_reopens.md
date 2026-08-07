# tests.test_episode_negative_control:test_red_proof_sharp_inflated_reopens
function, tests/test_episode_negative_control.py:974, 7 lines

```python
def test_red_proof_sharp_inflated_reopens(control, monkeypatch)
```

R4: run-scoped `reopens` and step-scoped `rework-count` are two facts, not one

written twice. Forcing `reopen_total` to the step-scoped value must be caught.

calls internal: compare_fields
reads third-party: episode_capture (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
