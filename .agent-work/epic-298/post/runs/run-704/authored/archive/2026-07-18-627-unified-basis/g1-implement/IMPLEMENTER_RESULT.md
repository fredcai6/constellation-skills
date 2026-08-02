# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1 (systematic-budget module — Tier-1 #2 / #506 analytic engine)`

## Completed slice
Built `src/physics/layer2/systematic_budget.py`: a per-session nuisance-uncertainty
propagator. `systematic_budget(params, *, mass_kg, rho, theta_R, cda_pin_sigma)` returns, for
each of `cda, p_max, a_b, b_b, a_t, b_t, A0, A2`, a `(shared_rel, session_varying_rel)` tuple
computed from ANALYTIC sensitivities (no re-fitting), whose quadrature TOTAL matches the
documented `scripts/nuisance_sensitivity.py` reference (4.3% CdA / 3.7% P_max) exactly at the
real Monza (Italy) RBR 2023 Q inputs.

## Scope
**Files changed:**
- `src/physics/layer2/systematic_budget.py` (new)
- `tests/unit/physics/layer2/test_systematic_budget.py` (new, 18 synthetic-param tests)
- `tests/unit/physics/layer2/test_systematic_budget_monza_validation.py` (new, 1 fast
  no-telemetry validation test + a manual-only `__main__` live-perturbation harness)

**Specific exclusions touched:** no. `estimate_store.py`, `pooling.py`, `pool_driver.py`, and
all views were read-only references, never edited. No production default, `circuits.yaml`, or
gold bundle changed. No writes to `data/*.db` (verified via `git status --porcelain`: only the
three new files + `.agent-work/` are untracked, no modification to any `data/` path).

## Behavior changed
Yes (additive only): a new, previously-nonexistent module + its tests. Nothing existing was
modified, so no existing behavior changed. `estimate_store.SYSTEMATIC_FLOOR` still governs
production floors until G4 wires this engine in (out of scope for g1 by design).

## Map Impact

- **Structural anchors touched:** `struct:physics.layer2` — new
  `src/physics/layer2/systematic_budget.py` (public `systematic_budget()` + internal
  `_cda_pmax_budget`, `_braking_traction_budget`, `_split_variance` helpers); read-only
  reference to `scripts/nuisance_sensitivity.py`, `src/physics/layer2/estimate_store.py`
  (`SYSTEMATIC_FLOOR`), `src/physics/mass_model.py::quali_mass`,
  `src/physics/longitudinal_fit.py::MASS_KG`, and the four view modules
  (`power_drag_view.py`, `braking_view.py` incl. `cda_frontier_jacobian`, `traction_view.py`,
  `lateral_view.py`) whose design-matrix structure the analytic sensitivities are derived from.
- **Capabilities added/changed/affected:** new capability — per-session five-view estimate
  systematic budget (shared vs session-varying split), standalone (not yet wired into the
  store; that is G4).
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — honored,
  verified by grep (only stdlib `typing` imported). New assumption introduced: `MASS_SENS_CDA`
  and `MASS_SENS_PMAX` are treated as EXACTLY 1.0 (an analytic design-matrix argument, not a
  fit output) — this is a genuinely provable claim (see docstring), not a placeholder.
- **Decision candidates / resolved decisions:** (1) `MASS_SHARED_VARIANCE_FRACTION = 0.8` —
  the mass nuisance's shared-vs-session split is a documented judgment call (the handoff says
  "mostly shared", this module picks 0.8 of the VARIANCE, not the magnitude — see
  `_split_variance`'s docstring for why variance-fraction, not linear-fraction, is the correct
  quadrature-preserving split). Flagged for Commander/architecture confirmation. (2) A0/A2's
  curvature+terrain bound (`A0_CURVATURE_TERRAIN_BOUND_REL` / `A2_CURVATURE_TERRAIN_BOUND_REL`
  = 0.04 each) is carried forward from the existing informed reference, explicitly NOT derived
  from this module's four nuisances (which are proven to contribute exactly zero to A0/A2) —
  a placeholder pending #497/#506's real curvature/terrain measurement, not a computed number.
  (3) `THETA_SENS_CDA_REL`, `RHO_SENS_PMAX_REL`, `THETA_SENS_PMAX_REL` are DERIVED algebraically
  from the pre-existing documented reference (see Assumptions below) rather than freshly
  measured this session — a live remeasurement is recommended once environment access is
  confirmed unblocked (see the `run_live_monza_perturbation_validation` harness).
