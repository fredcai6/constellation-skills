# scripts.apply_episode_delta:is_episode_in_ordinary_search
function, scripts/apply_episode_delta.py:753, 14 lines

```python
def is_episode_in_ordinary_search(episode_id: str, root: Path) -> bool
```

Per-id membership seam (section 7), bound to Option A: a directory check.

This is the structural win the ruling buys. Membership is a filesystem fact, so a
malformed, hand-edited, or forged `- status: retired` line in a free-text field
cannot move an episode between sets — there is no field to parse and therefore no
parse to fool.

Like the other two read seams it refuses an absent store rather than answering about
one: "no, that episode is not in ordinary search" and "there is no store here" are
different facts, and a predicate that collapses them hands its caller a False that
means nothing.

calls internal: _require_store_layout
reads internal: ACTIVE_DIR
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
