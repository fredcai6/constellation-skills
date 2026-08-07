# tests.test_curate_corpus:DescriptionDetectorTests.test_confusable_skill_without_exclusion_flagged
method, tests/test_curate_corpus.py:230, 12 lines

```python
def test_confusable_skill_without_exclusion_flagged(self)
```

A skill named in curate_corpus's CONFUSABLE set whose description has

no exclusion clause is flagged; the same name WITH one is only `info`.

calls internal: DescriptionDetectorTests.assertEqual, DescriptionDetectorTests.assertIn, clean_frontmatter, find, write_skill
calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: cc x3
reads stdlib: tempfile (module)
unresolved: 1 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
