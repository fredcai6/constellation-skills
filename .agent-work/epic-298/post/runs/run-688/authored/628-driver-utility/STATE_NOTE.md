# Crash-resume state note — #628 Ship H

- **step:** execute — G5 in progress; detached observable batch RUNNING; poll scratch DB row count in-turn
- **slug:** 628-driver-utility
- **next command:** poll `sqlite3 data/driver_utility_observables.db "select count(*) from ..."` (or python) until ~240 driver-sessions covered; then run G2 estimator + G3 gate per frozen-methodology.md
- **pid:** 18012 (detached hidden python.exe; log .agent-work/628-driver-utility/logs/g5-batch.out/.err)
- **expected artifact:** data/driver_utility_observables.db (untracked scratch rows, 2023-Q R1-12, 21 drivers) → then data/driver_utility.db banked artifact + held-out verdict numbers in wave7-628-verdict.md

## Context
- Engine lease session-id: ship-h-628. Worktree C:/Programs/f1-628 branch feat/628-driver-utility (base 61b1c76e).
- DBs read-only in MAIN checkout: C:/Programs/f1Brainz/data/{physics_estimates.db,telemetry_store.db}.
- DB hygiene: NEVER commit data/*.db; git checkout -- data/ before each gate advance.
- G5 detached launch: Start-Process -WindowStyle Hidden; update pid here before detaching.
