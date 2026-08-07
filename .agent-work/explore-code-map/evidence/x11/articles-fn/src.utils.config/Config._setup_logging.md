# src.utils.config:Config._setup_logging
class method, src/utils/config.py:178, 23 lines

```python
def _setup_logging(cls)
```

Setup logging configuration

calls stdlib: logging.FileHandler, logging.StreamHandler, logging.basicConfig, logging.info, pathlib.Path
reads internal: Config.LOGS_DIR x2, Config._config_data
reads stdlib: logging (module) x5
unresolved: 5 calls (dispatch-unknown-base), 1 calls (dynamic), 1 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
