# scripts.context_manifest:content
function, scripts/context_manifest.py:409, 14 lines

```python
def content(manifest: Mapping[str, Any]) -> dict
```

The part of the manifest that must be identical across environments.

Built by **admitting** `CONTENT_KEYS`, never by denying `run`. The two spellings
agree on today's envelope and disagree on every future one: a denial makes an
added key content by default, so an environment-varying field would slip into
the compared content just by existing. Admission excludes it by default and
forces a deliberate, reviewable edit to let it in.

`/run` remains the *only* exclusion. Anything else that has to be masked to make
a determinism comparison pass belongs in `/run` instead, and its presence
outside `/run` is a design defect, not a test to loosen.

reads internal: CONTENT_KEYS

referenced by: none found
