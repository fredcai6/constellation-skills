# tests.test_curate_corpus:DuplicationDetectorTests.test_emphatic_banner_clusters_as_exact_shingle
method, tests/test_curate_corpus.py:151, 17 lines

```python
def test_emphatic_banner_clusters_as_exact_shingle(self)
```

The banner tokenizes to exactly SHINGLE_SIZE (8) words

('follow this skill strictly use the engine rigorously'), so it is the
boundary case: planted in >= 2 skills it forms exactly one shingle and
DOES cluster. (Any shorter phrase would not.)

calls internal: DuplicationDetectorTests.assertEqual x5, clean_frontmatter x2, write_skill x2, find
calls stdlib: builtins.len x2, builtins.tuple, pathlib.Path, tempfile.TemporaryDirectory
reads internal: cc x5, EMPHATIC_BANNER x3
reads stdlib: tempfile (module)
unresolved: 2 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: none found
