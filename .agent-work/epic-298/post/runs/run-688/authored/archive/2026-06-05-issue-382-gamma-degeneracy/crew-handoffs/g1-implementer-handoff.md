# Implementer Handoff — G1

## Gate
`g1-implement` (issue #382, β degeneracy root-cause)

## Task
Build a self-contained diagnosis harness `scripts/diagnose_compound_beta_degeneracy.py` that produces a **measured root-cause** for why the production `compound_prior` solver emits a degenerate β (β-spread ~0 across the middle compounds, wrong-signed C1) when a cruder stdlib pooled fixed-effects fit recovers a clean monotone-down β ladder. Mirror the §1.3 ridge-dominance check.

## Protected Intent
The production compound_prior fit feeds runtime lap-time normalization (qs_* features). Sibling #380 is concurrently injecting the gate-recovered β at the EXISTING `CompoundNormalizer` interface. This gate must (a) NOT change production solver behavior, (b) NOT touch the normalizer / emitted-artifact schema (the #380 seam), (c) deliver a measured diagnosis, not a refactor.

## Test Mode
test-after allowed (scripts/ harness, exploratory/non-canonical output). No src change expected → no src region tests required. IF you find you must edit `src/compound_prior/`, STOP and return (that crosses into D2 scope and needs the Commander).

## Close Criteria
- `scripts/diagnose_compound_beta_degeneracy.py` exists, runs `py scripts/diagnose_compound_beta_degeneracy.py --smoke` exit 0 (smoke = fast path, e.g. one season or a small synthetic, that exercises every code path quickly), and a full run `py scripts/diagnose_compound_beta_degeneracy.py` emits a JSON evidence file under `.agent-work/issue-382-gamma-degeneracy/evidence/`.
- The script CONFIRMS the production degeneracy by reading the committed gold artifacts `params/gold/compound_prior/<year>/compound_prior_summary.json` (β jagged/wrong-signed C1; γ_C1..C4 identical plateau — see evidence/gold-artifacts-confirmed.md) AND prints the contrast vs the stdlib pooled-FE β ladder.
- The script MEASURES which mechanism flattens β, by ablation on the production solver run on DB-extracted observations:
  1. **Ridge-dominance (§1.3 mirror):** sweep `ridge_alpha ∈ {0, 1e-4, 1e-3, 1e-2, 1e-1, 1.0}` (use `dataclasses.replace(config, ridge_alpha=...)`); for each, report the β vector, β-spread (e.g. max−min or std across compounds), and the implied ridge shrinkage. Report the per-parameter data information `diag(X'WX)` (the weighted normal-matrix diagonal) vs `ridge_alpha` — this is the §1.3 "does the ridge dominate the data likelihood" check. State at what α the β ladder reappears.
  2. **Sparse prior:** toggle `sparse_prior_mode` none vs `support_aware_zero_shrinkage` (strength 1.0, the gold setting) and report β change.
  3. **Design/weighting vs the gate:** vendor a minimal pooled fixed-effects fit (port the method from `.agent-work/issue-382-gamma-degeneracy/prior-art/fit_compound_crossover_gate.py` — within-(driver,race) demeaning, single global φ; stdlib/numpy ok) and run it on the same DB so the script stands alone against main. Report its β ladder next to production's. Identify whether the gap is ridge, the baselined-residual design, or weighting.
- A measured ROOT-CAUSE statement for β degeneracy is written into the evidence JSON and the IMPLEMENTER_RESULT, with a fix-OR-by-design call (e.g. "ridge_alpha=1.0 shrinks β-spread by X%; β ladder recovers at α≤Y — fixable by lowering α / scaling α to data weight" vs "by design because …").

## Allowed Scope
- NEW file: `scripts/diagnose_compound_beta_degeneracy.py`
- READ/IMPORT (do not modify): `src/compound_prior/` (solver, baseline, extractor, observation_schema), `params/gold/compound_prior/*`, `data/f1_data_*.db`, prior-art/ vendored gate method.
- WRITE evidence under `.agent-work/issue-382-gamma-degeneracy/evidence/`.

## Specific Exclusions
- Do NOT modify any file under `src/compound_prior/` (especially `runtime_normalization.py` — the #380 seam — and `solver/`).
- Do NOT change `params/gold/*` artifacts.
- Do NOT call FastF1/Jolpica/live APIs — DB-only (use `src.data` DatabaseManager or read the per-season DBs; the extractor `src/compound_prior/extractor.py` + `scripts/extract_race_observations.py` show the DB→observations path).
- Do NOT depend on the un-merged `claude/compound-regime-feasibility` branch at runtime (vendor the method you need).

## Constraints
- `py` not `python`.
- DB is the only data source for analysis.
- Determinism: fixed seeds / sorted iteration so numbers are reproducible.
- Keep the harness reasonably fast; a `--smoke` flag must give a quick all-paths run. Full run may take minutes (8 seasons) — that's fine, but print progress with timestamps.
- The production solver entrypoint is `fit_compound_prior(stacked_observations, CompoundPriorFitConfig(...))` from `src.compound_prior.solver`. Gold config: `ridge_alpha=1.0, sparse_prior_mode='support_aware_zero_shrinkage', sparse_prior_strength=1.0, reference_compound='C3', accepted_compounds=('C1','C2','C3','C4','C5'), race_delta_gamma_mode='additive', effect_space normalized_fractional`. To extract observations from DB use the same path the canonical fit uses (`scripts/extract_race_observations.py` → then `fit_tire_wear_model` baseline). If reproducing the exact baselined design is heavy, you MAY ablate on the gate-style demeaned design as the comparison and read gold artifacts for the production side — but be explicit in the evidence about which design each number comes from.

## Required Evidence
- `.agent-work/issue-382-gamma-degeneracy/evidence/beta_degeneracy.json` with: gold β/γ per season (from artifacts), ridge-α sweep table (α → β vector, β-spread, diag(X'WX) summary), sparse-prior toggle result, pooled-FE β ladder, and a `root_cause` string + `fix_or_by_design` string.
- Console summary printed on full run.
- `py scripts/diagnose_compound_beta_degeneracy.py --smoke` exit-0 output.

## Verification Commands
```bash
py scripts/diagnose_compound_beta_degeneracy.py --smoke
py scripts/diagnose_compound_beta_degeneracy.py
```

## Suggested Model Tier
sonnet (bounded analysis script; clear spec; the hard thinking — hypotheses, gold config, seam boundary — is already done in this handoff and the work-area notes).

## Authority
- Decided by Commander (logged): diagnose-only, no production behavior change (D2); reproduce via gold artifacts + solver ablation (D3); vendor the pooled-FE method (D1). You must NOT decide to edit src or flip a production default — return to Commander if the diagnosis seems to require it.

## Stop Conditions
Stop and return IMPLEMENTER_RESULT if: you must edit `src/compound_prior/`, you must touch the normalizer/artifact schema, DB extraction is infeasible (note what's missing), or the measured result contradicts the H1/H2 hypotheses in a way that needs a scope decision.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (paths + key numbers), assumptions used, stop conditions hit, out-of-scope observations (esp. anything implicating the #380 seam).
