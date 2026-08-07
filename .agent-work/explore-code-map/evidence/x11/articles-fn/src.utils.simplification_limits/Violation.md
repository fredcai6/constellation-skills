# src.utils.simplification_limits:Violation
class, src/utils/simplification_limits.py:32, 13 lines

```python
@dataclass(frozen=True)
class Violation
```

HOLE: no docstring

```python
path: str
symbol: Optional[str]
metric: str
actual: int
limit: int
```

- [format_message](Violation.format_message.md) method: HOLE: no docstring

reads stdlib: builtins.str x4, builtins.int x2, typing.Optional
writes internal: Violation.actual, Violation.limit, Violation.metric, Violation.path, Violation.symbol

referenced by: 10 sites, this module only
