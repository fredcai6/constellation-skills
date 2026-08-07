# scripts.apply_episode_delta:Assertion
class, scripts/apply_episode_delta.py:209, 19 lines

```python
@dataclass
class Assertion
```

HOLE: no docstring

```python
aid: str
kind: str
strength: str
lifecycle_standing: str
statement: str
history: list[str] = field(default_factory=list)
```

- [render](Assertion.render.md) method: HOLE: no docstring

calls stdlib: dataclasses.field
reads stdlib: builtins.str x8, builtins.list x2
writes internal: Assertion.aid, Assertion.history, Assertion.kind, Assertion.lifecycle_standing, Assertion.statement, Assertion.strength

referenced by: 8 sites, this module only
