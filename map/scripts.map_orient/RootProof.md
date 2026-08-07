# scripts.map_orient:RootProof
class, scripts/map_orient.py:272, 5 lines

```python
@dataclass(frozen=True)
class RootProof
```

Whether `--root` was POSITIVELY proven to be a repo root, and by what.

```python
proven: bool
evidence: str
```

reads stdlib: builtins.bool, builtins.str
writes internal: RootProof.evidence, RootProof.proven

referenced by: 11 sites, this module only
