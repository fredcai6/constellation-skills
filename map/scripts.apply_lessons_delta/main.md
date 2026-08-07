# scripts.apply_lessons_delta:main
function, scripts/apply_lessons_delta.py:647, 49 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: load_playbook x2, apply_delta, render_playbook, ripe_lessons
calls stdlib: builtins.print x7, builtins.len x2, argparse.ArgumentParser, builtins.sum, json.loads
calls third-party: agent_work_root.durable_root
reads internal: LessonsDeltaError
reads stdlib: json (module) x2, pathlib.Path x2, sys (module) x2, sys.stderr x2, argparse (module), builtins.OSError, builtins.__doc__, json.JSONDecodeError
unresolved: 9 calls (dispatch-unknown-base), 17 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
