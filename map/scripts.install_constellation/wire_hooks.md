# scripts.install_constellation:wire_hooks
function, scripts/install_constellation.py:816, 67 lines

```python
def wire_hooks(target_root: Path, *, interpreter: str, dry_run: bool, scope: str, out: Callable[[str], object]) -> None
```

The ONE path on which this installer writes a settings.json. Reached only

from the explicit `--wire-hooks` opt-in (`decision:opt-in-wiring-only`, a
human ruling), and still a no-op under `--dry-run`.

calls internal: wire_hooks.out x7, InstallError x3, add_hook_entry, build_hook_command, build_hook_entry, installed_gauge_writer_path, settings_path_for_target_root
calls stdlib: builtins.isinstance, builtins.type, json.dumps, json.loads
reads internal: HOOK_EVENT x3, GAUGE_WRITER_HOOK_SCRIPT, SETTINGS_FILENAME
reads stdlib: builtins.dict x2, json (module) x2, builtins.OSError, builtins.ValueError
unresolved: 5 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
