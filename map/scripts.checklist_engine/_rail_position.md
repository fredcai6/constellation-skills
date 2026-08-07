# scripts.checklist_engine:_rail_position
function, scripts/checklist_engine.py:244, 20 lines

```python
def _rail_position(cl: dict) -> tuple[str, dict]
```

Derive the decision-point position for a gated checklist and the tokens its

rail string needs. ``remaining`` is the ordered list of not-yet-terminal items;
its head (``remaining[0]``) is the active gate.

- ``n == 0`` -> ``terminal`` (only ``release`` remains).
- ``n == 1`` -> ``near-terminal`` (active step is the last before release).
- active gate is the first item -> ``early``.
- otherwise -> ``mid-flight``.

calls stdlib: builtins.len
reads internal: TERMINAL
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
