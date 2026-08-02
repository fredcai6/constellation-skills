# #668 Triage Recommendations (delegated — routed to the Admiral)

Both candidates are **recommend-and-defer**: neither clears the fix-now ladder, and GitHub
issue-filing authority is not explicitly granted by the launch order (under an epic Admiral,
filing decisions route to the Admiral). Surfaced here + in the closeout report for the Admiral
to file or drop.

## tc1 — physics region suite stalls on `test_damage_tractability.py`
- **Labels:** bug, tooling.
- **What:** `tests/unit/physics/test_damage_tractability.py` stalls the `tests/unit/physics`
  region suite indefinitely, blocking a clean full-region run. Pre-existing, unrelated to #668
  (surfaced by two #668 reviewers when they tried the region suite).
- **Importance:** medium — it prevents the region-suite evidence the project's rigor profile
  expects; each reviewer had to fall back to the targeted `instrument_panel` subset.
- **Evidence:** g2-variance-review (tc1) and the g3/g4 reviewers all reported the stall;
  `instrument_panel` subset runs clean in seconds.
- **Acceptance:** the physics region suite runs to completion (quarantine/skip or fix the
  stalling test).
- **Out of scope:** any #668 instrument logic (the stall is in an unrelated damage test).
- **Fix-now ladder:** FAILS (cold-start area, not in the #668 diff, not verifiable as part of
  this run). **Disposition: recommend-and-defer.** Deferral reason: unrelated pre-existing
  defect; filing authority sits with the Admiral.

## tc2 — dedup a shared axis-grouping helper in `replication.py`
- **Labels:** cleanup.
- **What:** `main_effect_margin_uncertainty()` and `_axis_means()` in
  `src/physics/instrument_panel/replication.py` share axis-grouping logic that a small shared
  helper could de-duplicate (Fowler `duplicated-code`, flagged non-blocking by the g6 reviewer).
- **Importance:** low — cosmetic maintainability; no behavior impact.
- **Evidence:** g6-finalize-review Fowler pass (non-blocking observation).
- **Acceptance:** a shared helper removes the duplication; all instrument_panel tests stay green,
  pyright-0, byte-identical behavior.
- **Out of scope:** any change to the signed frozen values or the double-centering method.
- **Fix-now ladder:** FAILS (editing the load-bearing replication module now re-triggers a full
  review for a purely cosmetic gain; better as a deliberate simplify-pass). **Disposition:
  recommend-and-defer.** Deferral reason: non-blocking cleanup; filing authority sits with the
  Admiral.
