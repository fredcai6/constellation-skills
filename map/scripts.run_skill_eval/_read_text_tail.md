# scripts.run_skill_eval:_read_text_tail
function, scripts/run_skill_eval.py:563, 13 lines

```python
def _read_text_tail(text_path) -> str
```

Best-effort tail of a run's stderr OR transcript file, for `is_infra_marker`

and `is_permission_denial` sniffing. Never raises: a missing/unreadable file
yields an empty string (which fences nothing), so a read hiccup cannot mis-fence
a run.

calls stdlib: pathlib.Path
reads internal: _STDERR_TAIL_BYTES
reads stdlib: builtins.OSError
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
