# evals.euler-2-even-fibonacci.checks.spine_completed:journal_consistent
function, evals/euler-2-even-fibonacci/checks/spine_completed.py:222, 79 lines

```python
def journal_consistent(spine_path: Path, data: dict) -> tuple[bool, str]
```

Cross-verify the engine journal sidecar against the final spine (issue #131).

GRANDFATHER: a spine with no ``<spine>.journal`` passes (the journal strengthens
provenance where present but is never required -- the pre-journal reference
workspaces and any pre-journal install stay valid on lease+grammar alone).

When a journal IS present it must be internally sound AND consistent with the
spine: valid JSON lines; seq 1..N; an intact hash-chain (each line's prev_hash is
the prior line's hash, and each hash re-derives); non-decreasing timestamps that
fall within the lease window; an ``advance``/``record`` entry for every
``complete`` task; and a journal reference for every satisfied engine-checked
condition's backing evidence id.

calls internal: _parse_iso x4, _journal_hash
calls stdlib: builtins.isinstance x2, builtins.enumerate, builtins.len, builtins.str, json.loads, pathlib.Path
reads internal: ENGINE_CHECK_KINDS
reads stdlib: builtins.dict x3, builtins.OSError, builtins.ValueError, builtins.list, json (module)
unresolved: 37 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
