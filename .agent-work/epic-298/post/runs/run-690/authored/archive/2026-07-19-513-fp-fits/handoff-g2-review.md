# Reviewer Handoff — G2

## What was implemented
FP mass support: `mass_model.fp_mass(...) -> FpMass(mass_kg, sigma_kg)` distribution (NOT scalar) +
new `src/physics/layer2/fp_lap_latent.py` per-lap latent extractor (fuel est with intercept σ, compound
OBSERVED, tyre_life, emergent run_purpose). Implementer result:
`.agent-work/513-fp-fits/result-g2-implement.md`.

## How to inspect
`git diff -- src/physics/mass_model.py tests/unit/physics/test_mass_model.py` and read new files
`src/physics/layer2/fp_lap_latent.py`, `tests/unit/physics/test_fp_lap_latent.py`.

## Task statement
See `.agent-work/513-fp-fits/handoff-g2.md` (the frozen implementer handoff) — verify against it.

## Close criteria to verify
- `fp_mass` returns a DISTRIBUTION `FpMass(mass_kg, sigma_kg)`, never a scalar. σ is dominated by the
  unobservable FP starting-fuel intercept (`FP_FUEL_INTERCEPT_SIGMA_KG`). THIS IS THE LOAD-BEARING
  CONTRACT (owner explicit-unknown discipline) — a scalar return is a BLOCK.
- Invariant `base < fp_mass.mass_kg < quali_mass + MAX_FUEL_KG`; push fp_mass < long-run fp_mass.
- `run_purpose` is EMERGENT from lap pattern (lap-time-vs-session-best + stint/pit position), NEVER a
  session-type label. `classify_run_purpose` is pure + tested.
- Compound read directly from `lap_times.compound` (OBSERVED), never inferred.
- All tunable constants named at module scope + flagged as calibration placeholders (no hidden tuning).

## Constraints to verify
- physics-region: NO imports from evo_predictor/latent_power/compound_prior/fastf1.
- No `data/*.db` read in unit tests (in-memory/tmp fixtures only); `git status data/` clean.
- `quali_mass`/`race_mass` and existing behavior UNCHANGED.
- Season-DB read is read-only and follows the `physics → data` direction (session_race pattern).
- No fit output feeds fp_mass (non-circular).

## Evidence produced
`py -m pytest tests/unit/physics/test_mass_model.py tests/unit/physics/test_fp_lap_latent.py -q` →
151 passed (reproduce it). fp_mass value table in the result.

## Verification commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/test_mass_model.py tests/unit/physics/test_fp_lap_latent.py -q && git status --short data/
```

## Return format
Return REVIEW_RESULT with verdict APPROVE or BLOCK + findings (each: severity, defect, location). BLOCK
on any scalar fp_mass return, any session-label leak into run_purpose, any data/*.db read in tests, or
any physics-region import violation.
