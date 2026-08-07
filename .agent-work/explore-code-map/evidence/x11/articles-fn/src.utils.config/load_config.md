# src.utils.config:load_config
function, src/utils/config.py:338, 27 lines

```python
def load_config(config_file: str = 'default.yaml') -> Dict[str, Any]
```

Load configuration from YAML file.

Args:
    config_file: Path to config file or name of file in configs/ directory

Returns:
    Configuration dictionary

calls internal: Config.load_config
calls stdlib: builtins.open, pathlib.Path
calls third-party: yaml.safe_load
reads internal: Config x2, Config.CONFIG_DIR
reads stdlib: builtins.Exception
reads third-party: yaml (module) x2, yaml.YAMLError
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found (scripts/ and tests/ not indexed)
