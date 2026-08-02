# G3 store repopulation — state note (FULL 5-constructor scope, Commander decision)

**Checkpoint 1 (RBR):** COMPLETE — 15 fitted, 0 errors, 1653s. RBR r1-15 wired in
`data/physics_estimates_g3wired.db`. Pinned ceiling verified physical (no under-call).

**Status (now):** RUNNING the other 4 constructors (Ferrari/McLaren/Williams/Mercedes) r1-15 via
`py scripts/repopulate_g3wired_store.py --resume`. --resume skips the wired RBR (fitted today) and
force-wires the rest. ~58 sessions @ ~95-130s ≈ 1.5-2h. Log: `reports/physics/g3_repop_full.log`.

**Resumability (confirmed):** seed happens ONLY if the target db is absent (first run); a re-run on
the existing store does NOT re-seed, so completed constructors survive interruption. `--resume` skips
(gp,constructor) already wired today. OLD store `data/physics_estimates.db` verified PRISTINE (Jun 20,
220 rows, Monaco RBR a_b=26.108138 unchanged).

If interrupted: re-run the SAME command (`--resume`) — it resumes from the last completed constructor.

## Scope correction (apples-to-apples with #510)
C1's `car_prior.build_car_ceiling` pools each constructor's FULL causal history
(`round_idx <= target_round`). #510 baseline CSV: n_sessions_causal = 6/10/13/14/15 for the
dashboard target rounds. A 4-circuits-only store would mismatch (n_sessions_causal 1-4). So the
correct wired-store scope = the C1 constructors x ALL rounds 1..15, **seeded from a COPY of the
OLD store** so every other constructor retains its full causal history (each ceiling pools only
its OWN rows). OLD store `data/physics_estimates.db` is NEVER modified.

## Current run
- **Script:** `scripts/repopulate_g3wired_store.py --rbr-only` (seed OLD copy + force-wire RBR r1..15)
- **NEW store:** `data/physics_estimates_g3wired.db` (seeded from OLD, RBR rows overwritten wired)
- **Calibration:** 97s/session -> RBR ~15 sessions ~= 24 min
- **Log:** `reports/physics/g3_repop.log`
- **Probe (Monaco RBR, reproduced twice):** wired a_b=26.61, b_b=1.40e-3, cda=1.449, a_b_cold=26.34
  vs OLD a_b=26.11 / G2 synthesis a_b=26.74 -> deeper than incumbent, matches synthesis within 0.13.

## Continuation (FLAGGED for G4 / a follow-on crew)
Ferrari/McLaren/Williams/Mercedes r1..15 (~58 sessions ~= 1.5h): same script, drop `--rbr-only`:
`py scripts/repopulate_g3wired_store.py` (seeds from OLD again — or point --old-db at the RBR store).
Until run, those 4 constructors' C1 rows read OLD-braking. RBR (the primary) is fully wired now.

Implementer STAYS ACTIVE and polls to completion; does NOT declare done until the RBR-wired store
+ pinned-ceiling evidence exist.
