# src.utils.ids:DriverMapper.map_driver_name
method, src/utils/ids.py:103, 25 lines

```python
def map_driver_name(self, first_name: str, last_name: str, source: str = 'fastf1') -> Optional[str]
```

Map driver name to standard format

Args:
    first_name: Driver's first name
    last_name: Driver's last name
    source: Source system

Returns:
    Standardized driver name or None if no mapping found

reads internal: DriverMapper.driver_aliases
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found (scripts/ and tests/ not indexed)
