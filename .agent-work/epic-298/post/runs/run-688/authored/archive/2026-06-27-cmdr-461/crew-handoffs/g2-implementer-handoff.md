# G2 Implementer Handoff — FastF1 version-guard hardening

## Work ID
cmdr-461

## Task
Harden the FastF1 version guard in `src/preprocessing/trajectory/loaders.py`.
This is item 3 from issue #461 (trajectory grading hygiene).

## Protected Intent
Add OBSERVABLE behaviour when `fastf1.Cache.offline_mode()` is unavailable in the
installed fastf1 version, by logging a warning instead of silently passing.
Also add a `_FASTF1_MIN_VERSION` constant documenting the tested minimum.
No signatures, return types, or existing behaviour should change.

## Worktree
`C:/Programs/f1Brainz-worktrees/509-461`
Branch: `chore/461-trajectory-hygiene`

## File to Edit
`src/preprocessing/trajectory/loaders.py`

## Precise Changes Required

### 1. Add `_FASTF1_MIN_VERSION` constant

After the `_DEFAULT_CACHE` constant (line ~36), add:

```python
# Minimum tested fastf1 version.  The offline loader is exercised against
# fastf1 3.8.1; older versions may differ in Cache API shape.
_FASTF1_MIN_VERSION: str = "3.0.0"
```

### 2. Improve the `offline_mode` guard in `load_session_offline`

Current code (inside `load_session_offline`, lines ~273-276):

```python
    try:
        fastf1.Cache.offline_mode(True)  # type: ignore[attr-defined]
    except AttributeError:
        pass
```

Replace with:

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

## What NOT to Change
- Do NOT touch `smoother.py`, any file in `src/physics/`, or any file in `scripts/`
- Do NOT change function signatures, return types, or call semantics
- Do NOT add any new imports (the `fastf1` import is already inside the function via
  `import fastf1  # type: ignore[import-untyped]`)
- Do NOT change `load_session()` (separate function, simpler signature)
- Do NOT change the `SessionNotCachedError` detection logic

## Allowed Scope
Only `src/preprocessing/trajectory/loaders.py` — the two specific changes above.

## Constraints
- `constraint:physics_region_no_evo_import` — no evo-region imports
- `fastf1>=3.0.0` in pyproject.toml (minimum tested version)

## Inbound Map Anchors
- **structural**: `struct:preprocessing` → `src/preprocessing/trajectory/loaders.py`
  (sole FastF1 cache reader in the package)
- **capability**: Offline FastF1 session loading without network access
- **constraint**: Physics region imports no evo-region packages

## Evidence Required
Run:
1. `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/loaders.py`
   — must output `PASS`
2. `py -m pytest tests/unit/preprocessing/ -q`
   — all tests must pass (91 items)

Report the exit codes and last 30 lines of output for each.

## Close Criteria
- `_FASTF1_MIN_VERSION = "3.0.0"` constant added after `_DEFAULT_CACHE`
- `except AttributeError` in `load_session_offline` logs a warning (not passes silently)
- simplification_limits PASS
- Unit tests green

## Authority
Delegated from Admiral to Commander (cmdr-461). No human checkpoints needed for
this mechanical code change.
