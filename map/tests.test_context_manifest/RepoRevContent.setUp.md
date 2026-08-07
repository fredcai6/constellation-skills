# tests.test_context_manifest:RepoRevContent.setUp
method, tests/test_context_manifest.py:946, 9 lines

```python
def setUp(self)
```

HOLE: no docstring

calls internal: RepoRevContent.addCleanup
calls stdlib: pathlib.Path x2, tempfile.TemporaryDirectory
reads internal: RepoRevContent.repo x3, RepoRevContent.skill x3, RepoRevContent.tmp x3
reads stdlib: tempfile (module)
writes internal: RepoRevContent.repo, RepoRevContent.roots, RepoRevContent.skill, RepoRevContent.tmp
unresolved: 3 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: none found
