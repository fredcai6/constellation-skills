# scripts.run_skill_eval:LaunchOutcome
class, scripts/run_skill_eval.py:159, 9 lines

```python
@dataclass
class LaunchOutcome
```

The observable result of one launch attempt. `launch_agent` (and the fake

launchers) return this; `classify_run` consumes it. Fenceable conditions are
flags so classification stays a pure function of the outcome.

```python
exit_code: int | None
stderr_text: str = ''
timed_out: bool = False
launch_error: bool = False
corpus_mismatch: bool = False
```

reads stdlib: builtins.bool x3, builtins.int, builtins.str
writes internal: LaunchOutcome.corpus_mismatch, LaunchOutcome.exit_code, LaunchOutcome.launch_error, LaunchOutcome.stderr_text, LaunchOutcome.timed_out

referenced by: 11 sites, this module only
