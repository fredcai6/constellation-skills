# tests.test_episode_store:PathTraversalGuardTests
class, tests/test_episode_store.py:795, 62 lines

```python
class PathTraversalGuardTests(TestCase)
```

Issue #321 — resolve_episode_path() is the ONE seam every id-taking reader

(fetch_episode, neighbours' anchor fetch, the writer's own Transaction.load())
already routes through. Before this fix it built `root / sub / f"{episode_id}.md"`
from a caller-handed id with zero format validation, then only checked `.exists()`
— so a crafted id containing `..` segments could resolve outside episodes/
entirely and read an arbitrary file that happens to exist at the traversed
location. This proves the exposure existed AND that the ID_RE.fullmatch() guard
now closes it — not merely that a not-found id returns None (a well-formed absent
id already returned None before this fix too, which would be a check that cannot
fail).

```python
TRAVERSAL_TARGET = ROOT / 'SKILL_INDEX.md'
```

- [setUp](PathTraversalGuardTests.setUp.md) method: HOLE: no docstring
- [tearDown](PathTraversalGuardTests.tearDown.md) method: HOLE: no docstring
- [test_traversal_id_would_have_escaped_the_store_and_the_guard_now_blocks_it](PathTraversalGuardTests.test_traversal_id_would_have_escaped_the_store_and_the_guard_now_blocks_it.md) method: HOLE: no docstring

reads internal: ROOT
writes internal: PathTraversalGuardTests.TRAVERSAL_TARGET

referenced by: none found
