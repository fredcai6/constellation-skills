# tests.test_mutation_floor:MutationFloor.test_4_mutation_unmapped_not_any_to_not_all_is_killed
method, tests/test_mutation_floor.py:308, 3 lines

```python
def test_4_mutation_unmapped_not_any_to_not_all_is_killed(self)
```

Regression: this one SURVIVED the first shipped floor.

calls internal: MutationFloor._assert_mutation_is_killed
reads internal: MUTATIONS

referenced by: none found
