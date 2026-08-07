# scripts.run_skill_eval:Scenario
class, scripts/run_skill_eval.py:138, 10 lines

```python
@dataclass
class Scenario
```

HOLE: no docstring

```python
id: str
task_prompt: str
process_checks: list[Path]
answer_checks: list[Path]
fixture_dir: Path | None
n: int
m: int
model: str | None
timeout_seconds: int
```

reads stdlib: builtins.int x3, builtins.str x3, pathlib.Path x3, builtins.list x2
writes internal: Scenario.answer_checks, Scenario.fixture_dir, Scenario.id, Scenario.m, Scenario.model, Scenario.n, Scenario.process_checks, Scenario.task_prompt, Scenario.timeout_seconds

referenced by: 7 sites, this module only
