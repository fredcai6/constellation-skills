# scripts.run_crew:main
function, scripts/run_crew.py:817, 114 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: load_registry_for_resume x3, CrewLaunchError x2, CrewSpec x2, load_registry x2, next_attempt x2, registry_path x2, abandon_crew, active_duplicate, build_parser, resume_crew, select_backend, verify_external_result
calls stdlib: builtins.print x10, pathlib.Path
reads internal: BACKEND_EXTERNAL x3, BACKEND_CLI, CrewLaunchError, DISPATCH_EXTERNAL
reads stdlib: sys (module) x3, sys.stderr x3
unresolved: 4 calls (dispatch-unknown-base), 1 calls (dynamic), 44 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
