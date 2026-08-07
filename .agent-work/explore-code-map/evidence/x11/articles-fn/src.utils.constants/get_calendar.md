# src.utils.constants:get_calendar
function, src/utils/constants.py:263, 16 lines

```python
def get_calendar(year: int) -> List[str]
```

Get F1 calendar for a specific year.

Args:
    year: Season year

Returns:
    List of GP names in calendar order

Raises:
    KeyError: If year is not in calendars

calls stdlib: builtins.KeyError, builtins.list
reads internal: F1_CALENDARS x3
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 20 sites in 14 modules (src.data.collector, src.evo_predictor.data_adapter._build, src.evo_predictor.data_adapter._helpers, src.evo_predictor.data_adapter._memory, src.evo_predictor.module_training_evidence_modes, src.evo_predictor.module_training_orchestration, src.evo_predictor.pipeline, src.evo_predictor.recency_features, src.evo_predictor.sampled_backtest, src.physics.fit_batch, src.physics.ideal_lap.residuals, src.physics.layer2.estimate_batch, src.physics.layer2.grip_batch, src.physics.wear.batch)
