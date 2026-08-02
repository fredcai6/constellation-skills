# Implementer Handoff — tc3: backfill_estimate_store.py missing session_type (Admiral cleanup ruling)

## Task
Fix the missing-`session_type` bug in `scripts/backfill_estimate_store.py` (the D9-canonical
`session_estimates` writer) — it loads the session with the right `session_type` but never passes it into
`estimate_session(...)`, so a real FP backfill silently defaults to `quali_mass(year)`. This is the IDENTICAL
bug already fixed in `estimate_batch.run_estimate_batch`. Fixing it unblocks a clean #646 re-pop.

## Test Mode
TDD required — RED-first: write a test proving the current call omits `session_type` (or that an FP backfill
would use quali_mass), watch it fail, then fix.

## Close Criteria
- The `estimate_session(...)` call in `backfill_estimate_store.py` (around lines 140-143) passes
  `session_type=session_type` (matching `estimate_batch`'s fixed call). Also thread `db_path` if
  `estimate_session` needs it for FP mass resolution (check the signature — it gained `db_path`).
- A RED-first test (e.g. `tests/unit/physics/layer2/test_backfill_estimate_store.py` or extend an existing
  backfill test) that asserts the backfill passes `session_type` through to the estimate function (mock
  `estimate_session` / capture kwargs). Confirm it fails before the fix, passes after.
- Default (Q) behavior unchanged; existing backfill tests green.

## Allowed Scope
- `scripts/backfill_estimate_store.py`; a test file under `tests/unit/physics/layer2/`.

## Constraints
- physics-region rules; no data/*.db writes/reads in the test (mock estimate_session / use a fake).
- `py -m src.utils.simplification_limits --baseline --paths scripts/backfill_estimate_store.py` PASS.
- Do NOT run a real backfill.

## Required Evidence
- The RED output (pre-fix) + GREEN (post-fix) for the new test, plus any existing backfill test green.
- `git status --short data/` clean.

## Verification Commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_backfill_estimate_store.py -q
```

## Suggested Model Tier
`simple bounded` — one-line fix + a capture test, seam cited.

## Authority
The fix (mirror estimate_batch's `session_type=session_type` threading) is DECIDED (Admiral cleanup ruling).

## Return Format
IMPLEMENTER_RESULT to `.agent-work/513-fp-followup/result-backfill-fix.md` + SendMessage to "ShipI-513":
completed slice, files, RED→GREEN evidence, stop conditions, workflow feedback.
