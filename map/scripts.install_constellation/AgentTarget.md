# scripts.install_constellation:AgentTarget
class, scripts/install_constellation.py:35, 6 lines

```python
@dataclass(frozen=True)
class AgentTarget
```

HOLE: no docstring

```python
name: str
user_env_var: str | None
user_config_dir: str
project_config_dir: str
restart_message: str
```

reads stdlib: builtins.str x5
writes internal: AgentTarget.name, AgentTarget.project_config_dir, AgentTarget.restart_message, AgentTarget.user_config_dir, AgentTarget.user_env_var

referenced by: 8 sites, this module only
