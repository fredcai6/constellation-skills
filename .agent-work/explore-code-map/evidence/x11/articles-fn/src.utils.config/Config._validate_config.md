# src.utils.config:Config._validate_config
class method, src/utils/config.py:243, 72 lines

```python
def _validate_config(cls)
```

Validate configuration schema and required fields.

Raises:
    ConfigurationError: If required fields are missing or invalid

calls cross-module: src.models.exceptions:ConfigurationError x8
calls stdlib: builtins.isinstance x3, builtins.list, builtins.type
reads internal: Config._config_data x2
reads stdlib: builtins.int x2, builtins.list x2, builtins.dict
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
