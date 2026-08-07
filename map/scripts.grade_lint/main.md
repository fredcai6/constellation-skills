# scripts.grade_lint:main
function, scripts/grade_lint.py:748, 41 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: build_arg_parser, build_ledger, compute_exit_code, lint_one_file, load_id_universe, render_text, violation_to_dict
calls stdlib: builtins.print x3, builtins.bool, builtins.set, json.dumps, pathlib.Path
reads internal: DecisionRecord, LintToolingError, Violation
reads stdlib: builtins.list x2, sys (module) x2, sys.stderr x2, builtins.OSError, builtins.set, builtins.str, json (module)
unresolved: 3 calls (dispatch-unknown-base), 10 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
