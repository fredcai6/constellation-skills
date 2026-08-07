# src.utils.console:force_stream_utf8
function, src/utils/console.py:15, 13 lines

```python
def force_stream_utf8(stream: TextIO | None) -> None
```

Reconfigure *stream* to UTF-8 when it supports it; otherwise do nothing.

No-op when *stream* is ``None`` or has no ``reconfigure`` (e.g. it has already
been replaced by a capture buffer), and when reconfiguration is rejected.

reads stdlib: builtins.OSError, builtins.ValueError
unresolved: 1 calls (dynamic)

referenced by: 2 sites, this module only
