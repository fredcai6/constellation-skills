# tests.test_map_orient:PartialFillMatrix.test_one_filler_poisons_a_multi_element_unmapped_list
method, tests/test_map_orient.py:393, 14 lines

```python
def test_one_filler_poisons_a_multi_element_unmapped_list(self)
```

MULTI-element on purpose.

A single-element list cannot tell `not any(is_filler)` from
`not all(is_filler)` -- they agree on lists of length 1. A floor built
only from single-element cases therefore lets a mutation between them
SURVIVE, which is exactly what happened before this test existed.

calls internal: PartialFillMatrix.assertEqual, PartialFillMatrix.subTest, RepoFixture, degraded_receipt, verify
reads internal: RepoFixture.root x2
unresolved: 1 reads (dispatch-unknown-base)

referenced by: none found
