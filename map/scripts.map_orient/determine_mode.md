# scripts.map_orient:determine_mode
function, scripts/map_orient.py:351, 16 lines

```python
def determine_mode(root_proof: RootProof, candidates: Sequence[Candidate]) -> str
```

PURE. The reserved verdict literal for this orientation.

calls internal: candidate_is_citable, candidate_outcome
calls stdlib: builtins.all
reads internal: MODE_DEGRADED_EMPTY_MAP, MODE_DEGRADED_NO_MAP, MODE_DEGRADED_UNPARSEABLE, MODE_RESOLVED, MODE_UNRESOLVABLE_ROOT, OUTCOME_ABSENT, OUTCOME_UNPARSEABLE, RootProof.proven

referenced by: 7 sites, this module only
