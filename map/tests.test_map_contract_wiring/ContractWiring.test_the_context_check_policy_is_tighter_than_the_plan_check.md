# tests.test_map_contract_wiring:ContractWiring.test_the_context_check_policy_is_tighter_than_the_plan_check
method, tests/test_map_contract_wiring.py:208, 8 lines

```python
def test_the_context_check_policy_is_tighter_than_the_plan_check(self)
```

No `override_policy` on the context check: waiving it needs the

high-friction `--force` path, which always demands authority + reason.

calls internal: ContractWiring.assertIsNone, task
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
