# scripts.verify_agent_feedback:main
function, scripts/verify_agent_feedback.py:225, 23 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: verify_agent_feedback
calls stdlib: builtins.print x2, argparse.ArgumentParser, builtins.str, pathlib.Path
calls third-party: agent_work_root.durable_root
reads internal: FeedbackVerificationError
reads stdlib: argparse (module), builtins.__doc__, pathlib.Path, sys (module), sys.stderr
unresolved: 4 calls (dispatch-unknown-base), 7 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
