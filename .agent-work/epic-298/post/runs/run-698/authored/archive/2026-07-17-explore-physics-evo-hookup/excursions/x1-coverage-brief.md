# Excursion Brief: `x1-physics-estimate-coverage`

## The one named question

Which (season, session-type) cells can the physics pipeline produce per-car capability estimates for TODAY, and what concretely breaks or is missing outside the proven 2023-Q slice?

## Type

research

**Why this type:** facts from code + on-disk artifacts; nothing to build.

## What "answered" looks like

A coverage matrix (seasons 2022–2026 × session types FP1/FP2/FP3/Q/SQ/R) with three states per cell — WORKS TODAY (artifact or code path proves it), SHOULD WORK (code path exists, never run/validated), BLOCKED (named missing piece, e.g. C4 #513 FP-fits unbuilt) — each state cited to a file/artifact. Plus: where estimates are stored (store schema, tables) and the single command that produces them.

## Budget / stop conditions

- Read-only. Do not run the pipeline; judge from code, stores, docs, run artifacts.
- ~30–45 min of investigation; report inconclusive cells as UNKNOWN rather than guessing.
- **Scoped nulls:** a null verdict states what was and was NOT tested — it kills this test under these conditions, never the idea class.

## Research excursion

- **Sources:** `src/physics/` (estimate store, estimate batch, layer2 pooling, utilization), `build/pool_physics_estimates.py`, on-disk stores under `data/`, `docs/pipeline/` explainer, `docs/architecture/packets/physics.md`, `.agent-work/` archives for #509/#512 runs. Telemetry availability: the Parquet telemetry mirror (894 sessions 2018–2026, all session types) is the raw input ceiling.
- **Findings format:** cited findings (file:line or artifact path per claim); contradictions surfaced, not smoothed.

## Return

Write the full findings to `.agent-work/explore-physics-evo-hookup/excursions/x1-coverage-RESULT.md`. Final message = 10-line summary.
