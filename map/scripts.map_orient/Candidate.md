# scripts.map_orient:Candidate
class, scripts/map_orient.py:259, 10 lines

```python
@dataclass(frozen=True)
class Candidate
```

One entrypoint the resolver looked for, and what it found there.

```python
order: int
kind: str
path: str
exists: bool
has_content: bool
anchor_count: int
note: str
```

reads stdlib: builtins.str x3, builtins.bool x2, builtins.int x2
writes internal: Candidate.anchor_count, Candidate.exists, Candidate.has_content, Candidate.kind, Candidate.note, Candidate.order, Candidate.path

referenced by: 14 sites, this module only
