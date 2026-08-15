# IMPLEMENTER_RESULT

return: success

## Changed files

- `scripts/checklist_engine.py` — `_trip_advisory` now distinguishes a pending
  HARD gate from an in-progress gate. Pending advice states the legal sequence:
  attach a refresh-request, start the guarded gate, then `advance --why`.
- `tests/test_checklist_engine.py` — updated pending-HARD advice expectations and
  added a direct regression that performs attach → start → advance and proves the
  successor `current` retains the handoff digest.

## Red/green proof

- Red: `python -m pytest tests/test_checklist_engine.py -k TripHardGuardsBeginNotClose -q`
  produced `1 failed, 21 passed, 420 deselected`; the failing assertion exposed
  the old close-before-refresh advice.
- Green: the same command produced `22 passed, 420 deselected in 0.40s`.

## Observations

- The runtime trip/refresh guards already permit the stated sequence; this slice
  changes advisory text and regression coverage only.
- `git diff --check` passed. The source diff is restricted to `_trip_advisory`
  wording/status selection and the allowed test neighborhood. No commit or push.

## Workflow feedback

- The normal sandbox could not start (`bwrap: loopback: Failed RTM_NEWADDR`), but
  the escalated interactive TTY `apply_patch` route worked for the measured edits.
