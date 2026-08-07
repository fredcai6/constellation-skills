# scripts.verify_lessons_applied:main
function, scripts/verify_lessons_applied.py:19, 27 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls stdlib: builtins.print x5, argparse.ArgumentParser
calls third-party: agent_work_root.durable_root, apply_lessons_delta.load_playbook, apply_lessons_delta.ripe_lessons
reads stdlib: sys (module) x3, sys.stderr x3, argparse (module), builtins.__doc__, pathlib.Path
reads third-party: apply_lessons_delta.LessonsDeltaError
unresolved: 3 calls (dispatch-unknown-base), 5 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
