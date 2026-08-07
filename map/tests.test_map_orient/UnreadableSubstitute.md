# tests.test_map_orient:UnreadableSubstitute
class, tests/test_map_orient.py:455, 71 lines

```python
class UnreadableSubstitute(TestCase)
```

A substitute that cannot be read must REFUSE, never discharge.

This is the hole the whole contract exists to close: the tool used to emit
`content_hash: "unreadable"` for a path it could not read, and a non-empty
sentinel satisfied the "is it hash-pinned" test -- so a single typo in a
substitute path discharged the entire degraded record at exit 0.

- [test_a_nonexistent_substitute_path_refuses](UnreadableSubstitute.test_a_nonexistent_substitute_path_refuses.md) method: The reviewer's exact reproduction, pinned.
- [test_an_unreadable_substitute_is_not_pinned_with_a_sentinel](UnreadableSubstitute.test_an_unreadable_substitute_is_not_pinned_with_a_sentinel.md) method: HOLE: no docstring
- [test_the_refusal_names_the_offending_substitute](UnreadableSubstitute.test_the_refusal_names_the_offending_substitute.md) method: HOLE: no docstring
- [test_one_real_substitute_still_discharges](UnreadableSubstitute.test_one_real_substitute_still_discharges.md) method: Positive control: the fix must not refuse a genuine declaration.
- [test_a_sentinel_content_hash_in_a_handwritten_receipt_refuses](UnreadableSubstitute.test_a_sentinel_content_hash_in_a_handwritten_receipt_refuses.md) method: HOLE: no docstring
- [test_a_hash_pin_must_be_a_real_sha256](UnreadableSubstitute.test_a_hash_pin_must_be_a_real_sha256.md) method: HOLE: no docstring

referenced by: none found
