# scripts.episode_capture:_write_failure_stub
function, scripts/episode_capture.py:569, 41 lines

```python
def _write_failure_stub(checklist: Mapping[str, Any], iid: str, base_dir: Any, exc: BaseException) -> Path | None
```

Record that the reading was attempted and failed, rather than writing nothing.

"No file here" and "the record could not be taken" are different facts, and a
later reader has no other way to tell them apart. The stub is deliberately NOT a
valid manifest: it carries `emit_error` and `files: null`, so nothing can mistake
it for a real delivery record or for the legitimate empty one (`files: []`).

Never raises, and never overwrites an already-taken manifest. If it cannot write
either — no `context_manifest` on the path at all — it returns `None`, which is
the honest reading: the capture machinery is simply not installed here.

calls internal: manifest_root
calls stdlib: builtins.str, builtins.type, datetime.datetime.now
calls third-party: context_manifest.manifest_path, context_manifest.write_manifest
reads stdlib: builtins.Exception, datetime.datetime, datetime.timezone, datetime.timezone.utc
reads third-party: context_manifest (module) x2
unresolved: 4 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
