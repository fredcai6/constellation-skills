# tests.test_curate_corpus:DuplicationDetectorTests.test_duplication_ignores_a_single_planting
method, tests/test_curate_corpus.py:142, 8 lines

```python
def test_duplication_ignores_a_single_planting(self)
```

A signature in only one skill must NOT cluster (needs >= 2 skills).

calls internal: clean_frontmatter x2, write_skill x2, DuplicationDetectorTests.assertEqual, find
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: COMPLIANCE_BOILERPLATE, cc
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
