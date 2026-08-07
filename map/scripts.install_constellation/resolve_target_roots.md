# scripts.install_constellation:resolve_target_roots
function, scripts/install_constellation.py:497, 15 lines

```python
def resolve_target_roots(args: argparse.Namespace, env: Mapping[str, str], cwd: Path) -> list[tuple[AgentTarget, Path]]
```

HOLE: no docstring

calls internal: resolve_target_root x2, InstallError
reads internal: AGENT_TARGETS x2
unresolved: 1 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
