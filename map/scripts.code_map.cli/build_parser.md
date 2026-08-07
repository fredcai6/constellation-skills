# scripts.code_map.cli:build_parser
function, scripts/code_map/cli.py:56, 16 lines

```python
def build_parser()
```

The argument parser for every stage. One `--root` per subcommand rather

than one before it, because `code_map build --root .` is the form people type.

calls internal: _Parser, _Parser.add_subparsers
calls stdlib: builtins.str
reads internal: ARTIFACTS_DIRNAME, MAP_DIRNAME, REPO_ROOT, STAGES, _WANTS_ARTIFACTS, _WANTS_OUT
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 7 sites in 2 modules (tests.test_code_map)
