# Implementer Handoff — tc1: track_status explicit missingness (Admiral cleanup ruling)

## Task
In `src/physics/layer2/fp_lap_latent.py`, `extract_fp_lap_latent` sets `track_status` via an empty-string
sentinel (`... else ""`) for a missing/NULL `lap_times.track_status`. Make it EXPLICIT missingness:
`FpLapLatent.track_status: Optional[str]` = `None` on NULL (mirror the tyre_life=Optional[int] fix already
in this module). Consistency, not correctness — "" is unambiguous but None is the module's own convention now.

## Test Mode
TDD RED-first: extend the existing NULL-fixture test (the one that tests tyre_life=None) to also assert a
NULL track_status row yields `track_status is None` (not ""). Confirm RED before, GREEN after.

## Close Criteria
- `FpLapLatent.track_status` typed `Optional[str]`; extraction sets `None` (not "") when NULL; docstring notes it.
- Any downstream numeric/string use of track_status in THIS module applies a named policy at that point (there
  likely is none — it's carried through). Do NOT change semantics elsewhere.
- RED→GREEN test; existing fp_lap_latent tests stay green.

## Allowed Scope
- `src/physics/layer2/fp_lap_latent.py` + `tests/unit/physics/test_fp_lap_latent.py`.

## Constraints
- physics-region; no data/*.db in tests (tmp/in-memory); `git status --short data/` clean.
- `py -m src.utils.simplification_limits --baseline --paths src/physics/layer2/fp_lap_latent.py` PASS.
- Keep the test file < 1000 lines (split if needed).

## Required Evidence
- RED (pre-fix) + GREEN for the NULL-track_status assertion; `py -m pytest tests/unit/physics/test_fp_lap_latent.py -q` green; data clean.

## Verification Commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/test_fp_lap_latent.py -q
```

## Suggested Model Tier
`simple bounded`.

## Authority
The fix (track_status Optional[str]=None, mirror tyre_life) is DECIDED (Admiral cleanup ruling).

## Return Format
IMPLEMENTER_RESULT to `.agent-work/513-fp-followup/result-tc1.md` + SendMessage to "team-lead".
