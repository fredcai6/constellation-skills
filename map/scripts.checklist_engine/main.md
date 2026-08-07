# scripts.checklist_engine:main
function, scripts/checklist_engine.py:2680, 56 lines

```python
def main(argv: list[str] | None = None) -> int
```

HOLE: no docstring

calls internal: _all_evidence_ids x2, save x2, _rail_prefix, append_journal_entry, dispatch, load, parse_args, recovery_for
calls stdlib: builtins.isinstance x2, builtins.print x2, builtins.sorted, pathlib.Path
reads internal: EngineError, MUTATING_VERBS
reads stdlib: builtins.bool, builtins.int, sys (module), sys.stderr
unresolved: 1 calls (dispatch-unknown-base), 2 calls (dynamic), 8 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
