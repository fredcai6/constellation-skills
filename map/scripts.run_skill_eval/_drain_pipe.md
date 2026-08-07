# scripts.run_skill_eval:_drain_pipe
function, scripts/run_skill_eval.py:621, 10 lines

```python
def _drain_pipe(pipe, file_obj) -> None
```

Copy a child pipe to its capture file until EOF. Swallows OSError/ValueError

so an abandoned daemon drainer (grandchild still holding the write-handle, file
already closed) dies quietly instead of surfacing a spurious error.

calls stdlib: builtins.iter
reads internal: _PIPE_CHUNK_BYTES
reads stdlib: builtins.OSError, builtins.ValueError
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
