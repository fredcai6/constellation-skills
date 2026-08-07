# scripts.install_constellation:resolve_target_root
function, scripts/install_constellation.py:474, 21 lines

```python
def resolve_target_root(args: argparse.Namespace, agent: AgentTarget, env: Mapping[str, str], cwd: Path) -> Path
```

HOLE: no docstring

calls internal: InstallError x3, default_user_target
reads internal: AgentTarget.project_config_dir
unresolved: 5 calls (dispatch-unknown-base), 10 reads (dispatch-unknown-base)

referenced by: 2 sites, this module only
