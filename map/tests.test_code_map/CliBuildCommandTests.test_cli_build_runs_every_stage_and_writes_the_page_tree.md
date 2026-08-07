# tests.test_code_map:CliBuildCommandTests.test_cli_build_runs_every_stage_and_writes_the_page_tree
method, tests/test_code_map.py:193, 10 lines

```python
def test_cli_build_runs_every_stage_and_writes_the_page_tree(self)
```

HOLE: no docstring

calls internal: CliBuildCommandTests.assertTrue x2, CliBuildCommandTests.assertEqual, CliBuildCommandTests.subTest
calls cross-module: scripts.code_map.cli:main
calls stdlib: builtins.str, contextlib.redirect_stdout, io.StringIO
reads internal: CliBuildCommandTests.repo x3
reads cross-module: scripts.code_map.cli:
reads stdlib: contextlib (module), io (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
