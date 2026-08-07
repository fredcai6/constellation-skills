# src.utils.ids:DriverMapper._load_manual_mappings
method, src/utils/ids.py:61, 15 lines

```python
def _load_manual_mappings(self) -> Dict[str, Dict[str, str]]
```

Load manual override mappings from YAML file

calls stdlib: builtins.isinstance, builtins.len, builtins.open
calls third-party: yaml.safe_load
reads internal: DriverMapper.override_file x2, logger x2
reads stdlib: builtins.Exception, builtins.dict
reads third-party: yaml (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
