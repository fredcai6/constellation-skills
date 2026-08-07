# tests.test_map_orient:RepoFixture.__init__
method, tests/test_map_orient.py:78, 6 lines

```python
def __init__(self, stack: unittest.TestCase, git: bool = True)
```

HOLE: no docstring

calls stdlib: pathlib.Path, tempfile.TemporaryDirectory
reads internal: RepoFixture.tmp x2, RepoFixture.root
reads stdlib: tempfile (module)
writes internal: RepoFixture.root, RepoFixture.tmp
unresolved: 3 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
