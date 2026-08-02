# G2 Implementer Result — FastF1 version-guard hardening

## Gate
cmdr-461 / g2-implement

## Verdict
DONE — no blockers

## Changes Made

### File: `src/preprocessing/trajectory/loaders.py`

**Change 1: Added `_FASTF1_MIN_VERSION` constant**

After `_DEFAULT_CACHE = "C:/Programs/f1Brainz/data/telemetry"`, added:

```python
# Minimum tested fastf1 version.  The offline loader is exercised against
# fastf1 3.8.1; older versions may differ in Cache API shape.
_FASTF1_MIN_VERSION: str = "3.0.0"
```

**Change 2: Improved `offline_mode` AttributeError handler in `load_session_offline`**

Replaced:
```python
    try:
        fastf1.Cache.offline_mode(True)  # type: ignore[attr-defined]
    except AttributeError:
        pass
```

With:
```python
    try:
        fastf1.Cache.offline_mode(True)  # type: ignore[attr-defined]
    except AttributeError:
        _fv = getattr(fastf1, "__version__", "unknown")
        logger.warning(
            "fastf1.Cache.offline_mode() is not available in fastf1 %s "
            "(expected in versions below %s); the loader cannot enforce "
            "offline mode — the session may attempt network requests.",
            _fv,
            _FASTF1_MIN_VERSION,
        )
```

## Evidence

- `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/loaders.py`
  → `PASS (1 files checked)` ✓
- `py -c "import ast; ast.parse(open(...).read()); print('syntax OK')"` → `syntax OK` ✓
- No signature changes, no new imports, no evo-region imports added
- `fastf1` is already imported lazily inside the function (line 280)

## Constraints Satisfied
- Did NOT touch smoother.py, src/physics/*, scripts/
- No signature or behavior changes beyond adding the warning log
- No new dependencies

## Workflow Feedback
The change is trivial (5 code lines). In future, version-guard hardening of this class
should be classified as a reasoning gate from the start — the dispatcher has full context
and the change is mechanical. The crew overhead is disproportionate for changes this small.
