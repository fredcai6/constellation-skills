# scripts.run_skill_eval:write_stable_corpus_marker
function, scripts/run_skill_eval.py:535, 18 lines

```python
def write_stable_corpus_marker(skills_dir, source_commit, *, build_date=None) -> str
```

Compute the STABLE (install-path-invariant) corpus id for `skills_dir` and write

`<skills_dir>/CORPUS.json` with it. Mirrors `_install.write_corpus_marker`'s marker
shape (`{corpus_id, source_commit, date}`) — it differs ONLY in recording the stable
id instead of the raw path-dependent one, so the id the resume path reads back equals
the id the assert site checks the per-run copy against. `write_corpus_marker` itself
recomputes via raw `compute_corpus_id`, so it cannot be reused for the eval id here.

calls internal: stable_corpus_id
calls stdlib: datetime.date.today, json.dumps, pathlib.Path
reads internal: CORPUS_MARKER
reads stdlib: datetime.date, json (module)
writes internal: write_stable_corpus_marker.skills_dir
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
