# Archived: #445 physics-envelope exploration

Archived 2026-06-17 (epic #485 / #488, branch `feat/physics-engine-445`).

This is the **exploration scratch** that derived the physics car-capability model
(`.agent-work/445/envelope/`). It is preserved here as the method record; the work
has been **productized** into `src/physics/`:

| Exploration (here) | Production |
|---|---|
| grip frontier / `ribbon_reeval`, `ideal_lap_v2` | `lateral_envelope.py`, `apex_extract.py` (#487) |
| `drs_joint_fit` / `long_throttle_probe` | `longitudinal_fit.py` (DRS-split drag + power, D1) |
| `brake_frontier` | `braking_fit.py` (Phase 5) |
| traction quadrant (`accel_order_*`, `aniso_long_fit`, `long_constraints`) | `traction_fit.py` (measured traction frontier, #488) |
| `lap_trace_v5` ideal-lap assembly | `capability_envelope.py` + `physics_simulator.py` (#488) |
| reproducible diagnostics | `scripts/plot_capability_diagnostics.py` |

**Contents:** the `.py` exploration scripts (the method record) + result `.json`/`.csv`
(e.g. `season_drs.json`, `apex_feature.json` — the validated reference data the
production-vs-exploration checks compared against). Regenerable binaries (`.npz`
caches, `.png` plots, `.log`/`.out` run logs) were dropped on archive.

**Open follow-up:** the single capability-API pathway (the other half of #491) moved
to Epic 2 (#492) — the interface needs the cross-session/season grip pool before it
can be settled.
