# Reviewer Handoff — G5 (estimate_session FP wiring + explicit-unknown + #560)

## What was implemented
`estimate_session` gained `session_type="Q"`, `mass_kg`, `mass_sigma_kg`, `db_path`; a `_resolve_session_mass`
helper (injected mass → as-is; FP → `_resolve_fp_mass` via fp_mass/fp_lap_latent at the constructor's fastest
clean lap; else Q → `quali_mass(year)`). `:115` load literal → `session_type`. `estimate_batch` threads
`session_type` into estimate_fn. `_axis_statuses` gained `session_type` + reads `est.mass_sigma_kg` to force
`cda`/`p_max`/`b_b`/`b_t` UNRESOLVED (wide σ) for FP fits with a real mass σ. `EstimateRecord` gained
`mass_sigma_kg_assumed`. #560 `_support_trust_profile` reason wording corrected for FP. Result:
`.agent-work/513-fp-fits/result-g5-implement.md`.

## How to inspect
`git diff -- src/physics/layer2/session_estimator.py src/physics/layer2/estimate_store_fields.py
src/physics/layer2/estimate_store.py src/physics/layer2/estimate_batch.py` + new tests
`tests/unit/physics/layer2/test_session_estimator_fp.py`. Spec: `.agent-work/513-fp-fits/handoff-g5.md`.

## Close criteria to verify (reproduce)
- Q BYTE-IDENTICAL (HARD): default-arg Q calls unchanged. Verify `_resolve_session_mass`'s Q branch returns
  `quali_mass(year), None` (identical to the old unconditional `m = quali_mass(year)`). Reproduce the
  estimate_batch/estimate_store regression: `py -m pytest tests/unit/physics/layer2/test_estimate_batch.py
  tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_estimate_store_cumulative.py -q`
  (expect green). BLOCK on any Q-behavior change.
- σ WIDENS, NEVER SHIFTS (HARD, F2/F10): the fp_mass intercept σ inflates the mass-CONSUMING longitudinal
  axes (cda/p_max/b_b/b_t) via the EXISTING `_axis_statuses`/`effective_axis_sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC`
  machinery — confirm no mean is shifted and grip/lateral (mass-cancelling) axes are NOT widened. BLOCK if a
  parallel σ path was invented or a mean is moved.
- FP PATH REACHABLE: `estimate_session` accepts `session_type` and `estimate_batch` passes it; FP resolves
  mass via `_resolve_fp_mass` (not quali_mass). Confirm it's genuinely wired, not dead code.
- Injected `mass_kg` without σ does NOT trigger widening (caller vouches) — same as Q.
- 21 new FP tests in `tests/unit/physics/layer2/test_session_estimator_fp.py` green.
- `py -m src.utils.simplification_limits --baseline --paths <touched src>` PASS. `git status --short data/` clean.
- The live 2023 FP smoke fit is DEFERRED to G7's real compute batch (accepted disposition — the wiring is
  verified structurally + by the 21 FP unit tests here). Do NOT block on the absence of a live fit.

## Constraints to verify
- physics-region: no evo/latent_power/compound_prior/fastf1 imports.
- No data/*.db write; grip math unchanged; #627 machinery reused (not duplicated); no new hard #560 floor.

## Verification commands
```bash
cd /c/Programs/f1-513 && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_session_estimator_fp.py -q && PYTHONPATH=/c/Programs/f1-513 py -m pytest tests/unit/physics/layer2/test_estimate_batch.py tests/unit/physics/layer2/test_estimate_store.py -q && git status --short data/
```

## Return format
REVIEW_RESULT: verdict APPROVE or BLOCK + findings (severity, defect, location). BLOCK on: any Q-behavior
change, any fp_mass σ that shifts a mean rather than widening, a parallel σ path instead of the #627 machinery,
FP path being dead/unreachable, a new hard #560 floor, or any region-import violation. Write to
`.agent-work/513-fp-fits/result-g5-review.md` AND SendMessage to "ShipI-513".
