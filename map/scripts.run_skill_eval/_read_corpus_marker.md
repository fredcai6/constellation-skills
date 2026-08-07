# scripts.run_skill_eval:_read_corpus_marker
function, scripts/run_skill_eval.py:1138, 13 lines

```python
def _read_corpus_marker(skills_dir: Path) -> tuple[str, str | None]
```

Read (corpus_id, source_commit) from an already-installed corpus's

CORPUS.json, for the resume path (the skills tree is not reinstalled). Falls
back to recomputing the id (the marker is excluded from the hash, so the
recomputed id matches the recorded one) when the marker is missing/unreadable.

calls internal: _source_commit, stable_corpus_id
calls stdlib: json.loads, pathlib.Path
reads internal: CORPUS_MARKER
reads stdlib: builtins.KeyError, builtins.OSError, builtins.ValueError, json (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
