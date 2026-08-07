# tests.test_map_contract_wiring:ContractWiring.test_verify_orientation_is_not_duplicated_onto_the_plan_step
method, tests/test_map_contract_wiring.py:173, 7 lines

```python
def test_verify_orientation_is_not_duplicated_onto_the_plan_step(self)
```

Symmetry is the failure mode here, not the goal: the orientation

receipt is written and gated once, at the step whose anchor makes it
early.

calls internal: ContractWiring.assertNotIn, ContractWiring.subTest, command_checks

referenced by: none found
