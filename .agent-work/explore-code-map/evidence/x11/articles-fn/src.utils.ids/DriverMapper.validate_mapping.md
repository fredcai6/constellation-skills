# src.utils.ids:DriverMapper.validate_mapping
method, src/utils/ids.py:303, 23 lines

```python
def validate_mapping(self, fastf1_code: str, ergast_code: str) -> bool
```

Validate if a driver mapping is correct

Args:
    fastf1_code: FastF1 driver code
    ergast_code: Ergast driver code

Returns:
    True if mapping is valid, False otherwise

reads internal: DriverMapper.manual_mappings x3, DriverMapper.driver_aliases x2

referenced by: none found (scripts/ and tests/ not indexed)
