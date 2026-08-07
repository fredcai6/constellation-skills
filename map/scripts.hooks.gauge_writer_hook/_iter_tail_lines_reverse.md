# scripts.hooks.gauge_writer_hook:_iter_tail_lines_reverse
function, scripts/hooks/gauge_writer_hook.py:272, 17 lines

```python
def _iter_tail_lines_reverse(path, max_bytes=TAIL_BYTES)
```

Yield non-blank lines from the tail of `path`, most-recent-first,

reading at most max_bytes from the end. Never raises.

calls stdlib: builtins.min, builtins.open, builtins.reversed, os.path.getsize
reads stdlib: os (module), os.path
unresolved: 5 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
