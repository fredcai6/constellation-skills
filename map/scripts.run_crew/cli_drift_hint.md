# scripts.run_crew:cli_drift_hint
function, scripts/run_crew.py:225, 14 lines

```python
def cli_drift_hint(stderr_text: str) -> str | None
```

Actionable message when a failed launch looks like agent-CLI flag drift

(the launcher rejected our argv) rather than a crew failure. Returns None
when the stderr carries no drift marker.

calls stdlib: builtins.any
reads internal: _CLI_DRIFT_MARKERS
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
