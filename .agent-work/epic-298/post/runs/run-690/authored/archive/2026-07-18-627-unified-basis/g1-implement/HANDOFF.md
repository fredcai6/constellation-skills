# Implementer Handoff

## Gate
g1 (systematic-budget module — Tier-1 #2 / #506 analytic engine)

## Task
Build `src/physics/layer2/systematic_budget.py`: a per-session nuisance-uncertainty propagator. Given a
session's fitted params + nuisances, return each param's SYSTEMATIC relative sigma SPLIT into a `shared_rel`
and a `session_varying_rel` component. This is the reusable engine G4 will wire into the store + pooling; this
gate builds and validates it standalone (no store/pooling changes here).

## Protected Intent
Honest, data-driven systematic uncertainty that replaces the static `SYSTEMATIC_FLOOR` table. The SHARED
component is the common-mode error pooling cannot average away (the #506 core) — it must be computed, not
guessed. Honest-wide over optimistic-tight.

## Test Mode
test-after allowed (numeric module; validate against the existing perturbation probe).

## Close Criteria
- New module `src/physics/layer2/systematic_budget.py` with a documented public function, e.g.
  `systematic_budget(params: dict, *, mass_kg, rho, theta_R, cda_pin_sigma) -> dict[str, tuple[shared_rel, session_varying_rel]]`
  covering axes: CdA, P_max, a_b, b_b, a_t, b_t, A0, A2.
- Uses ANALYTIC sensitivities (no re-running fits): CdA and P_max scale ~1:1 with mass (d ln X / d ln m ≈ 1);
  CdA·rho is the constrained product so d ln CdA / d ln rho ≈ −1 (P_max similarly rho-sensitive); braking a_b/b_b
  and traction a_t/b_t carry the pinned-CdA sensitivity (their fit-sigma already dominates their systematic —
  document that); lateral A0 AND A2: mass/rho CANCEL (mu = |a_lat|/(g cos theta)), so their systematic is
  curvature/terrain-bounded — do NOT reuse the blind 4%; give a documented bound (name A2 explicitly).
- SPLIT rule, documented: SHARED = nuisances identical across a year's sessions — the `quali_mass(year)` model
  bias (mass is one value/year, a common-mode bias) and the `theta_R = 0.15` literal used in every de-conflation.
  SESSION-VARYING = per-session rho measurement error + genuine per-session fuel-load variation about the model.
  Allocate the mass systematic mostly to SHARED (the model bias dominates and is what pooling cannot remove);
  document the allocation explicitly. This split boundary is a load-bearing choice — state your rationale in a
  module docstring (the Commander records it as a decision candidate).
- VALIDATION: the TOTAL systematic (shared ⊕ session-varying in quadrature) reproduces
  `scripts/nuisance_sensitivity.py`'s perturbation budget on Monza (Italy) RBR 2023 Q within a documented
  tolerance: ~4.3% CdA, ~3.7% P_max, and braking/traction fit-sigma-dominated (their systematic < their fit-sigma).
  Monza(Italy) RBR 2023 Q is the CANONICAL session pinned across G1/G3/G4 — use it.
- Unit tests in `tests/unit/physics/layer2/test_systematic_budget.py` (SYNTHETIC params, NO FastF1): the split
  returns two finite non-negative components per axis; CdA/P_max shared component is the dominant (mass-driven)
  one; A0/A2 do NOT carry the mass/rho systematic (they cancel); the analytic CdA/P_max mass-sensitivity is ~1:1.
  Add ONE validation test (or a `if __name__=='__main__'` harness) that reproduces the Monza numbers when the
  telemetry DB is present — guard it to SKIP cleanly when the DB/telemetry is absent so the unit suite stays
  FastF1-free and green.

## Allowed Scope
- CREATE `src/physics/layer2/systematic_budget.py`.
- CREATE `tests/unit/physics/layer2/test_systematic_budget.py`.
- READ-ONLY reference: `scripts/nuisance_sensitivity.py` (the perturbation method + the ±20kg mass / ±1.5% rho /
  theta_R 0.05–0.25 / ±4% CdA-pin uncertainty magnitudes), `src/physics/layer2/estimate_store.py`
  (`SYSTEMATIC_FLOOR` — what you replace), `src/physics/mass_model.py::quali_mass`, `src/physics/longitudinal_fit.py::MASS_KG`.

## Specific Exclusions
- Do NOT modify `estimate_store.py`, `pooling.py`, `pool_driver.py`, or any view — that wiring is G4.
- Do NOT change any production default, `circuits.yaml`, or gold bundle.
- Do NOT write to `data/*.db`. If you run the Monza validation and it touches telemetry, do NOT commit any DB;
  `git checkout -- data/` after.

## Constraints
- `constraint:physics_region_no_evo_import` — no evo imports.
- ASCII-safe source; `py` launcher; `PYTHONIOENCODING=utf-8` on captured subprocesses.
- The nuisance magnitudes are the REAL uncertainties: mass ±20kg (≈±2.5%), rho ±1.5%, theta_R prior 0.05–0.25,
  pinned-CdA ±4% — match `scripts/nuisance_sensitivity.py`.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — new `src/physics/layer2/systematic_budget.py`; ref `scripts/nuisance_sensitivity.py`.
- Capability: per-session five-view estimate systematic budget.
- Constraints: `constraint:physics_region_no_evo_import`.
- Decision anchors: the shared-vs-session-varying split boundary is a load-bearing choice — document your rationale.
- Evidence expectations: total systematic matches nuisance_sensitivity ~4.3% CdA / ~3.7% P_max on Monza RBR 2023 Q.

## Deliverable Path Check
- Committed — `src/physics/layer2/systematic_budget.py`; `git check-ignore` exits 1 (not ignored). Verified.
- Committed — `tests/unit/physics/layer2/test_systematic_budget.py`; not ignored.
- Both are NEW files: `git diff` will not show them until staged; they appear in `git status`.

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_systematic_budget.py -q` — full pass; paste the tail.
- The analytic-vs-perturbation agreement number on Monza (paste, or paste the SKIP line if telemetry absent —
  in which case state that the analytic sensitivities are unit-tested against their closed form instead).

## Verification Commands
```bash
cd /c/Programs/f1-627
py -m pytest tests/unit/physics/layer2/test_systematic_budget.py -q
py -m pytest tests/unit/physics/layer2/ -q -k systematic
```

## Suggested Model Tier
stronger — numeric/physics reasoning about sensitivities and the shared/session-varying split.

## Authority
The tier/scope is frozen by the Admiral launch order (cited by the Commander). You decide the analytic
sensitivity derivations and the split allocation (document them). You must NOT change any file outside Allowed
Scope, nor alter production defaults.

## Worktree Isolation (CRITICAL)
Your cwd MUST be `C:/Programs/f1-627` for every command. Before any run, assert a src.physics module resolves to
this worktree: `py -c "import src.physics.layer2.estimate_store as m; print(m.__file__)"` must print a path under
`C:\Programs\f1-627`. The editable-install `.pth` resolves `src.*` to THIS worktree only when cwd is inside it.
If the Monza validation needs telemetry, the DB is at `C:/Programs/f1Brainz/data/telemetry_store.db` /
`C:/Programs/f1Brainz/data/telemetry` — absolute paths into the MAIN checkout (your worktree lacks the untracked data).

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a production default must change, the perturbation validation
cannot be reproduced AND the analytic form cannot be unit-tested, or a decision beyond the split-allocation is needed.

## Return Format
Write `IMPLEMENTER_RESULT` to `.agent-work/627-unified-basis/g1-implement/IMPLEMENTER_RESULT.md` AND summarize in
your final message (deliver via SendMessage to ShipF-627 before ending your turn): completed slice, files changed,
test mode satisfied, evidence (pasted test tail + validation number), the split-allocation rationale, assumptions,
stop conditions hit, out-of-scope observations, workflow feedback.
