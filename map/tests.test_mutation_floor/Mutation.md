# tests.test_mutation_floor:Mutation
class, tests/test_mutation_floor.py:54, 7 lines

```python
@dataclass(frozen=True)
class Mutation
```

HOLE: no docstring

```python
name: str
why: str
subs: tuple[tuple[str, str], ...]
expect_kills: str
```

reads stdlib: builtins.str x5, builtins.tuple x2
writes internal: Mutation.expect_kills, Mutation.name, Mutation.subs, Mutation.why

referenced by: 14 sites, this module only
