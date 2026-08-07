# scripts.map_orient:candidate_outcome
function, scripts/map_orient.py:313, 9 lines

```python
def candidate_outcome(candidate: Candidate) -> str
```

PURE. `hit` | `absent` | `empty` | `unparseable`.

calls internal: candidate_is_citable
reads internal: Candidate.exists, Candidate.has_content, OUTCOME_ABSENT, OUTCOME_EMPTY, OUTCOME_HIT, OUTCOME_UNPARSEABLE

referenced by: 6 sites, this module only
