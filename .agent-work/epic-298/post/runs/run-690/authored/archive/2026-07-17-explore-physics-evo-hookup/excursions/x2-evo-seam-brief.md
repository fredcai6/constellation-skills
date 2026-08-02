# Excursion Brief: `x2-evo-fp-seam-and-baseline`

## The one named question

Where exactly do FP-derived features enter the live evo sampled runtime today, and what concrete evidence shows those features trailing the naive "just use FP3 order" baseline?

## Type

research

**Why this type:** seam mapping + evidence retrieval from code and run artifacts; nothing to build.

## What "answered" looks like

(a) A seam map: which of the 12 registered latent-power modules consume FP data, through which adapter/feature path (file:line), and the exact contract a NEW physics-capability module (or an injected physics prior) would have to satisfy to join the fusion — PairBatch shape, registry entry, precision-weighting expectations. (b) The artifact/number behind "FP features trail FP3": a gold report, backtest, or #601/#606 analysis showing the comparison — or an explicit finding that no such artifact exists and the claim is impressionistic. (c) Where quali prediction quality is measured today (the metric a physics feature must move).

## Budget / stop conditions

- Read-only. No training runs.
- ~30–45 min; if the FP3-baseline artifact can't be found, say so explicitly (that's a finding, not a failure).
- **Scoped nulls:** state what was and was NOT examined.

## Research excursion

- **Sources:** `src/evo_predictor/module_adapters/_registry.py`, `src/evo_predictor/fusion.py`, `src/evo_predictor/sampled_runtime.py`, feature-construction code under `src/evo_predictor/`, `src/latent_power/field_solve.py`, `params/gold/` reports + manifest, `.agent-work/601-fantasy-league/` and `.agent-work/epic-601*/` artifacts (decomposition #606, corrected quali baselines noted in the epic), GitHub issues #601/#606 via `gh`.
- **Findings format:** cited findings (file:line / artifact path / issue number per claim).

## Return

Write the full findings to `.agent-work/explore-physics-evo-hookup/excursions/x2-evo-seam-RESULT.md`. Final message = 10-line summary.
