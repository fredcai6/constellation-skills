# scripts.apply_episode_delta:ensure_store_layout
function, scripts/apply_episode_delta.py:514, 11 lines

```python
def ensure_store_layout(root: Path) -> None
```

Create the store's two layout directories if they are absent — the WRITER's

bootstrap, and deliberately not a reader's.

Writing is a creating act, so `--store-root <somewhere-new>` legitimately makes a
store there. Reading is not: a reader that quietly created a missing directory would
then answer "0 episodes, exit 0" for a typo'd root, which is the silent-omission
class arriving through the back door. The read seams therefore REFUSE an absent
layout (see _require_store_layout) and only this function ever makes one.

reads internal: ACTIVE_DIR, RETIRED_DIR
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
