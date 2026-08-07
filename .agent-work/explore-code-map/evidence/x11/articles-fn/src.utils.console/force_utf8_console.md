# src.utils.console:force_utf8_console
function, src/utils/console.py:30, 4 lines

```python
def force_utf8_console() -> None
```

Make stdout and stderr UTF-8 so unicode prints don't crash under cp1252.

calls internal: force_stream_utf8 x2
reads stdlib: sys (module) x2, sys.stderr, sys.stdout

referenced by: none found (scripts/ and tests/ not indexed)
