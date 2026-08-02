# Reviewer Handoff — G4

## Gate
`g4`

## Survey State Location
`.agent-work/629-feature-view/g4-review/review.json`.

## What Was Implemented
`src/physics/feature_view/build_lap_evidence.py` —
`build_lap_evidence_records(latents, *, year, gp_name, session_type, model_version,
quali_fuel_kg=NOMINAL_QUALI_FUEL_KG, track_evolution=None, session_max_track_evolution=None)`
composes `LapEvidenceRecord` rows from `FpLapLatent` objects. Plus
`tests/unit/physics/feature_view/test_build_lap_evidence.py` (9 new tests).

## How to Inspect the Diff
Uncommitted working tree, `C:/Programs/f1-629`, branch `feat/629-feature-view`. Read the new
file and test file directly.

## Task Statement
Full detail: `.agent-work/629-feature-view/g4-implementer-handoff.md`. Full evidence:
`.agent-work/629-feature-view/g4-implementer-result.md`.

## Close Criteria
- `representativeness_weight` genuinely equals a direct
  `observation_weight(observation_features(latent, quali_fuel_kg=..., track_evolution=...,
  session_max_track_evolution=...))` call — reproduce this yourself with your own constructed
  `FpLapLatent`, not just reading the implementer's test.
- `mass_kg`/`mass_sigma_kg`/`run_purpose`/`compound` are straight copies from the input
  `FpLapLatent` — confirm no transformation/rounding/renaming occurs.
- `track_evolution`'s DB-read boundary is respected: confirm `extract_fp_lap_latent` and
  `session_race.compute_cumulative_track_laps` are NOT imported/called in the new file (grep);
  confirm the optional `{lap_number: cumulative}` mapping genuinely changes the computed weight
  when present vs. absent (construct your own case), and that a MISSING lap_number key in a
  non-empty mapping behaves identically to no mapping at all (both fall through to `None` ->
  `NEUTRAL_TRACK_EVOLUTION_SCORE`), not a KeyError or a fabricated 0.
- `unit_class_residuals` stays `None`/`"unresolved"` on every produced record — try to
  construct a call path that would set it to confirm it's genuinely impossible (G1's
  `__post_init__` guard should raise).
- `quali_fuel_kg` defaults to `mass_model.NOMINAL_QUALI_FUEL_KG` (the real named constant,
  value `10.0`), not a hardcoded literal — read the import and default value directly.
- No `src.evo_predictor` import.
- `py -m pytest tests/unit/physics/feature_view -q` green — reproduce count (57 expected:
  27+6+15+9).
- `simplification_limits --paths src/physics/feature_view` clean.

## Allowed Scope
`src/physics/feature_view/build_lap_evidence.py` (new); `tests/unit/physics/feature_view/
test_build_lap_evidence.py` (new). Nothing else.

## Specific Exclusions
G1/G2/G3 files are CLOSED — confirm untouched, do not flag as in-scope.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import`.
- No DB read inside the composer (`extract_fp_lap_latent`/`compute_cumulative_track_laps` not
  called).
- `unit_class_residuals` never fabricated.
- Tests need no DB at all (synthetic `FpLapLatent` construction only).

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` (read-only: `fp_lap_latent`,
  `fp_representativeness`), `struct:physics` (`mass_model`), `struct:physics.feature_view`.
- **Capability:** `observation_weight`, `observation_features`.
- **Constraints:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** decision pressure 3 (unit-class residuals) — resolved; not this
  gate's decision to revisit.

## Evidence Produced
See `.agent-work/629-feature-view/g4-implementer-result.md`. Commander independently re-ran
the suite (57 passed) and confirmed the grep.

## Suggested Model Tier
Simple bounded — the DB-read-boundary respect and the reserved-field guarantee are the two
things worth adversarial attention; both are narrow, well-specified checks.

## Stop Conditions
Stop and return BLOCK if: the representativeness weight is approximated rather than computed
via the real functions; the composer reads a DB directly; `unit_class_residuals` can be made
non-None; evidence is unverifiable.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.
