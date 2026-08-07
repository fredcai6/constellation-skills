# src.utils.constants:get_practice_session_types
function, src/utils/constants.py:312, 22 lines

```python
def get_practice_session_types(year: int, gp_name: str) -> List[str]
```

Return the ordered list of practice session types for a race weekend.

Modern sprint weekends (2022+) use FP1 + sprint qualifying (SQ) + sprint race (S).
Legacy sprint weekends (2021) used FP1 + FP2 — SQ/S session codes did not exist yet.
Normal weekends use FP1 + FP2 + FP3.
Q and R are never included — this is the canonical source for practice-only
session pools used by feature builders and session dropout.

Args:
    year: Season year
    gp_name: Grand Prix name

Returns:
    List of practice session type strings, e.g. ["FP1", "FP2", "FP3"]

calls internal: is_sprint_weekend
calls stdlib: builtins.list x3
reads internal: LEGACY_SPRINT_PRACTICE_SESSIONS, LEGACY_SPRINT_YEARS, NORMAL_PRACTICE_SESSIONS, SPRINT_PRACTICE_SESSIONS

referenced by: 2 sites in 2 modules (src.evo_predictor.gold_cycle.runner_support, src.evo_predictor.module_training_orchestration)
