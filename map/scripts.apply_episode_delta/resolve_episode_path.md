# scripts.apply_episode_delta:resolve_episode_path
function, scripts/apply_episode_delta.py:704, 40 lines

```python
def resolve_episode_path(episode_id: str, root: Path) -> Path | None
```

Fetch-by-id path-resolution seam (section 7), bound to Option A: try active/,

then retired/. Returns None if the id does not exist.

At most one of the two SHOULD exist for any valid id — but "should" is the whole
point: the residual half-retired state is admitted to be possible (a hard kill
between two filesystem calls runs no compensation), so this function checks rather
than assuming. An earlier version of this docstring asserted "an episode is never in
both places at once" while the code below silently returned the active/ copy when it
was, which is the worst of both: a comment the next reader trusts instead of testing.

Fetch-by-id deliberately reaches into the archive: "where is this specific record"
is an addressed lookup, not a search, and the ruling excludes retired episodes from
*search*, never from retrieval by name.

Two refusals rather than answers, both because the alternative is a plausible wrong
answer: a store that is not there is not a store with no such episode (trap 5), and
an id present in BOTH directories is a half-retired store, not a choice between two
copies. The second one is what makes the half-retirement refusal reach fetch and the
writer, not only the scanning readers — this seam is the one they share.

First check, before anything else touches the filesystem: the id must match the
store's own grammar (ID_RE, section 2). A caller-handed id (fetch/neighbours'
anchor fetch, and every other reader routed through this seam) is never validated
upstream the way a LISTED id is (iter_episode_ids -> _layout_episode_ids runs every
filename through episode_id_for() before it becomes a candidate) — without this
check, a crafted id containing `..` path-traversal segments would resolve outside
episodes/ entirely (issue #321). A malformed id can never legitimately exist, so
`None` is the correct, contract-preserving answer here — not a new exception type.

calls internal: _reject_half_retired, _require_store_layout
calls stdlib: builtins.len
reads internal: ACTIVE_DIR, ID_RE, RETIRED_DIR
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