- **Claims/evidence produced:** `systematic_budget()`'s analytic total for CdA and P_max
  reproduces the documented `estimate_store.SYSTEMATIC_FLOOR` reference (4.3% / 3.7%) EXACTLY
  at the real measured Monza (Italy) RBR 2023 Q inputs (`mass_kg=quali_mass(2023)=808.0`,
  `rho=1.1480283106796993`, both obtained from a real DB-backed session load, not fabricated).
- **Trust limitations / drift found:** the live perturbation re-run (the actual purpose of the
  Monza validation) could not complete in this environment — see Stop Conditions / Assumptions.
  `THETA_SENS_CDA_REL`/`RHO_SENS_PMAX_REL`/`THETA_SENS_PMAX_REL` should be treated as
  provisional (derived, not independently measured) until that live run succeeds.
- **Triage candidates:** (a) re-run `run_live_monza_perturbation_validation` once environment
  contention is not a factor, to independently verify the three derived constants and split the
  P_max remaining budget by real rho/theta_R arms instead of an even split; (b) G4 should decide
  whether `cda_pin_sigma` is sourced from this module's own CdA output (self-consistent
  chaining) or from `PowerDragResult.cda_prior_closed.sigma` directly (they should be similar
  but are not identical channels) when wiring this into the store.

## Test mode
**Required:** `test-after (numeric module; validate against the existing perturbation probe)`
**Satisfied:** yes — 18 synthetic-param unit tests + 1 fast real-input validation test, all
green; TDD red/green not applicable per the handoff's explicit test-mode allowance.

## Evidence

```bash
cd /c/Programs/f1-627
py -m pytest tests/unit/physics/layer2/test_systematic_budget.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-627
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 18 items

tests\unit\physics\layer2\test_systematic_budget.py ..................   [100%]

============================= 18 passed in 1.33s ==============================
```

```bash
py -m pytest tests/unit/physics/layer2/ -q -k systematic
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-627
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 704 items / 684 deselected / 20 selected

tests\unit\physics\layer2\test_estimate_store.py .                       [  5%]
tests\unit\physics\layer2\test_systematic_budget.py ..................   [ 95%]
tests\unit\physics\layer2\test_systematic_budget_monza_validation.py .   [100%]

===================== 20 passed, 684 deselected in 2.84s ======================
```

**Result:** pass.

### Analytic-vs-perturbation agreement number on Monza

**Not a live re-run this session** (see Stop Conditions). Partial live evidence obtained:
`load_quali_session(2023, "Italy", "Q", store="C:/Programs/f1Brainz/data/telemetry_store.db")`
succeeded in ~7s, returning the REAL measured air density `rho=1.1480283106796993` (no
fallback) for Monza (Italy) RBR 2023 Q. Feeding that real `rho` and the real
`quali_mass(2023)=808.0` into `systematic_budget()`'s analytic CdA/P_max computation:

```
CdA total   = 4.3000%  (documented reference: ~4.3%, estimate_store.SYSTEMATIC_FLOOR comment)
P_max total = 3.7000%  (documented reference: ~3.7%, estimate_store.SYSTEMATIC_FLOOR comment)
```

