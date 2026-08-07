# tests.test_code_map:CliBuildCommandTests.test_cli_build_maps_the_corpus_and_not_the_scratch
method, tests/test_code_map.py:204, 8 lines

```python
def test_cli_build_maps_the_corpus_and_not_the_scratch(self)
```

The exclusion has to hold through the whole pipeline, not only at the

discovery call: a scratch module reaching the page tree is the failure
this gate exists to prevent.

calls internal: CliBuildCommandTests.assertEqual
calls cross-module: scripts.code_map.cli:main
calls stdlib: builtins.sorted, builtins.str, contextlib.redirect_stdout, io.StringIO
reads internal: CliBuildCommandTests.repo x2
reads cross-module: scripts.code_map.cli:
reads stdlib: contextlib (module), io (module)
unresolved: 2 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found
