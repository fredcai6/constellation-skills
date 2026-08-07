# tests.test_map_contract_wiring:ContextImperativeAnchor.test_the_context_map_read_is_not_anchored_to_a_late_artifact
method, tests/test_map_contract_wiring.py:75, 11 lines

```python
def test_the_context_map_read_is_not_anchored_to_a_late_artifact(self)
```

`execute.json` is authored at the END of a run.

Anchoring the map read to it is what PRE-B measured as compliance with
zero orientation. The context step must not reintroduce that anchor --
not with `execute.json`, and not with any other 'before authoring X'
phrasing, which is the same defect wearing a different noun.

calls internal: ContextImperativeAnchor.assertNotIn x2, imperative
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
