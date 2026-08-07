# scripts.apply_lessons_delta:Playbook
class, scripts/apply_lessons_delta.py:124, 14 lines

```python
@dataclass
class Playbook
```

HOLE: no docstring

```python
run_tick: int
dormancy_runs: int
apply_recurrences: int
apply_confirmed: int
preamble: str
active: list[Lesson]
ticked_work_ids: list[str] = field(default_factory=list)
```

- [find](Playbook.find.md) method: HOLE: no docstring

calls stdlib: dataclasses.field
reads internal: Lesson x2
reads stdlib: builtins.int x4, builtins.list x3, builtins.str x3
writes internal: Playbook.active, Playbook.apply_confirmed, Playbook.apply_recurrences, Playbook.dormancy_runs, Playbook.preamble, Playbook.run_tick, Playbook.ticked_work_ids

referenced by: 6 sites, this module only
