# scripts.install_constellation:select_skills
function, scripts/install_constellation.py:287, 26 lines

```python
def select_skills(requested: Sequence[str] | None, available: Iterable[Skill]) -> list[Skill]
```

HOLE: no docstring

calls internal: InstallError
calls stdlib: builtins.list, builtins.set, builtins.sorted
reads internal: Skill x2
reads stdlib: builtins.str x3, builtins.list x2, builtins.dict, builtins.set
unresolved: 6 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
