# Archived physics design specs/plans (Epic 2 #492 / #496) — distilled 2026-06-19

These are the **spent** design specs and implementation plans for the per-session
physics fit + ideal-lap evaluator + Layer-2 frontier-view work. The work landed;
the durable *ideas* were distilled into the architecture graph and the originals
moved here as history. Do not treat these as current truth — follow the pointers.

| Archived doc | Status | Durable idea → where it now lives |
|---|---|---|
| `2026-06-17-p0-physics-fit-store.md` | landed | Fit store + evidence report → `docs/architecture/packets/physics.md` (session_fit, fit_store, fit_batch, fit_evidence) |
| `2026-06-18-p1-sim-evaluator-design.md` | landed | Sim is a two-sided CEILING evaluator (small gap = suspicious), per-car Gsat fallback, telemetry-pooled DRS mask → `decision:ideal_lap_sim_two_sided_evaluator` + physics packet (sim_evaluator) |
| `2026-06-18-p1a-sim-evaluator.md` | landed | Gsat guard + DRS mask + Δv diagnostic → physics packet (sim_evaluator), same decision anchor |
| `2026-06-18-p1b-braking-peak-kernel-design.md` | **superseded** | Smoother rounds the braking speed knee; kernel recovery fails → `decision:smoother_rounds_braking_knee`; real fix #496/#498 |
| `2026-06-18-p1b-braking-kernel.md` | **superseded** | (same; the implementation plan for the removed kernel) |
| `2026-06-18-physics-layer2-foundation-brakingview.md` | landed | Layer-2 cantilever frontier + prior-injectable params + BrakingView → `struct:physics.layer2` (physics packet, layer2 section) |

Active, non-archived design docs that still govern this area:
- `docs/superpowers/specs/2026-06-10-physics-state-space-direction-design.md` (governing direction)
- `docs/superpowers/specs/2026-06-17-physics-cross-session-pooling-design.md` (#492 Layer A)
- `docs/superpowers/specs/2026-06-18-physics-aware-estimator-design.md` (#496)
- `docs/superpowers/plans/2026-06-19-matern-kind3-physics-refinement.md` (#498, pending execution)
