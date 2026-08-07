# scripts.episode_capture:emit_step_manifest
function, scripts/episode_capture.py:515, 52 lines

```python
def emit_step_manifest(checklist: Mapping[str, Any], iid: str, base_dir: Any = None) -> Path | None
```

Take this step's delivery snapshot. Called by the engine, never by an agent.

Returns the manifest path, or `None` when nothing was written. MUST NOT raise,
and MUST NOT change any verb's exit code or output — see the module docstring
for why the except is broad.

Call it AFTER the status mutation. The step is selected by the engine's own
`active_id()`, and before `reopen` flips a complete gate back to `in-progress`
that selector is still pointing at a later gate — so calling early would record
the wrong step.

A `base_dir` of `None` writes nothing at all. Without the checklist's location
there is no work area to write into, and inventing one would scatter the record
outside the run it belongs to; `checklist_engine.main()` always supplies it, so
the CLI path an agent actually drives always emits.

calls internal: _write_failure_stub, emit_mechanical_snapshot, manifest_root, resolve_roots
calls third-party: context_manifest.build_manifest, context_manifest.manifest_path, context_manifest.write_manifest
reads stdlib: builtins.Exception
reads third-party: context_manifest (module) x3
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
