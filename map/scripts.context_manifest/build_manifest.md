# scripts.context_manifest:build_manifest
function, scripts/context_manifest.py:368, 39 lines

```python
def build_manifest(checklist: Mapping[str, Any], roots: Mapping[str, Any], reader: Callable[[str], bytes | None] = read_bytes, repo_state: Callable[[Mapping[str, Any]], Mapping[str, Any]] = default_repo_state) -> dict
```

The one envelope, for the checklist's active step.

The step is selected with the engine's own `active_id()`, and there is no way
to pin one instead: a `step=` override existed briefly and had exactly one
caller, a test, which is now spelled the way a real run is — mark the earlier
items terminal and let the selector arrive at the step. Its absence is the
point. A second way to choose the step is a second selector wearing a keyword
argument, and it would let a test assert against a step production never
reaches.

`repo_state(roots)` returns `{commit, dirty}` and only `commit` is used —
canon-determined, identical for any checkout of that commit, so it is safe as
the content field `repo_rev`. `dirty` is read from the edge and discarded
here; it reached no part of the manifest after #327 (#305 g4). The edge is
still asked for the pair because it is a general repo-facts primitive; this
assembly point is simply the one consumer, and it consumes one half. See the
module docstring for the measurement behind the removal.

calls internal: build_manifest.repo_state, declaration_of, rows, run_facts
calls stdlib: builtins.ValueError x2, builtins.dict
calls third-party: checklist_engine.active_id
reads internal: _MANIFEST_CONTRACT_VERSION
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
