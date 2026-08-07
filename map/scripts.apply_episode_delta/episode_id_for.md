# scripts.apply_episode_delta:episode_id_for
function, scripts/apply_episode_delta.py:481, 22 lines

```python
def episode_id_for(path: Path) -> str | None
```

THE classifier: is this file an episode, and if so, which one? Returns the

episode id, or None for a file that is not an episode at all.

Derived from the store's OWN id grammar (ID_RE, section 2) rather than from a
hand-maintained list of filenames — and that is the whole point. The first attempt
at this gate used a named allowlist (NON_EPISODE_FILENAMES) consulted at the flat
root only, and it failed in the way hand-maintained enumerations always fail: the
layout gained two directories, membership moved from content to location, and the
classifier stayed behind. Its own placeholders then became the phantom id `README`.

An id grammar cannot drift from itself. `README`, `notes`, `CODEOWNERS`, `index`,
and every future `.gitkeep`-shaped afterthought are rejected by the same rule that
accepts `governor-268-001` — no edit required when someone adds a file, and no
silent acceptance of a real stray when someone forgets to. It is also the rule that
REFUSES a bad placeholder at authoring time rather than at first read.

Uniform in all three directories: episode-ness is a property of the name, so the
answer cannot depend on which directory asked.

reads internal: ID_RE
unresolved: 1 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
