# tests.test_map_contract_wiring:ContractWiring.test_neither_new_check_uses_a_relative_root
method, tests/test_map_contract_wiring.py:181, 13 lines

```python
def test_neither_new_check_uses_a_relative_root(self)
```

Command checks inherit the launcher's cwd. `<repo-root>` (added in

g1) is the robustness token; the pre-existing relative checks are
fragile-not-broken and are tracked as #341, deliberately not fixed
here.

calls internal: ContractWiring.assertNotIn x2, ContractWiring.assertIn, ContractWiring.subTest, command_checks

referenced by: none found
