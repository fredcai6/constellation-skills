# scripts.run_crew:_require_handoff
function, scripts/run_crew.py:309, 10 lines

```python
def _require_handoff(handoff: str, root: Path, *, action: str) -> Path
```

Resolve the handoff path against root and REFUSE if it is missing. `action`

("launch" | "record") shapes the refusal message so the spawn and external
paths keep their distinct wording.

calls internal: CrewLaunchError
calls stdlib: pathlib.Path
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
