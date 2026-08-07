# scripts.hooks.spine_rail:_save_json_map
function, scripts/hooks/spine_rail.py:79, 21 lines

```python
def _save_json_map(path: Path, data: dict) -> None
```

Atomically write a JSON object map. Never raises.

KNOWN, NOT CHASED (#419, deliberately outside that issue's scope; filed as
a triage candidate): the write is atomic but the surrounding
load-modify-save is NOT, and nothing takes a lock, so two agents claiming
at the same moment can lose one of the two claims. Per-agent keying widens
that window rather than creating it -- a dispatched wave now writes N
entries where it wrote one, so exposure grows with fan-out. The symptom of
a lost write is SILENCE, indistinguishable from an idle governor, and it
reintroduces exactly the blindness #419 removes. Raised independently by
two reviewers and a cold critic.

calls stdlib: builtins.open, json.dump, os.replace
reads stdlib: builtins.Exception, json (module), os (module)
unresolved: 2 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
