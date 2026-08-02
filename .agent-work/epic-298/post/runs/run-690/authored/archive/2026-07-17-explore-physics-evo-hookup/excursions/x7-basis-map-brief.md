# Excursion Brief: `x7-current-basis-and-dropped-correlations`

## The one named question

What underlying physical parameter basis do the current five views actually solve for — where do views share parameters vs duplicate near-identical physics under different names, and where are cross-view correlations currently dropped?

## Type

research

**Why this type:** code-truth mapping of the existing estimator; raw material for the unified-basis stage-1 design. Nothing to build.

## What "answered" looks like

(a) A basis map: every parameter each view estimates (Braking, Lateral, Traction, PowerDrag, Coast — per src/physics/layer2/session_estimator.py and the per-view fitters), in physical terms, with its σ source. (b) A duplication/correlation table: which parameters are the *same physics* measured twice (e.g. grip in braking-decel vs lateral mech grip vs traction accel; CdA in drag vs coast vs brake-aero-slope vs traction-aero-slope), and whether the current code couples them (shared solve, joint covariance) or fits them independently and drops the correlation. (c) Where the covariance JSON blobs in the estimate store capture cross-view structure vs only within-view. (d) Any existing seams that already point toward a shared basis (e.g. the decoupled-1D-longitudinal decision record, refinement-into-views in the 2023-Q pipeline).

## Budget / stop conditions

- Read-only. ~40–60 min.
- Do not propose the new design — map the current truth only; the design happens in the spec phase.
- **Scoped nulls:** "correlation dropped in code" ≠ "correlation not recoverable"; state both sides.

## Research excursion

- **Sources:** src/physics/layer2/ (session_estimator.py, estimate_store.py, per-view modules), src/physics/session_fit.py, docs/architecture/decisions/decoupled-1d-longitudinal.md, docs/architecture/packets/physics.md, the #496/#498 refinement path (build/pool_physics_estimates.py chain).
- **Findings format:** cited file:line per claim; tables.

## Return

Full findings → `.agent-work/explore-physics-evo-hookup/excursions/x7-basis-map-RESULT.md`. Final message = 10-line summary.
