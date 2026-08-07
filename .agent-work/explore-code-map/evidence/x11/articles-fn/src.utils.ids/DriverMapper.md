# src.utils.ids:DriverMapper
class, src/utils/ids.py:16, 310 lines

```python
class DriverMapper
```

Maps driver identifiers between FastF1 and Ergast systems

Handles:
- FastF1 DriverNumber/Abbreviation ↔ Ergast driverId/code
- Manual override mappings for edge cases
- Driver aliases and name variations

- [__init__](DriverMapper.__init__.md) method: Initialize driver mapper
- [_load_manual_mappings](DriverMapper._load_manual_mappings.md) method: Load manual override mappings from YAML file
- [map_driver_code](DriverMapper.map_driver_code.md) method: Map driver code between systems
- [map_driver_name](DriverMapper.map_driver_name.md) method: Map driver name to standard format
- [create_mapping_table](DriverMapper.create_mapping_table.md) method: Create a comprehensive mapping table between FastF1 and Ergast drivers
- [get_driver_consistency_score](DriverMapper.get_driver_consistency_score.md) method: Calculate consistency score between FastF1 and Ergast driver data
- [suggest_mappings](DriverMapper.suggest_mappings.md) method: Suggest potential driver mappings based on name similarity
- [export_mappings](DriverMapper.export_mappings.md) method: Export driver mappings to a file
- [validate_mapping](DriverMapper.validate_mapping.md) method: Validate if a driver mapping is correct

reads stdlib: builtins.str x17, typing.Dict x4, typing.Optional x3, builtins.bool, builtins.float, typing.List
reads third-party: pandas (module) x9, pandas.DataFrame x9

referenced by: none found (scripts/ and tests/ not indexed)
