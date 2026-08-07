# src.utils.ids:DriverMapper.__init__
method, src/utils/ids.py:26, 34 lines

```python
def __init__(self, override_file: Optional[str] = None)
```

Initialize driver mapper

Args:
    override_file: Path to YAML file with manual override mappings

calls internal: DriverMapper._load_manual_mappings
writes internal: DriverMapper.driver_aliases, DriverMapper.manual_mappings, DriverMapper.override_file

referenced by: none found (scripts/ and tests/ not indexed)
