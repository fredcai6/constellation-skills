# tests.test_map_orient:PartialFillMatrix
class, tests/test_map_orient.py:350, 98 lines

```python
class PartialFillMatrix(TestCase)
```

Each arm omits exactly ONE required field; the other two are present.

Three arms is what kills an `all` -> `any` mutation: `any` would let every
one of them through. The positive control is what stops a bare
`return False` from faking the kill.

- [test_positive_control_a_complete_record_passes](PartialFillMatrix.test_positive_control_a_complete_record_passes.md) method: HOLE: no docstring
- [test_missing_substitutes_is_refused](PartialFillMatrix.test_missing_substitutes_is_refused.md) method: HOLE: no docstring
- [test_missing_unmapped_is_refused](PartialFillMatrix.test_missing_unmapped_is_refused.md) method: HOLE: no docstring
- [test_missing_escalation_is_refused](PartialFillMatrix.test_missing_escalation_is_refused.md) method: HOLE: no docstring
- [test_filler_escalation_is_refused](PartialFillMatrix.test_filler_escalation_is_refused.md) method: HOLE: no docstring
- [test_filler_unmapped_is_refused](PartialFillMatrix.test_filler_unmapped_is_refused.md) method: HOLE: no docstring
- [test_one_filler_poisons_a_multi_element_unmapped_list](PartialFillMatrix.test_one_filler_poisons_a_multi_element_unmapped_list.md) method: MULTI-element on purpose.
- [test_a_multi_element_unmapped_list_of_real_entries_passes](PartialFillMatrix.test_a_multi_element_unmapped_list_of_real_entries_passes.md) method: Positive control for the case above: an all-real list must pass.
- [test_one_unpinned_substitute_poisons_a_multi_element_list](PartialFillMatrix.test_one_unpinned_substitute_poisons_a_multi_element_list.md) method: HOLE: no docstring
- [test_filler_substitute_path_is_refused](PartialFillMatrix.test_filler_substitute_path_is_refused.md) method: HOLE: no docstring
- [test_unhashed_substitute_is_refused](PartialFillMatrix.test_unhashed_substitute_is_refused.md) method: HOLE: no docstring
- [test_the_completeness_predicate_requires_all_three](PartialFillMatrix.test_the_completeness_predicate_requires_all_three.md) method: Direct assertion on the predicate the mutation targets.

referenced by: none found
