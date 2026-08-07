# scripts.episode_capture:_artifact_refs
function, scripts/episode_capture.py:243, 26 lines

```python
def _artifact_refs(task: Mapping[str, Any], base_dir: Any) -> list[str] | None
```

`artifact-ref` — the changed files, repo-relative, from the engine's own

collector rather than from anything an agent typed.

Deliberately NOT a new `artifact-ref` evidence type: that type has zero
occurrences across the store's ~900 evidence items, so sourcing the field there
would make it depend on an agent remembering to attach it — a second secretly
agent-dependent field, which is the class this gate exists to eliminate.

The diff policy is the step's OWN `git-change-policy` check when it has one (a
step that already declares which diff it is about is taken at its word), and
otherwise the engine's default `staged` mode. `[]` is a real answer — "nothing is
staged" — and is returned as such; `None` (refusal) is reserved for a git failure,
where the honest reading is "not knowable", not "nothing".

calls internal: _engine
calls stdlib: builtins.isinstance x3, builtins.list x2, pathlib.Path
reads stdlib: builtins.dict x4, builtins.Exception
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
