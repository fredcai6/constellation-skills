# tests.test_curate_corpus:DuplicationDetectorTests.test_duplication_bites_two_authentic_signatures
method, tests/test_curate_corpus.py:112, 29 lines

```python
def test_duplication_bites_two_authentic_signatures(self)
```

Compliance boilerplate in {alpha,beta} and the engine-invocation

string in {delta,gamma} produce two distinct `duplication` clusters,
each `flagged`, naming exactly the sharing skills.

calls internal: clean_frontmatter x4, write_skill x4, DuplicationDetectorTests.assertEqual x3, DuplicationDetectorTests.assertIn x2, DuplicationDetectorTests.assertGreaterEqual, find
calls stdlib: builtins.len, builtins.tuple, pathlib.Path, tempfile.TemporaryDirectory
reads internal: COMPLIANCE_BOILERPLATE x2, ENGINE_INVOCATION x2, cc x2
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base), 6 reads (dispatch-unknown-base)

referenced by: none found
