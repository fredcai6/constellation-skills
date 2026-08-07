# src.utils.ids:DriverMapper.export_mappings
method, src/utils/ids.py:274, 28 lines

```python
def export_mappings(self, output_file: str, fastf1_data: pd.DataFrame, ergast_data: pd.DataFrame)
```

Export driver mappings to a file

Args:
    output_file: Output file path
    fastf1_data: FastF1 driver data
    ergast_data: Ergast driver data

calls internal: DriverMapper.create_mapping_table, DriverMapper.suggest_mappings
calls third-party: pandas.DataFrame
reads internal: logger x3
reads stdlib: builtins.Exception
reads third-party: pandas (module)
unresolved: 6 calls (dispatch-unknown-base)

referenced by: none found (scripts/ and tests/ not indexed)
