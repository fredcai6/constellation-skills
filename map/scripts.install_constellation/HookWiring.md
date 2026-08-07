# scripts.install_constellation:HookWiring
class, scripts/install_constellation.py:603, 12 lines

```python
@dataclass(frozen=True)
class HookWiring
```

One read-only verdict about one settings.json.

```python
state: str
settings_path: Path
settings_exists: bool
resolved: tuple[str, ...] = ()
unresolved: tuple[str, ...] = ()
undeterminable: tuple[str, ...] = ()
error: str | None = None
```

reads stdlib: builtins.str x5, builtins.tuple x3, builtins.bool, pathlib.Path
writes internal: HookWiring.error, HookWiring.resolved, HookWiring.settings_exists, HookWiring.settings_path, HookWiring.state, HookWiring.undeterminable, HookWiring.unresolved

referenced by: 6 sites, this module only
