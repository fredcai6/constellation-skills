# src.utils.constants:is_sprint_weekend
function, src/utils/constants.py:281, 12 lines

```python
def is_sprint_weekend(year: int, gp_name: str) -> bool
```

Check if a Grand Prix has a sprint format.

Args:
    year: Season year
    gp_name: Grand Prix name

Returns:
    True if sprint weekend, False otherwise

reads internal: SPRINT_WEEKENDS x2

referenced by: 4 sites, this module only
