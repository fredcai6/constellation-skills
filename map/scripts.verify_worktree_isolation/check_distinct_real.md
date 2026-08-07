# scripts.verify_worktree_isolation:check_distinct_real
function, scripts/verify_worktree_isolation.py:66, 21 lines

```python
def check_distinct_real(provisioned_paths: list[str], registered: list[str], primary: str) -> tuple[bool, str]
```

The pure multi-path decision. `provisioned_paths` are the paths the Admiral

created; `registered` is `parse_worktree_list` output; `primary` is the main
checkout. Every provisioned path must be registered, none may be the primary,
and no two may resolve to the same worktree. Returns (ok, reason); reason is
"" when ok and names the offending path otherwise.

calls internal: normalize_path x3
reads stdlib: builtins.str x2, builtins.dict

referenced by: 1 sites, this module only
