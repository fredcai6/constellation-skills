# scripts.gauge_reader:uncalibrated_model
function, scripts/gauge_reader.py:356, 25 lines

```python
def uncalibrated_model(gauge_path: str | Path) -> str | None
```

The model name the writer could not calibrate, or None.

Answers "why is there no reading?" so a caller can say so out loud instead
of going silently quiet -- an unexplained silent governor is how a
miscalibration survives unnoticed. Never raises; any problem is None.

Deliberately NOT staleness-checked: an uncalibrated model is a defect in
this repo's tables, not a perishable observation, and it stays true until
someone adds the row. Staleness would let the warning expire while the bug
it reports is still live.

calls stdlib: builtins.isinstance x2, json.loads, pathlib.Path
reads internal: UNCALIBRATED_FILENAME, _PROFILES
reads stdlib: builtins.OSError, builtins.ValueError, builtins.dict, builtins.str, json (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
