# tests.test_mutation_floor:MutationFloor
class, tests/test_mutation_floor.py:271, 139 lines

```python
class MutationFloor(TestCase)
```

HOLE: no docstring

```python
maxDiff = None
```

- [_copy_module](MutationFloor._copy_module.md) method: HOLE: no docstring
- [test_0_unmutated_baseline_is_green](MutationFloor.test_0_unmutated_baseline_is_green.md) method: A red below must be attributable to the mutation, not to the harness.
- [test_1_mutation_all_to_any_is_killed](MutationFloor.test_1_mutation_all_to_any_is_killed.md) method: HOLE: no docstring
- [test_2_mutation_unresolvable_root_collapse_is_killed](MutationFloor.test_2_mutation_unresolvable_root_collapse_is_killed.md) method: HOLE: no docstring
- [test_3_mutation_existence_instead_of_citable_content_is_killed](MutationFloor.test_3_mutation_existence_instead_of_citable_content_is_killed.md) method: HOLE: no docstring
- [test_4_mutation_unmapped_not_any_to_not_all_is_killed](MutationFloor.test_4_mutation_unmapped_not_any_to_not_all_is_killed.md) method: Regression: this one SURVIVED the first shipped floor.
- [test_5_mutation_sentinel_accepted_as_a_hash_pin_is_killed](MutationFloor.test_5_mutation_sentinel_accepted_as_a_hash_pin_is_killed.md) method: Regression: the B1 blocker, pinned so it cannot come back.
- [test_6_mutation_absent_frame_credited_as_a_pass_is_killed](MutationFloor.test_6_mutation_absent_frame_credited_as_a_pass_is_killed.md) method: THE vacuous pass -- the one mutation this gate exists to pin.
- [test_7_mutation_undeclared_substitute_refusal_disabled_is_killed](MutationFloor.test_7_mutation_undeclared_substitute_refusal_disabled_is_killed.md) method: HOLE: no docstring
- [test_8_mutation_known_fallback_label_on_membership_alone_is_killed](MutationFloor.test_8_mutation_known_fallback_label_on_membership_alone_is_killed.md) method: HOLE: no docstring
- [test_9_mutation_every_substitute_reported_as_verified_is_killed](MutationFloor.test_9_mutation_every_substitute_reported_as_verified_is_killed.md) method: g2 review BLOCK regression: the label must stay READ, not just written.
- [test_10_mutation_provenance_line_dropped_is_killed](MutationFloor.test_10_mutation_provenance_line_dropped_is_killed.md) method: HOLE: no docstring
- [_assert_mutation_is_killed](MutationFloor._assert_mutation_is_killed.md) method: HOLE: no docstring

reads internal: Mutation
reads stdlib: builtins.str, pathlib.Path
writes internal: MutationFloor.maxDiff

referenced by: none found
