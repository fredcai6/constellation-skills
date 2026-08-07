# src.utils.ids
src/utils/ids.py, 325 lines

Driver ID Mapping Utility

This module handles mapping between FastF1 and Ergast driver identifiers,
including manual overrides for edge cases and name mismatches.

imports stdlib: logging, typing.Dict, typing.List, typing.Optional
imports third-party: pandas, yaml
imported by: none found (scripts/ and tests/ not indexed)

```python
logger = logging.getLogger(__name__)
```

- [DriverMapper](DriverMapper.md) class: Maps driver identifiers between FastF1 and Ergast systems
  - [DriverMapper.__init__](DriverMapper.__init__.md) method: Initialize driver mapper
  - [DriverMapper._load_manual_mappings](DriverMapper._load_manual_mappings.md) method: Load manual override mappings from YAML file
  - [DriverMapper.map_driver_code](DriverMapper.map_driver_code.md) method: Map driver code between systems
  - [DriverMapper.map_driver_name](DriverMapper.map_driver_name.md) method: Map driver name to standard format
  - [DriverMapper.create_mapping_table](DriverMapper.create_mapping_table.md) method: Create a comprehensive mapping table between FastF1 and Ergast drivers
  - [DriverMapper.get_driver_consistency_score](DriverMapper.get_driver_consistency_score.md) method: Calculate consistency score between FastF1 and Ergast driver data
  - [DriverMapper.suggest_mappings](DriverMapper.suggest_mappings.md) method: Suggest potential driver mappings based on name similarity
  - [DriverMapper.export_mappings](DriverMapper.export_mappings.md) method: Export driver mappings to a file
  - [DriverMapper.validate_mapping](DriverMapper.validate_mapping.md) method: Validate if a driver mapping is correct
