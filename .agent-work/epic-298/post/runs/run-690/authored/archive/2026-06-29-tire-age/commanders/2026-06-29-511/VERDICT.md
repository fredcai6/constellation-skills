# W3 / #511 — Tyre-age grip-evolution + supplant: VERDICT

**Per-axis readiness verdict (Phase-C, measured-not-wired):**

| axis | verdict | basis |
|---|---|---|
| **lateral_mech** (primary) | **CONTEXTUAL** | clean separable grip-DECAY axis, but does not supplant lap-time pace-degradation |
| lateral_aero | **honest-null** | insufficient separable signal at the fast-corner level |
| traction | **honest-null / →#557** | decay ladder holds but the level is ~66% residual variance |
| braking / power-drag / coast | produced, not banked | braking decay ~null (expected, #443); coast diagnostic |

## What physics CAN do (the positive result)
A **clean, monotone-up, separable, LOO-honest tyre grip-DECAY axis** on the lateral (mechanical-grip) channel:

- Pooled per-compound decay rate **k: HARD 2.94e-3 < MEDIUM 4.43e-3 < SOFT 5.53e-3 (×/lap)** — monotone-up, softer degrades faster, the expected physics.
- G3 separation **independently reviewer-APPROVED** (13/13): the tyre-decay axis separates from track-evolution via the pit-staggered fleet; car-envelope quali-anchored (relative/centred, driver→constructor) and subtracted; g_track a genuine per-circuit slope on cumulative_track_laps; **anti-circular guardrail verified** (default prior a true no-op, no #443 magnitudes, evo-free, AST-clean); LOO genuine leave-one-circuit-out.
- 1,040 driver-stint estimates, 20 races, 22 drivers; 923 dry-compound stints with finite lateral_k.

## What physics does NOT do (the bound on the bet)
It does **not supplant lap-time compound estimation at *pace*-degradation.** Against a correctly-identified, fuel-corrected lap-time degradation truth (per-race OLS: driver/stint-ordinal fixed-effects + global fuel(lap_number) + per-compound tyre_life slope), the per-compound **pace-degradation is ~flat** — because teams pit softer tyres before their cliff (strategic window selection). Result: within-race pairwise ordering accuracy P is **below coin-flip for every predictor** — physics_primary **0.313** (the best of the field), physics_pooled_loo 0.182, abs-C# textbook-hardness floor 0.182. Even the textbook hardness prior fails the flat truth.

**Key finding: grip-decay-rate ≠ run-window pace-degradation.** They are genuinely different quantities. Physics measures the former cleanly; the supplant target (the incumbent's job) is the latter.

## Honest caveats
- **Modality:** the truth is lap-time-family (same modality as the compound_prior γ incumbent); a physics win would be strong cross-modal validation, a physics non-win is partly the incumbent's home-field. The verdict does **not** NO-GO on physics-loses-to-γ; it is CONTEXTUAL because the truth itself is ~flat (window-selected) and the grip-decay axis is real and well-ordered. 2σ is a reference, not a gate.
- **An earlier probe inverted** (stint fixed-effects is rank-deficient: lap_number = stint_offset + tyre_life collinear → min-norm artifact). Corrected to driver/stint-ordinal FE before baking; a regression test guards against the naive fuel-confounded slope.

## Disposition
- **CONTEXTUAL**, consistent with #512 ("ceilings aren't pace") and #443's POC (pace is strategy/car-dominated). A bet-bounding, honest Phase-C result — not a NO-GO (the grip axis is real), not a clean GO (no pace-degradation supplant).
- The grip-decay axis is usable as a **feature for a race-sim pace-curve that models the window-selection** (Phase-P #450) — not as a drop-in pace-degradation predictor.
- Triage: traction level honest-null → #557; net-new g_track pooling term → decision candidate; live-γ + #443 telemetry-truth triangulation, non-window-selected (full-stint-to-cliff) truth, and multi-season → epic-closeout 25-ideas.

Dashboard: `reports/physics/tyre_age_2023.md` (+ gitignored PNGs). Modules: `src/physics/layer2/{race_stint_batch, tyre_separation, tyre_supplant}.py`. Supplant orchestrator: `tyre_supplant.run_supplant`.
