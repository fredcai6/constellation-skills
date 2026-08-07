# src.utils.ids:DriverMapper.map_driver_code
method, src/utils/ids.py:77, 25 lines

```python
def map_driver_code(self, driver_code: str, source: str = 'fastf1') -> Optional[str]
```

Map driver code between systems

Args:
    driver_code: Driver code to map
    source: Source system ('fastf1' or 'ergast')

Returns:
    Mapped driver code or None if no mapping found

reads internal: DriverMapper.manual_mappings x3, DriverMapper.driver_aliases x2

referenced by: none found (scripts/ and tests/ not indexed)
