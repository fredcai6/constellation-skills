# scripts.gauge_reader:thresholds_for
function, scripts/gauge_reader.py:124, 11 lines

```python
def thresholds_for(model: str) -> tuple[float, float]
```

Return the (soft, hard) fill FRACTIONS for `model`.

Converts the model's intent-first absolute caps to fractions against its own
window (`soft_cap/window`, `hard_cap/window`) -- the same `(float, float)`
shape Trip has always consumed. An unknown model falls back to
`_DEFAULT_PROFILE` (fractions == DEFAULT_THRESHOLDS), so the caller always
gets a usable pair, never a lookup failure.

reads internal: _DEFAULT_PROFILE, _PROFILES
unresolved: 1 calls (dispatch-unknown-base)

referenced by: none found
