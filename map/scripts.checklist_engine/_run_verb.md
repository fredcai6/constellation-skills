# scripts.checklist_engine:_run_verb
function, scripts/checklist_engine.py:2557, 40 lines

```python
def _run_verb(cl: dict, args: argparse.Namespace, base_dir: Path | None) -> str
```

Execute a mutating verb and return its message, or raise EngineError if the

verb refuses. Read-only/lease verbs are handled by `dispatch` before this.

calls internal: EngineError x2, advance, amend, append, attach, attest, block, build_payload, consolidate, flag_candidate, load_config, record, reopen, resume, rework_cap, skip, start, waive
calls stdlib: json.loads, pathlib.Path
reads stdlib: builtins.OSError, builtins.ValueError, json (module)
unresolved: 1 calls (dispatch-unknown-base), 5 calls (dynamic), 40 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
