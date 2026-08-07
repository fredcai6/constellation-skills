# tests.test_map_orient:CitableContent.test_the_shipped_index_template_itself_does_not_resolve
method, tests/test_map_orient.py:235, 16 lines

```python
def test_the_shipped_index_template_itself_does_not_resolve(self)
```

The scaffold this repo ships must read DEGRADED, verbatim.

Uses the real committed template rather than a copied fixture so it
cannot rot into something nobody maintains.

calls internal: CitableContent.assertEqual x2, CitableContent.assertTrue x2, verdict x2, RepoFixture, RepoFixture.file, orient, receipt_of
reads internal: SHIPPED_INDEX_TEMPLATE x3, RepoFixture.root x2
unresolved: 3 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
