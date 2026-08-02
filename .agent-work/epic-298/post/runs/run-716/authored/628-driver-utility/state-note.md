# Crash-resume state note — #628 Ship H (updated live)

- **Spine:** C:/Programs/f1-628/.agent-work/628-driver-utility/spine.json (engine lease session-id `ship-h-628`)
- **Execute plan:** C:/Programs/f1-628/.agent-work/628-driver-utility/execute.json (gates G1..G5)
- **Current step:** execute → e0-context (about to drive G1)
- **Next command:** drive execute.json gate-by-gate via the engine (start/advance with --session-id ship-h-628)
- **Branch/worktree:** feat/628-driver-utility @ C:/Programs/f1-628 (base main 61b1c76e)
- **DBs (read-only, in MAIN checkout):** C:/Programs/f1Brainz/data/physics_estimates.db, telemetry_store.db
- **Detached compute (G5, not yet launched):** scratch DB data/driver_utility_observables.db (UNTRACKED);
  launch via Start-Process -WindowStyle Hidden; PID: <none yet>; expected artifact: observable rows in scratch DB.
- **DB hygiene:** NEVER commit data/*.db; git checkout -- data/ any dirtied DB before each gate advance.
