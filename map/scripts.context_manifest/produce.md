# scripts.context_manifest:produce
function, scripts/context_manifest.py:452, 11 lines

```python
def produce(checklist: Mapping[str, Any], roots: Mapping[str, Any], agent_work_root: Any, reader: Callable[[str], bytes | None] = read_bytes, repo_state: Callable[[Mapping[str, Any]], Mapping[str, Any]] = default_repo_state) -> tuple[Path, dict]
```

Build the active step's manifest and write it. Returns `(path, manifest)`.

calls internal: build_manifest, manifest_path, write_manifest
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
