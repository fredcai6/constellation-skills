# Implementer Handoff — G1 None-safety fix (issue #420)

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch `constellation/issue-420-quali-anchor-production`. Python `py`.
`PYTHONIOENCODING=utf-8`.

This is a TINY, fully-specified bug fix flagged by review. Apply exactly this.

## The bug
In `src/evo_predictor/sampled_runtime.py`, `_nanmin2(a, b)` calls
`math.isfinite(a)`. But `DriverFeatures.qs_best_raw`/`lr_best_raw` CAN be `None`
at inference (data_adapter/_assemble.py:189/192 populate them via
`getattr(pf, "..._theoretical_best_raw", np.nan)` where the source attr is
`Optional[float] = None`; getattr returns None when the attr exists as None).
`math.isfinite(None)` raises TypeError -> inference crashes for any driver lacking
a raw FP theoretical best.

## The fix
Make `_nanmin2` treat `None` as missing (same as NaN). Coerce None -> nan before
`math.isfinite`:

```python
def _nanmin2(a: float | None, b: float | None) -> float:
    """Return min(a, b), treating None/NaN/non-finite as missing."""
    af = float("nan") if a is None else float(a)
    bf = float("nan") if b is None else float(b)
    a_ok = math.isfinite(af)
    b_ok = math.isfinite(bf)
    if a_ok and b_ok:
        return min(af, bf)
    if a_ok:
        return af
    if b_ok:
        return bf
    return float("nan")
```
(Adjust to match the existing style; the key points: accept None, coerce to nan,
update the type hint to `float | None`.)

## Test
Add a test (in `tests/unit/evo_predictor/test_sampled_runtime.py` next to the
existing `_nanmin2`/anchor tests, or wherever the helper is tested) covering:
- `_nanmin2(None, 79.0) == 79.0`
- `_nanmin2(80.0, None) == 80.0`
- `_nanmin2(None, None)` is nan (use math.isnan)
- `_nanmin2(float('nan'), None)` is nan
Also, if feasible, a `_anchor_quali_field`-level test with a synthetic driver
whose `qs_best_raw=None` and `lr_best_raw=None` to prove no crash (that driver
gets no anchor contribution).

## Close Criteria
- `_nanmin2` accepts None without crashing; None treated as missing.
- New tests green; all existing tests still green.
- `py -m src.utils.simplification_limits src/evo_predictor/sampled_runtime.py` clean
  (except pre-existing predict_from_features 153).

## Allowed Scope
`src/evo_predictor/sampled_runtime.py` (`_nanmin2` only) + the test file.

## Specific Exclusions
Do NOT change anything else (attach point, blend fn, config, anchor=min-of-buckets
logic all stay). No fusion files. No docs.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/evo_predictor/test_quali_pace_anchor.py -q
py -m pytest tests/unit/evo_predictor/ -q
py -m src.utils.simplification_limits src/evo_predictor/sampled_runtime.py
```

## Suggested Model Tier
Simple bounded.

## Return Format
IMPLEMENTER_RESULT: the fix, the new test, test + simplification evidence.
