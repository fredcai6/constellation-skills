# scripts.run_crew:CrewSpec
class, scripts/run_crew.py:424, 14 lines

```python
@dataclass
class CrewSpec
```

The parameters of one crew launch, passed to a backend's `dispatch`.

Shared by both backends; `model`/`launcher` are only meaningful to the cli
backend (the external backend spawns nothing).

```python
work_id: str
gate: str
role: str
handoff: str
result: str
worktree: str
attempt: int
model: str | None = None
launcher: str = DEFAULT_LAUNCHER
```

reads internal: DEFAULT_LAUNCHER
reads stdlib: builtins.str x8, builtins.int
writes internal: CrewSpec.attempt, CrewSpec.gate, CrewSpec.handoff, CrewSpec.launcher, CrewSpec.model, CrewSpec.result, CrewSpec.role, CrewSpec.work_id, CrewSpec.worktree

referenced by: 7 sites, this module only
