# scripts.measure_overread:_read_events
function, scripts/measure_overread.py:146, 21 lines

```python
def _read_events(record: dict)
```

Yield each `Read` tool_use block's `input.file_path` string found in

one decoded transcript line's `message.content`. Never raises on
unexpected shape -- an unrecognized block is simply not a Read event.

calls stdlib: builtins.isinstance x5
reads stdlib: builtins.dict x3, builtins.list, builtins.str
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
