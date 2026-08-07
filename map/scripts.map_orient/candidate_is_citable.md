# scripts.map_orient:candidate_is_citable
function, scripts/map_orient.py:303, 8 lines

```python
def candidate_is_citable(candidate: Candidate) -> bool
```

PURE. A candidate counts as a hit ONLY when it yields citable content.

Falsification floor pins this predicate (tests/test_mutation_floor.py):
weakening it to `candidate.exists` makes a scaffolded-but-empty map read
RESOLVED, which satisfies the whole contract on a map with no content.

reads internal: Candidate.anchor_count

referenced by: 5 sites, this module only
