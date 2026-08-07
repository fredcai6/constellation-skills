# scripts.measure_overread:scan_transcript
function, scripts/measure_overread.py:169, 33 lines

```python
def scan_transcript(path: str | Path) -> ScanResult
```

Scan one JSONL transcript file and count its structural reads.

calls internal: ScanResult, _read_events, classify_path
calls stdlib: builtins.isinstance, builtins.open, json.loads, pathlib.Path
reads stdlib: json (module) x2, builtins.ValueError, builtins.dict, json.JSONDecodeError
writes internal: scan_transcript.path
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