This is an EXACT match because `THETA_SENS_CDA_REL`/`RHO_SENS_PMAX_REL`/`THETA_SENS_PMAX_REL`
were algebraically DERIVED from that same documented reference (see Assumptions) — it confirms
internal consistency (the module reproduces the reference it was calibrated against, using real
session inputs for the parts that ARE exact/analytic: mass, rho-for-CdA), but it is NOT
independent confirmation of the derived theta_R/rho-P_max split. The braking/traction axes
(a_b, b_b, a_t, b_t) are fully closed-form (theta_R exact 1:1 on intercepts,
`cda_frontier_jacobian`'s documented Jacobian on slopes) and did not depend on the stalled live
run at all — they are validated purely by their own closed-form unit tests
(`test_braking_traction_intercept_is_fully_shared_theta_r_driven`,
`test_braking_traction_slope_inherits_cda_split_fraction`,
`test_braking_traction_systematic_below_typical_fit_sigma`).

## TDD evidence, if required
- Failing test observed: n/a — test-after mode per handoff (numeric module, validate against
  an existing perturbation probe rather than red/green on behavior).
- Passing test observed: see Evidence above.
- Refactor while green: n/a (single-pass build; simplification-limits check passed clean, see
  Assumptions).

## Docs/contracts touched
- none — no committed report schema, doc, or config was touched (module docstring IS the
  contract documentation, per project convention for `src/physics/layer2/*.py`).

## Assumptions

1. **`cda_pin_sigma` is an ABSOLUTE sigma (m²)**, matching `ParamPrior.sigma` /
   `PowerDragResult.cda_prior_closed.sigma` in the production views — not a relative fraction.
   The handoff's signature names it `cda_pin_sigma` (not `cda_pin_sigma_rel`), and this
   interpretation lets `_braking_traction_budget`'s Jacobian formula
   (`j_coupling = rho/(2*mass_kg)`, units 1/m³, times CdA in m² → 1/m, matching `b_b`/`b_t`
   units) work directly without an extra unit conversion. G4 (wiring) should confirm this
   matches whatever it plans to pass in.
2. **`params` dict holds this session's FITTED axis values** (`cda`, `p_max`, `a_b`, `b_b`,
   `a_t`, `b_t`, required; `A0`/`A2` accepted but unused in the computation, since their
   systematic doesn't depend on their own value — only on the curvature/terrain placeholder).
3. **`THETA_SENS_CDA_REL = 0.031801`, `RHO_SENS_PMAX_REL = THETA_SENS_PMAX_REL = 0.019446`**
   are DERIVED (not independently measured this session) from
   `sqrt(4.3² − mass_rel(808)² − 1.5²)` for CdA-theta, and an EVEN split of
   `sqrt(3.7² − mass_rel(808)²)` between P_max's rho and theta_R channels (underdetermined
   from one reference number — see module docstring for the full derivation and its
   limitation). Flagged as a decision/triage candidate for a live remeasurement.
4. **Braking/traction intercept (a_b, a_t) CdA-pin sensitivity is treated as exactly 0**,
   the HEALTHY-interior-fit case documented in `cda_frontier_jacobian`'s own docstring
   (`J[0] ≈ 0` on a healthy fit; the bound-active degenerate case where CdA sensitivity
   relocates to the intercept is NOT modelled — out of scope, flagged below).
5. **`MASS_SHARED_VARIANCE_FRACTION = 0.8`** is a judgment call, not a measurement (see Map
   Impact decision candidates).

## Stop conditions hit

**Partial stop on the live Monza perturbation re-run** (m1/m4): two independent bounded
attempts to reproduce `scripts/nuisance_sensitivity.py`'s live perturbation budget against real
telemetry (`C:/Programs/f1Brainz/data/telemetry_store.db`, read-only, absolute main-checkout
path) stalled with near-zero CPU utilization (~0.15–0.19s accumulated CPU across ~10min and
~4min wall-clock windows respectively, confirmed via `Get-Process` sampling) inside
`prepare_braking_frontier`'s per-driver smoother-HP calibration
(`calibrate_session_hp`/`fit_stint_hp`), AFTER a successful ~7s DB-backed session load
(rho=1.148028, correct). This is not a defect in the analytic approach or in the DB-store
access path (both worked); the most plausible cause is I/O/lock contention from the 6+ other
Ship agents concurrently active in this session on the shared main-checkout files. Per the
handoff's own explicit sanction ("If telemetry is genuinely unreachable, attest that instead
and document the fallback... unit-test the analytic closed form only"), I invoked the
documented fallback: derived the three non-closed-form constants from the pre-existing
`SYSTEMATIC_FLOOR` reference already in the codebase, unit-tested the closed-form pieces
exhaustively (18 tests), and built a manual-only `__main__` harness
(`run_live_monza_perturbation_validation`, deliberately NOT pytest-collected, to avoid risking
a hang in the required-evidence commands — `pyproject.toml` does not deselect `slow` tests by
default) for a future live rerun. This is reported as a stop condition per doctrine, not
silently worked around.

