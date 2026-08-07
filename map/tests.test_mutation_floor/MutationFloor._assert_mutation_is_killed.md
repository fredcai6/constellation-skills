# tests.test_mutation_floor:MutationFloor._assert_mutation_is_killed
method, tests/test_mutation_floor.py:335, 75 lines

```python
def _assert_mutation_is_killed(self, mutation: Mutation) -> None
```

HOLE: no docstring

calls internal: MutationFloor.assertEqual x4, MutationFloor.assertNotEqual x2, MutationFloor.assertTrue x2, MutationFloor._copy_module, MutationFloor.assertGreater, apply_mutation, failed_nodes, passed_count, run_floor
calls stdlib: builtins.any
reads internal: Mutation.name x9, ORIGINAL x5, Mutation.expect_kills x2, Mutation.subs, Mutation.why
unresolved: 7 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 10 sites, this module only
