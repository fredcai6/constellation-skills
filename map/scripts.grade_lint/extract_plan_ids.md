# scripts.grade_lint:extract_plan_ids
function, scripts/grade_lint.py:411, 14 lines

```python
def extract_plan_ids(data) -> set[str]
```

The known gate/item id universe a JSON plan self-sources: its top-level

`items` list plus its `tasks` keys.

calls stdlib: builtins.isinstance x4, builtins.str x3, builtins.set
reads stdlib: builtins.dict x2, builtins.list x2, builtins.set, builtins.str
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
