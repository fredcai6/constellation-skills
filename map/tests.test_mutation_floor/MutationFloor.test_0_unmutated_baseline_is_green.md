# tests.test_mutation_floor:MutationFloor.test_0_unmutated_baseline_is_green
method, tests/test_mutation_floor.py:286, 12 lines

```python
def test_0_unmutated_baseline_is_green(self)
```

A red below must be attributable to the mutation, not to the harness.

calls internal: MutationFloor.assertEqual x2, MutationFloor._copy_module, MutationFloor.assertGreater, passed_count, run_floor
reads internal: ORIGINAL x2
unresolved: 1 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
