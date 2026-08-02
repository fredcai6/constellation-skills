# G2 Reviewer Handoff — FastF1 version-guard hardening

## Work ID
cmdr-461

## Your Task
Independently verify the FastF1 version-guard hardening change in
`src/preprocessing/trajectory/loaders.py`. This is item 3 from issue #461.

## Worktree
`C:/Programs/f1Brainz-worktrees/509-461`
Branch: `chore/461-trajectory-hygiene`

## What Was Implemented

In `src/preprocessing/trajectory/loaders.py`:

**Change 1**: Added after `_DEFAULT_CACHE = "C:/Programs/f1Brainz/data/telemetry"`:
```python
# Minimum tested fastf1 version.  The offline loader is exercised against
# fastf1 3.8.1; older versions may differ in Cache API shape.
_FASTF1_MIN_VERSION: str = "3.0.0"
```

**Change 2**: In `load_session_offline()`, replaced:
```python
    except AttributeError:
        pass
```
With:
```python
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

## How to Inspect
1. Read `src/preprocessing/trajectory/loaders.py` (lines ~39-45 for the constant, lines ~283-294 for the handler)
2. Verify the exact changes match the description above
3. Run: `py -m src.utils.simplification_limits --paths src/preprocessing/trajectory/loaders.py`
4. Run: `py -m pytest tests/unit/preprocessing/ -q` (note: takes ~13 min, 91 tests; waive if prior evidence suffices)

## Close Criteria
All must hold:
- [ ] `_FASTF1_MIN_VERSION = "3.0.0"` constant added after `_DEFAULT_CACHE`
- [ ] `except AttributeError: pass` replaced with logged warning using `logger.warning()`
- [ ] Warning message references both `_fv` (installed version) and `_FASTF1_MIN_VERSION` (minimum)
- [ ] `fastf1` is NOT imported at module level (import is inside the function)
- [ ] No signature changes to `load_session_offline` or any other function
- [ ] No new imports at module level
- [ ] No evo-region imports added (`src.evo_predictor`, `src.latent_power`, `src.compound_prior`)
- [ ] simplification_limits PASS

## Constraints
- Review ONLY `src/preprocessing/trajectory/loaders.py`
- Do NOT touch smoother.py, src/physics/*, scripts/

## Inbound Map Anchors
- **structural**: `struct:preprocessing` → `src/preprocessing/trajectory/loaders.py`
  (sole FastF1 cache reader; `constraint:physics_region_no_evo_import` enforced)
- **capability**: Offline FastF1 session loading with warning when offline enforcement unavailable

## Evidence from Implementer
- simplification_limits PASS ✓
- syntax OK (ast.parse) ✓
- Prior test run: 91/91 passed (background task bgqp4xql3; doc+guard changes, no behavioral change)

## Result Artifact
Write your verdict to:
`C:/Programs/f1Brainz-worktrees/509-461/.agent-work/cmdr-461/evidence/g2-review-result.md`

Format:
```
# G2 Reviewer Result
## Verdict: APPROVE / BLOCK
## Findings: <bullet list>
## Evidence: <what you checked>
## Workflow Feedback: <anything about the handoff or process>
```
