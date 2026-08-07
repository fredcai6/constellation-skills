# scripts.install_constellation:write_corpus_marker
function, scripts/install_constellation.py:1037, 25 lines

```python
def write_corpus_marker(skills_dir, source_commit: str, *, names: Iterable[str] | None = None, build_date: str | None = None) -> str
```

Compute the corpus id and write ``<skills_dir>/CORPUS.json``. Returns the id.

The marker carries ``corpus_id`` (content hash), ``source_commit`` (the
constellation commit this corpus was built from) and ``date`` (UTC build date).
``build_date`` is injectable for deterministic tests; it defaults to today.
``names`` is forwarded to :func:`compute_corpus_id`.

calls internal: compute_corpus_id
calls stdlib: datetime.date.today, json.dumps, pathlib.Path
reads internal: CORPUS_MARKER
reads stdlib: datetime.date, json (module)
writes internal: write_corpus_marker.skills_dir
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
