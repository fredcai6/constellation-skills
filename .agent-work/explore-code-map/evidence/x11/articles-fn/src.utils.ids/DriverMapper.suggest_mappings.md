# src.utils.ids:DriverMapper.suggest_mappings
method, src/utils/ids.py:223, 50 lines

```python
def suggest_mappings(self, fastf1_data: pd.DataFrame, ergast_data: pd.DataFrame) -> List[Dict[str, str]]
```

Suggest potential driver mappings based on name similarity

Args:
    fastf1_data: FastF1 driver data
    ergast_data: Ergast driver data

Returns:
    List of suggested mappings

calls internal: DriverMapper.create_mapping_table
calls stdlib: builtins.len
reads internal: logger x2
reads stdlib: builtins.Exception
unresolved: 14 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
