# tests.test_curate_corpus:FlagsNeverGatesTests.test_maximally_flagged_fixture_still_exits_zero
method, tests/test_curate_corpus.py:380, 19 lines

```python
def test_maximally_flagged_fixture_still_exits_zero(self)
```

HOLE: no docstring

calls internal: FlagsNeverGatesTests.assertEqual x2, FlagsNeverGatesTests._build_maximally_flagged_corpus, FlagsNeverGatesTests.assertIn, FlagsNeverGatesTests.assertTrue
calls stdlib: builtins.str x2, builtins.any, builtins.sorted, pathlib.Path, tempfile.TemporaryDirectory
reads internal: cc x5
reads stdlib: tempfile (module)
unresolved: 3 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: none found
