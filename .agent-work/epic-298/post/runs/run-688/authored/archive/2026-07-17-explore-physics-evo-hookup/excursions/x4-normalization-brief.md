# Excursion Brief: `x4-normalization-stability-probe`

## The one named question

Using the existing 2019–2026 Q estimate store, which normalization scheme — absolute physical-unit estimates vs relative-to-field-per-weekend — gives more stable weekend-to-weekend per-axis readings for the same car, and roughly how many weekends does each need to resolve a slow-moving performance component?

## Type

research (with computation — read-only against stores, analysis code in scratchpad)

**Why this type:** the question is empirical and the data exists; no production code is touched.

## What "answered" looks like

Per axis (power, CdA, lateral/grip, braking, coast — whatever `session_estimates` carries): a stability comparison between (a) raw absolute estimates and (b) weekend-relative (e.g. car minus field-median that weekend) — quantified as within-season same-car variance vs between-car separation (signal-to-noise), plus a rough "weekends to resolve a 1-field-σ car difference" number per scheme. A recommendation or an honest "condition-dependent" verdict. Numbers cited to the store; method reproducible (script kept in the work area or scratchpad, path cited).

## Budget / stop conditions

- Read-only on `data/physics_estimates.db` (and `data/physics_fits.db` if useful). Analysis scripts go in the scratchpad or `.agent-work/explore-physics-evo-hookup/excursions/x4-analysis/`; nothing under `src/` is modified.
- Environment confounds (density etc.) noted, not solved — this is a probe, not a paper.
- ~45–60 min; report partial/inconclusive rather than overrun.
- **Scoped nulls:** verdicts scoped to the current five-view Q estimates; they do NOT decide what a consolidated stage-1 model could achieve.

## Research excursion

- **Sources:** `data/physics_estimates.db:session_estimates` (per-constructor, 2019–2026 Q), `src/physics/layer2/estimate_store.py` for schema, `src/utils/environment` for density context if needed.
- **Findings format:** cited numbers; per-axis table; contradictions surfaced.

## Return

Full findings → `.agent-work/explore-physics-evo-hookup/excursions/x4-normalization-RESULT.md`. Final message = 10-line summary with the recommendation.
