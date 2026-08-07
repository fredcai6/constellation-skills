# scripts.apply_episode_delta:_Transaction
class, scripts/apply_episode_delta.py:1008, 130 lines

```python
class _Transaction
```

Everything an apply_delta() run needs, kept in memory until every op in the

delta has succeeded. Nothing under self.writes/self.deletes is touched on disk
until commit() — that deferral is what makes C4 (all-or-nothing) hold even across
multiple files in one delta.

- [__init__](_Transaction.__init__.md) method: HOLE: no docstring
- [known_ids](_Transaction.known_ids.md) method: HOLE: no docstring
- [load](_Transaction.load.md) method: HOLE: no docstring
- [create](_Transaction.create.md) method: HOLE: no docstring
- [write_plan](_Transaction.write_plan.md) method: Renders every touched episode to its FINAL destination path. Returns
- [commit](_Transaction.commit.md) method: REWORK (g2 review BLOCK, defect 2): stage every touched file to a temp

reads internal: Episode x2
reads stdlib: builtins.str x3, pathlib.Path x3, builtins.set x2, builtins.dict, builtins.tuple

referenced by: 5 sites, this module only
