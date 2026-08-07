# src.utils.ids:DriverMapper.create_mapping_table
method, src/utils/ids.py:129, 59 lines

```python
def create_mapping_table(self, fastf1_drivers: pd.DataFrame, ergast_drivers: pd.DataFrame) -> pd.DataFrame
```

Create a comprehensive mapping table between FastF1 and Ergast drivers

Args:
    fastf1_drivers: DataFrame with FastF1 driver data
    ergast_drivers: DataFrame with Ergast driver data

Returns:
    DataFrame with driver mappings

calls stdlib: builtins.len
calls third-party: pandas.DataFrame x2
reads internal: logger x2
reads stdlib: builtins.Exception
reads third-party: pandas (module) x2
unresolved: 11 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 3 sites, this module only
