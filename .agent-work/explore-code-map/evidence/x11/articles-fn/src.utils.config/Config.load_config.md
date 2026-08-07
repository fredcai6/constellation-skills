# src.utils.config:Config.load_config
class method, src/utils/config.py:49, 56 lines

```python
def load_config(cls, config_file: str = 'default.yaml') -> Dict[str, Any]
```

Load and validate configuration from YAML file.

Args:
    config_file: Name of config file in configs/ directory

Returns:
    Validated configuration dictionary

Raises:
    ConfigurationError: If config file missing or invalid

calls internal: Config._setup_fastf1_cache, Config._setup_logging, Config._validate_config
calls cross-module: src.models.exceptions:ConfigurationError x3
calls stdlib: builtins.str x4, builtins.open, pathlib.Path
calls third-party: yaml.safe_load
reads internal: Config._config_data x6, Config._config_source x2, Config.CONFIG_DIR
reads third-party: yaml (module) x2, yaml.YAMLError
writes internal: Config._config_data, Config._config_source
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 3 sites, this module only
