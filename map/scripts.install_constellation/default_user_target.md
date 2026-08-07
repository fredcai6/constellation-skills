# scripts.install_constellation:default_user_target
function, scripts/install_constellation.py:466, 6 lines

```python
def default_user_target(agent: AgentTarget, env: Mapping[str, str]) -> Path
```

HOLE: no docstring

calls internal: home_from_env
calls stdlib: pathlib.Path
reads internal: AgentTarget.user_env_var x2, AgentTarget.user_config_dir
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
