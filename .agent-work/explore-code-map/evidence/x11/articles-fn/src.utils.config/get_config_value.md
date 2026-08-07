# src.utils.config:get_config_value
function, src/utils/config.py:367, 15 lines

```python
def get_config_value(key: str, default: Any = None) -> Any
```

Get configuration value by key.

Args:
    key: Configuration key (supports dot notation for nested keys)
    default: Default value if key not found

Returns:
    Configuration value or default

calls internal: Config.get
reads internal: Config
reads stdlib: builtins.Exception

referenced by: 1 sites in 1 modules (src.physics.physics_config)
