# scripts.map_orient:collect_candidates
function, scripts/map_orient.py:1040, 43 lines

```python
def collect_candidates(root: Path, entrypoint: str | None) -> list[Candidate]
```

Impure edge: evaluate EVERY candidate, in order, and record each one.

Deliberately not short-circuiting on the first hit -- `candidates_tried[]`
is a delivery record of what was looked for, not a first-hit lookup log.

calls internal: _candidate_from_file x3, Candidate x2, _read_text, classify_packets
calls stdlib: builtins.len, builtins.sorted
reads internal: MAP_DIR x3, Candidate, GENERATED_MAP, INDEX_MD
reads stdlib: builtins.list
unresolved: 10 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
