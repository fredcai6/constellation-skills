# scripts.run_skill_eval:RunResult
class, scripts/run_skill_eval.py:171, 4 lines

```python
@dataclass
class RunResult
```

HOLE: no docstring

```python
status: str
reason: str | None
check_results: list
```

reads stdlib: builtins.str x2, builtins.list
writes internal: RunResult.check_results, RunResult.reason, RunResult.status

referenced by: 16 sites, this module only
