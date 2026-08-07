# scripts.map_orient:Orientation
class, scripts/map_orient.py:280, 7 lines

```python
@dataclass(frozen=True)
class Orientation
```

HOLE: no docstring

```python
root: str
mode: str
entrypoint: str | None
anchor_count: int
candidates: tuple[Candidate, ...]
root_evidence: str
```

reads internal: Candidate
reads stdlib: builtins.str x4, builtins.int, builtins.tuple
writes internal: Orientation.anchor_count, Orientation.candidates, Orientation.entrypoint, Orientation.mode, Orientation.root, Orientation.root_evidence

referenced by: 4 sites, this module only