No other stop conditions hit — allowed scope was not exceeded, no production default changed,
and the split-allocation decision was made and documented (not escalated) per the handoff's
explicit authority grant ("You decide the analytic sensitivity derivations and the split
allocation").

## Out-of-scope observations

- `estimate_store.SYSTEMATIC_FLOOR`'s `A0: 0.04` comment says "mass/rho cancel in
  de-conflation; interim pending curvature/terrain" — this g1 module confirms and formalizes
  that exact finding (A0/A2 carry zero of the four modelled nuisances) but does not replace the
  floor (G4's job). Worth flagging to G4: the floor's own comment already anticipated this
  gate's finding.
- The bound-active degenerate case in `cda_frontier_jacobian` (CdA sensitivity relocating to
  the intercept when the `b >= 0` bound is active) is real production behavior this module does
  not model (assumption 4 above) — if G4 finds braking/traction intercepts systematically
  under-budgeted on sessions with degenerate slope fits, this is the likely cause; a follow-up
  triage candidate.
- Environment note for future agents: prefer `load_quali_session(..., store=<absolute main-
  checkout telemetry_store.db path>)` over the bare `cache=` parameter when working from a
  worktree — the `cache=` parameter only feeds the FastF1-cache FALLBACK branch (used only
  when the DB store is absent), and passing an absolute path there does NOT redirect the
  primary DB-store lookup (which stays at the cwd-relative default unless `store=` is passed
  explicitly). This cost significant time to diagnose and is worth a note in the crew context
  or a keyword-arg-forwarding fix in `prepare_braking_frontier`/`prepare_throttle_frontier`
  (currently neither forwards a `store=` override to `load_quali_session`).

## Workflow Feedback

- **Handoff gaps:** the handoff's Verification Commands section didn't warn that
  `prepare_braking_frontier`/`prepare_throttle_frontier` (the natural entry points suggested by
  `scripts/nuisance_sensitivity.py`, which the handoff explicitly cites as read-only reference)
  don't expose a `store=` passthrough to reach the DB-backed telemetry store from a worktree —
  only `cache=` (FastF1-cache-fallback-only). This cost real time (~25 min across two
  diagnostic cycles) to discover via source reading. A one-line note in the handoff or
  CREW_CONTEXT ("use `load_quali_session(..., store=<abs path>)` + pass the pre-loaded
  `session=`/`rho=` into `prepare_*`, not `cache=`") would have saved it.
- **Context rediscovered:** the exact PowerDragView design-matrix scaling argument (why
  mass/rho give clean 1:1/-1:1 CdA sensitivities) had to be derived by reading
  `power_drag_view.py`'s `design()` closure directly — not documented anywhere as a citable
  fact before this gate. Same for `cda_frontier_jacobian`'s healthy-fit vs bound-active
  distinction in `braking_view.py` — a genuinely well-documented docstring, but only
  discoverable by reading the file, not from the handoff's Map Anchors.
- **Instructions improvised around:** the handoff's Close Criteria didn't specify units/shape
  for `cda_pin_sigma` (relative fraction vs absolute sigma) — I inferred ABSOLUTE (matching
  `ParamPrior.sigma`) from the production call sites and documented the inference explicitly
  (see Assumptions #1) rather than guessing silently.
- **What would have made this easier:** the handoff's "Verification Commands" section could
  have included a known-good `store=`-based telemetry smoke-test one-liner (mirroring what I
  eventually built in `diag_load2.py`) — this is exactly the kind of thing a Commander running
  this gate a second time would want pre-baked, given how easy it is to hit the `cache=` trap.

## Return status
`complete`
