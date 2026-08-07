# src.utils.config:Config.get
class method, src/utils/config.py:107, 14 lines

```python
def get(cls, key: str, default: Any = None) -> Any
```

Get configuration value by key (supports nested keys with dot notation)

calls internal: Config.load_config
reads stdlib: builtins.KeyError, builtins.TypeError
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 9 sites, this module only
