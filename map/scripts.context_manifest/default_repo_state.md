# scripts.context_manifest:default_repo_state
function, scripts/context_manifest.py:311, 26 lines

```python
def default_repo_state(roots: Mapping[str, Any]) -> Mapping[str, Any]
```

The real, git-backed implementation of the `repo_state` impure edge.

Delegates to `checklist_engine.repo_revision`, the module that already shells
out to git for `git-change-policy` — this file's own source stays free of the
literal identifier `subprocess`, which is what keeps
`ProducerGuards.test_producer_shells_out_to_nothing` true after this function
exists. `roots["repo"]` is the same repo root every other declaration entry
resolves against; a checklist with no `repo` root mapped (some fixtures map
only `skill`) yields `{"commit": None, "dirty": None}` rather than raising —
the same "absence is normal" rule `read_bytes` follows for a missing file.

Returns **both** `commit` and `dirty`, deliberately. Only `commit` is
consumed: `build_manifest` takes it as the content field `repo_rev` and
**drops `dirty` on the floor** — since #327 (#305 g4) no manifest carries
that field anywhere, in content or in `run` (see the module docstring for
the measurement that settled it). Still returning both keeps
`repo_revision()` a general repo-facts primitive rather than one pre-shaped
to this module's needs — a second caller with different needs is free to use
either half, and shaping the primitive around this module's single-half
appetite would be the wrong seam.

calls stdlib: pathlib.Path
calls third-party: checklist_engine.repo_revision
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
