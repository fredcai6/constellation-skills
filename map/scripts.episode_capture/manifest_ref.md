# scripts.episode_capture:manifest_ref
function, scripts/episode_capture.py:340, 25 lines

```python
def manifest_ref(checklist: Mapping[str, Any], step: str, base_dir: Any) -> str | None
```

`context-manifest-ref` — `ctx-<work-id>-<step>@<revision>`, per

`docs/EPISODE_STORE.md` §8's `<manifest-ref>@<revision>` contract.

The revision is the manifest's own blob OID over its own bytes — the doc's
"pinning to its own blob hash at capture time", satisfied literally. This is why
g1's write-if-absent rule is load-bearing rather than tidy: a manifest that could
be rewritten later cannot be honestly pinned by revision, because the bytes behind
the pin would change underneath it.

Refuses when no manifest was taken. A `ctx-<run>-<step>@` carrying an empty or
invented revision would look exactly like a pin and resolve to nothing.

calls internal: manifest_root
calls stdlib: builtins.open
calls third-party: context_manifest.manifest_path, context_manifest.rev
reads stdlib: builtins.ImportError, builtins.OSError, builtins.ValueError
reads third-party: context_manifest (module) x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
