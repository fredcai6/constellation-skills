# scripts.checklist_engine:build_payload
function, scripts/checklist_engine.py:2491, 12 lines

```python
def build_payload(args: argparse.Namespace) -> dict
```

Assemble an attach payload without forcing JSON through the shell.

Priority: --payload-file, then --payload (JSON), then --field K=V pairs.

calls internal: EngineError
calls stdlib: json.loads x2, pathlib.Path
reads stdlib: json (module) x2
unresolved: 2 calls (dispatch-unknown-base), 3 calls (dynamic), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
