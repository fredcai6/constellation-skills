# scripts.checklist_engine:_collect_changed_files
function, scripts/checklist_engine.py:642, 53 lines

```python
def _collect_changed_files(policy: dict, base_dir: Path | None) -> list[dict]
```

Thin git collector: gather `{path, size, binary}` for the changed files.

mode `staged` -> `git diff --cached`; mode `branch` -> `git diff <base>...HEAD`.
Binary detection uses `git diff --numstat` (a binary file shows `-  -`).
Size comes from the working-tree file when present, else `git cat-file` on
the staged/HEAD blob. Kept small and isolated so the PURE evaluator carries
the testable logic.

calls internal: _git x3, EngineError
calls stdlib: builtins.int, builtins.len, builtins.set, pathlib.Path.cwd
reads stdlib: builtins.OSError, builtins.ValueError, builtins.dict, builtins.list, builtins.set, builtins.str, pathlib.Path
writes internal: _collect_changed_files.policy
unresolved: 12 calls (dispatch-unknown-base), 8 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
