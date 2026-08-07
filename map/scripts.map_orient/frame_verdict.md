# scripts.map_orient:frame_verdict
function, scripts/map_orient.py:730, 96 lines

```python
def frame_verdict(receipt: dict, frame_text: str, inventory: Sequence[str]) -> tuple[str, int, list[str]]
```

PURE. (reserved first line, exit code, problems) for `verify-frame`.

The exit vocabulary is the FROZEN g1 one -- no new codes. Two of them carry
a slightly wider reading here, stated plainly rather than left implicit:

    12  a required INPUT DOCUMENT is missing or unusable. In g1 that was
        only the receipt; an absent mission frame is the same shape.
    10  the map contract is NOT discharged. In g1 that was an undischarged
        degraded record; a frame whose citations do not resolve is the same
        verdict about the same contract.

calls internal: cited_paths, cited_source_paths, declared_substitute_paths, normalize_cited_path, scan_anchors
calls stdlib: builtins.set x2
reads internal: MODE_RESOLVED x2, MODE_UNRESOLVABLE_ROOT x2, EXIT_DEGRADED_UNDISCHARGED, EXIT_OK, EXIT_RECEIPT_UNUSABLE, EXIT_UNRESOLVABLE_ROOT, FRAME_MISSING, FRAME_NAME, FRAME_OK, FRAME_REFUSED, KNOWN_FALLBACK_SET
reads stdlib: builtins.list, builtins.str
unresolved: 10 calls (dispatch-unknown-base)

referenced by: 13 sites, this module only
