# scripts.checklist_engine:load_config
function, scripts/checklist_engine.py:173, 16 lines

```python
def load_config(cl: dict, base: Path | None) -> dict
```

Resolve config: inline `config` wins; else follow `config_ref` to a file

(tried relative to the working dir, then to the checklist's dir); else empty.

calls stdlib: pathlib.Path x2, builtins.isinstance, json.loads, pathlib.Path.cwd
reads stdlib: builtins.dict, json (module), pathlib.Path
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
