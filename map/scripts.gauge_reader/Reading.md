# scripts.gauge_reader:Reading
class, scripts/gauge_reader.py:111, 11 lines

```python
@dataclass(frozen=True)
class Reading
```

A fresh, well-formed gauge sample.

Reaching the caller means: parsed, complete, and not stale -- staleness is
resolved inside the reader, never left for the caller to judge.

```python
schema_version: int
fill_fraction: float
model: str
observed_at: datetime
```

reads stdlib: builtins.float, builtins.int, builtins.str, datetime.datetime
writes internal: Reading.fill_fraction, Reading.model, Reading.observed_at, Reading.schema_version

referenced by: 4 sites, this module only
