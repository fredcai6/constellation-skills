# scripts.map_orient:build_orientation
function, scripts/map_orient.py:369, 16 lines

```python
def build_orientation(root_abs: str, root_proof: RootProof, candidates: Sequence[Candidate]) -> Orientation
```

PURE. Fold the root proof and every candidate into one verdict.

calls internal: Orientation, candidate_is_citable, determine_mode
calls stdlib: builtins.next, builtins.tuple
reads internal: MODE_RESOLVED, RootProof.evidence
unresolved: 2 reads (dispatch-unknown-base)

referenced by: 5 sites, this module only
