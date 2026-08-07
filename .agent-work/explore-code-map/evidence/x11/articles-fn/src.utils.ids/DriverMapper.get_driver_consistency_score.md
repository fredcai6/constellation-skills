# src.utils.ids:DriverMapper.get_driver_consistency_score
method, src/utils/ids.py:189, 33 lines

```python
def get_driver_consistency_score(self, fastf1_data: pd.DataFrame, ergast_data: pd.DataFrame) -> Dict[str, float]
```

Calculate consistency score between FastF1 and Ergast driver data

Args:
    fastf1_data: FastF1 driver data
    ergast_data: Ergast driver data

Returns:
    Dictionary with consistency metrics

calls internal: DriverMapper.create_mapping_table
calls stdlib: builtins.len x2
reads internal: logger
reads stdlib: builtins.Exception
unresolved: 1 calls (dispatch-unknown-base), 1 reads (dispatch-unknown-base)

referenced by: none found (scripts/ and tests/ not indexed)
