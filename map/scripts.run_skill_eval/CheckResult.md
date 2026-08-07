# scripts.run_skill_eval:CheckResult
class, scripts/run_skill_eval.py:151, 5 lines

```python
@dataclass
class CheckResult
```

HOLE: no docstring

```python
id: str
passed: bool
evidence: str
is_answer: bool
```

reads stdlib: builtins.bool x2, builtins.str x2
writes internal: CheckResult.evidence, CheckResult.id, CheckResult.is_answer, CheckResult.passed

referenced by: 2 sites, this module only
