# tests.test_mutation_floor:MutationFloor.test_9_mutation_every_substitute_reported_as_verified_is_killed
method, tests/test_mutation_floor.py:326, 3 lines

```python
def test_9_mutation_every_substitute_reported_as_verified_is_killed(self)
```

g2 review BLOCK regression: the label must stay READ, not just written.

calls internal: MutationFloor._assert_mutation_is_killed
reads internal: MUTATIONS

referenced by: none found
