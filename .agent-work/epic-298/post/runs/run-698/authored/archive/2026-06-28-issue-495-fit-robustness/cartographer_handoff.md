# Cartographer Handoff — #495 fit-robustness reconcile

## Task
Fold the #495 fit-robustness change into the recorded architecture (current-only map)
and report map impact. This is a small, local robustness fix — likely map-impact
NONE, but you decide.

## Branch / how to inspect
Branch `fix/495-fit-robustness` (main checkout). `git diff main...HEAD` or
`git diff` (uncommitted). Files changed:
- `src/physics/session_fit.py` — added an empty-speed-stream early guard returning a
  new `no_speed_stream` typed-skip in `fit_driver`, and an early `return None` guard
  in `fit_session_full`; refactored the `except ValueError` mapping to handle both
  `no_accel_samples` and `no_speed_stream` (`msg.split(":")[0]`).
- `src/preprocessing/trajectory/calibration.py` — `calibrate_session_hp` `windows=`
  branch raises a typed `ValueError("no_speed_stream: ...")` on empty `tc`/`tp`
  before `tc.min()` (was a raw `zero-size array` ValueError).
- `src/physics/fit_store.py` — `FitRecord.fit_status` comment (line 34) updated to
  the full set `ok | error | no_laps | no_accel_samples | no_speed_stream`.
- `tests/unit/physics/{test_calibration_robustness,test_475_validation_breadth}.py` —
  new tests + sentinel-set updates.
- NEW (untracked, under gitignored `/reports`): `reports/physics/495_fit_robustness_validation.md`
  (curated evidence report, sibling to the tracked P0/P1a/fit_store_evidence reports).

## What it does (capability terms)
Makes the per-session physics fit robust: the one remaining live crash (Saudi Arabia
2023 Q DEV — empty session-wide speed stream) becomes a clean typed-skip
`no_speed_stream` instead of a raw `error`. No fit-method/numeric change; no new
module; no cross-region import.

## Map context you should weigh (from the 2026-06-28 509-w3 reconcile)
The index's #495-cluster (PR #548) reconcile note recorded: "Map does not document
`SmootherHP` fields, parameter lists, or **fit-status sentinel strings** — all below
packet-description boundary. No new modules, edges, overlays, or decision anchors."
So adding the `no_speed_stream` sentinel is plausibly below the packet boundary too —
but confirm against the Inclusion Rule rather than assuming.

## Decision pressure to adjudicate (from the run)
- The enumerated **typed-skip reason set** (`no_laps`, `no_accel_samples`,
  `no_speed_stream`) is a `FitRecord` store contract. Decide whether it rises to a
  durable decision anchor or stays below the boundary (consistent with the #548
  precedent that sentinel strings are not map-documented).
- The recover-vs-skip boundary (recoverable iff streams time-overlap in flying-lap
  windows; skip iff a required stream is empty session-wide) — anchor-worthy or not?

## Verify (constraints)
- `constraint:physics_region_no_evo_import` still holds (no evo import added).
- No new module / edge / overlay introduced (confirm).
- `check_arch_map.py` green if you touch the map.

## Return
Write `.agent-work/issue-495-fit-robustness/cartographer_result.md`: map impact
(NONE or the exact packet/overlay/anchor edits made), the decision-pressure
adjudication, constraints re-verified, and any triage candidates. If map-impact NONE,
say so explicitly with the reason.
