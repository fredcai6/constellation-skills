# scripts.measure_overread:scan_corpus
function, scripts/measure_overread.py:204, 6 lines

```python
def scan_corpus(corpus_dir: str | Path) -> list[ScanResult]
```

Scan every *.jsonl transcript directly under `corpus_dir`, in sorted

filename order (determinism: never directory-iteration-order dependent).

calls internal: scan_transcript
calls stdlib: builtins.sorted, pathlib.Path
writes internal: scan_corpus.corpus_dir
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base), 1 reads (unbound-name)

referenced by: 1 sites, this module only
