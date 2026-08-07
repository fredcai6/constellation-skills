# scripts.run_skill_eval:main
function, scripts/run_skill_eval.py:1300, 47 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: run_scenario x3, _apply_overrides, _print_verdict, build_parser, load_scenario
calls stdlib: builtins.print x5, pathlib.Path x4, builtins.dict, tempfile.TemporaryDirectory, tempfile.mkdtemp
reads internal: _dry_installer x2, EvalConfigError, dry_run_fail_launch, dry_run_launch, launch_agent, temp_install
reads stdlib: sys (module) x5, sys.stderr x5, tempfile (module) x2
unresolved: 2 calls (dispatch-unknown-base), 14 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
