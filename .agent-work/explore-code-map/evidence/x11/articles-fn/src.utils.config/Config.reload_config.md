# src.utils.config:Config.reload_config
class method, src/utils/config.py:317, 13 lines

```python
def reload_config(cls, config_file: str = 'default.yaml')
```

Reload configuration from file.

Args:
    config_file: Name of config file to reload

Returns:
    Reloaded configuration dictionary

calls internal: Config.load_config
writes internal: Config._config_data, Config._config_source

referenced by: none found (scripts/ and tests/ not indexed)
