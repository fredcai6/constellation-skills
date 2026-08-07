# scripts.apply_lessons_delta:Lesson
class, scripts/apply_lessons_delta.py:65, 56 lines

```python
@dataclass
class Lesson
```

HOLE: no docstring

```python
lesson_id: str
scope: str
task_class: str
statement: str
grounding: str
bank_reason: str = ''
mentions: int = 1
confirmed: int = 0
disconfirmed: int = 0
recurrences: int = 0
status: str = 'active'
added: str = ''
last_confirmed: str = 'none'
runs_since_confirmed: int = 0
target: str = ''
deferred_at: int = -1
retired: str = ''
history: list[str] = field(default_factory=list)
```

- [render](Lesson.render.md) method: HOLE: no docstring

calls stdlib: dataclasses.field
reads stdlib: builtins.str x13, builtins.int x6, builtins.list x2
writes internal: Lesson.added, Lesson.bank_reason, Lesson.confirmed, Lesson.deferred_at, Lesson.disconfirmed, Lesson.grounding, Lesson.history, Lesson.last_confirmed, Lesson.lesson_id, Lesson.mentions, Lesson.recurrences, Lesson.retired, Lesson.runs_since_confirmed, Lesson.scope, Lesson.statement, Lesson.status, Lesson.target, Lesson.task_class

referenced by: 10 sites, this module only
