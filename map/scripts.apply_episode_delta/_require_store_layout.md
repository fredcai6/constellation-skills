# scripts.apply_episode_delta:_require_store_layout
function, scripts/apply_episode_delta.py:527, 24 lines

```python
def _require_store_layout(root: Path) -> None
```

Every READ seam's first act: refuse a store that is not there.

Trap 5. `Path.glob` over a missing directory returns empty and raises nothing, so the
natural implementation answers `[]` — indistinguishable from "the store is empty",
which is trap 1's own failure description reached by a different route. A wrong
`--store-root`, or a layout that never got committed (git does not track empty
directories, and this layout is two directories), must fail visibly instead.

calls internal: EpisodeDeltaError x2
reads internal: ACTIVE_DIR x2, RETIRED_DIR x2
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
