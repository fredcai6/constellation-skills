# scripts.map_orient:build_receipt
function, scripts/map_orient.py:862, 41 lines

```python
def build_receipt(work_id: str, orientation: Orientation, substitutes: Sequence[dict], unmapped: Sequence[str], escalation: str | None, emitted_at: str, fallbacks_probed: Sequence[dict] = ()) -> dict
```

PURE. The receipt document -- schema documented in the module docstring.

calls internal: candidate_outcome
calls stdlib: builtins.dict x2, builtins.list
reads internal: Orientation.anchor_count, Orientation.candidates, Orientation.entrypoint, Orientation.mode, Orientation.root, Orientation.root_evidence, SCHEMA_VERSION
unresolved: 6 reads (dispatch-unknown-base)

referenced by: 4 sites, this module only
