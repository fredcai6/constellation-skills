# scripts.curate_corpus:Finding
class, scripts/curate_corpus.py:129, 14 lines

```python
@dataclass
class Finding
```

One mechanical observation. `extra` carries structured data (e.g. the

skills + example shingle of a duplication cluster) for machine consumers.

```python
skill: str
check: str
status: str
detail: str
extra: dict = field(default_factory=dict)
```

- [to_dict](Finding.to_dict.md) method: HOLE: no docstring

calls stdlib: dataclasses.field
reads stdlib: builtins.str x4, builtins.dict x3
writes internal: Finding.check, Finding.detail, Finding.extra, Finding.skill, Finding.status

referenced by: 29 sites, this module only
