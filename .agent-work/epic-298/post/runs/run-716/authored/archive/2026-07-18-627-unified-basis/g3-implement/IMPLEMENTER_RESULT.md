# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3 (cross-view covariance population + redundancy demonstration -- Tier-1 #1, NON-DEFERRABLE)`

## Completed slice
All four close criteria landed: (1) `cda_jacobian` exposed on `BrakingViewResult`/`TractionViewResult`;
(2) `record_from_estimate` persists `cov(CdA,[a_b,b_b])`/`cov(CdA,[a_t,b_t])` in `cross_view_covariance`;
(3) honest cov-aware dual-CdA fusion (`src/physics/layer2/cross_view.py`) wired into the store with a
falsifiable agreement `z` and an explicit refusal reason when illegitimate; (4) a non-tautological
redundancy demonstration on the canonical Monza (Italy) RBR 2023 Q session, using REAL live + REAL stored
data throughout, with the propagation traced through the persisted cross-terms.

## Scope
**Files changed:**
- `src/physics/layer2/braking_view.py` (add + populate `cda_jacobian` on `BrakingViewResult`)
- `src/physics/layer2/traction_view.py` (add + populate `cda_jacobian` on `TractionViewResult`)
- `src/physics/layer2/cross_view.py` (new -- `fuse_dual_cda`, `propagate_shared_param_variance`,
  `cda_jacobian_covariance`)
- `src/physics/layer2/estimate_store.py` (`_cda_jacobian_cross_terms`, `_fused_cda_inputs`,
  `_fused_cda_fields`, `_cross_view_covariance_fields`; wired into `record_from_estimate`; extended
  `_CROSS_VIEW_COVARIANCE_KEYS` + the shape-documenting comment)
- `tests/unit/physics/layer2/test_braking_view.py`, `test_traction_view.py` (new `cda_jacobian` tests)
- `tests/unit/physics/layer2/test_cross_view.py` (new file, 9 tests)
- `tests/unit/physics/layer2/test_estimate_store.py` (extended `_fake_estimate` fixture; updated 2 stale
  G2 tests; 5 new tests)

**Local-only (NOT in the diff, not committed):**
- `.agent-work/627-unified-basis/g3-implement/monza_redundancy_demo.py` -- live session load + independent
  Coast fit + bounded braking/traction re-fit attempt (Red Bull Racing)
- `.agent-work/627-unified-basis/g3-implement/monza_multiteam_coast_probe.py` -- live independent Coast
  fits for 4 more constructors on the same session (used to find a real pair where fusion legitimately
  succeeds, since Red Bull Racing's own pair genuinely disagrees -- see below)
- `.agent-work/627-unified-basis/g3-implement/monza_finalize.py` -- final before/after table assembly from
  the already-collected real numbers (pure arithmetic, no further live/DB access)
- `monza_demo_log.txt`, `monza_multiteam_log.txt`, `monza_demo_result.json`, `monza_multiteam_result.json`,
  `monza_final_table.json` -- captured run output/evidence

**Specific exclusions touched:** no. `est.cda_closed` / `drag_area_closed_m2` (the production pinning
CdA) is untouched -- `fused_cda` is a strictly additional persisted quantity, never fed back into the
pinning flow. No `{axis}_status` resolved (all stay `"unresolved"`, G4's job). `SYSTEMATIC_FLOOR` untouched.
No `circuits.yaml`/gold/default changed. `git status --porcelain -- data/` is empty throughout (verified
after every DB-touching run).

## Behavior changed
Yes, additively. `record_from_estimate()` now populates `cross_view_covariance` with real values (or an
explicit non-None reason) instead of leaving it a bare `None` in the fitted-session case (the `None` case
now only occurs for `error_record()`, where no view was ever fit). Nothing about the production pin, gold,
or any existing consumer's read path changed.

## Fusion + propagation design

### 1. `cda_jacobian` exposed (braking_view.py / traction_view.py)
`BrakingView.fit`/`TractionView.fit` already compute `J = cda_frontier_jacobian(...)` to build the
returned `.covariance` (`outer(J,J) * cda_sigma**2` added to the frontier's own fit covariance); it was
discarded after use. Both `*ViewResult` dataclasses gained `cda_jacobian: np.ndarray | None = None`
(defaulted, frozen-dataclass-safe), and both `fit()` methods now pass `cda_jacobian=J` into the
constructor. New tests (`test_fit_exposes_cda_jacobian` in both view test files) assert the exposed field
is the SAME `J` that produced the covariance's CdA-driven inflation (recomputed independently via a
`sigma->1e-9` differencing check, not just re-asserted algebraically).

### 2. Persistence (`estimate_store.py`)
`_cda_jacobian_cross_terms(braking, traction, cda_sigma)` computes
`cov(CdA,[a_b,b_b]) = cda_sigma**2 * braking.cda_jacobian` and the traction analogue, via the new
`cda_jacobian_covariance()` helper. Null-safe: any missing view/Jacobian/sigma leaves the corresponding
keys `None`, never a fabricated number. Round-trips through the store's existing `cross_view_covariance`
JSON column (G2's schema, unchanged).

### 3. Honest cov-aware fusion (`cross_view.py::fuse_dual_cda`)
PowerDrag's CdA and an INDEPENDENTLY-fit Coast CdA (`cda_prior=None`) share the same within-session
mass/rho nuisance -> correlated. `fuse_dual_cda` builds `Sigma = [[sigma_pd**2, cov],[cov, sigma_co**2]]`
with `cov = shared_rel**2 * cda_pd * cda_co` (`shared_rel` from G1's `systematic_budget(...)["cda"]`), then
fuses by GLS (`sigma_fused**2 = 1/(u^T Sigma^-1 u)`). Reports the falsifiable agreement
`z = |cda_pd-cda_co| / sqrt(sigma_pd**2+sigma_co**2-2*cov)`; `z >= 5` (or a non-PSD `Sigma`) REFUSES the
fuse (`mu=sigma=None`, an explicit `reason` string) rather than silently blending a contradiction.

**A correctness fix found by testing on real data, not just synthetic tests:** feeding `fuse_dual_cda` the
bare FIT-only covariance (`sqrt(est.power_drag.covariance[1,1])`, the handoff's literal wording) made
`Sigma` non-PSD (invalid) on ALL FIVE real Monza-2023-Q constructor pairs I tested (PowerDrag-closed vs
independently-fit Coast) -- the SHARED relative systematic alone (~3.9%, G1) already exceeds the raw fit
sigma (~1.4-4%), so `cov` structurally exceeds what a covariance matrix built from those input sigmas can
represent. `_fused_cda_fields` now inflates each view's sigma to its HONEST TOTAL (fit ⊕ full systematic,
`shared_rel`+`session_rel` from the SAME `systematic_budget` call, scaled to that view's own CdA value)
before calling `fuse_dual_cda`; `cov` itself is unaffected (still shared-only). This is documented in
`_fused_cda_fields`'s docstring as a deliberate refinement over the handoff's literal wording, backed by
the 5-pair empirical check (2 of 5 then fuse legitimately; the other 3 still correctly refuse on a genuine,
now well-posed z >= 5 rather than a degenerate non-PSD artifact). I judged this within my granted authority
("You decide ... the exact `cross_view_covariance` value population") but flag it as a decision Commander
may want to confirm.

Production's `estimate_session()` always PINS Coast's CdA (`session_estimator._run_coast` passes
`cda_prior=cda`), so `coast.cda_pinned` is `True` and `coast.covariance[1,1]==0` in every stored row today
-- `_fused_cda_inputs` detects this (`coast.cda_pinned is False` required) and returns
`"coast_cda_pinned_not_independent"` rather than fusing a value against itself. `fused_cda` therefore stays
unpopulated on today's production pathway BY DESIGN; it activates only when a caller supplies a genuinely
independent Coast fit (as the demonstration does).

### 4. Propagation (`cross_view.py::propagate_shared_param_variance`)
`Var(b) = V0 + J**2 * sigma_CdA**2` where `V0` is the CdA-INDEPENDENT fit variance. Given the TOTAL
`Var(b)` at the OLD `sigma_CdA` and the PERSISTED `cov(CdA,b) = sigma_CdA**2 * J`, both `V0` and `J` are
recoverable WITHOUT a re-fit: `V0 = total_var_pin - cov**2/sigma_CdA_pin**2`. Substituting a NEW
`sigma_CdA` gives the new total variance. If `cov==0` (no persisted coupling, e.g. a bound-active slope)
the shared parameter's sigma cannot propagate at all -- variance is UNCHANGED, the honest null a
non-tautological demonstration must be able to produce (unit-tested explicitly:
`test_propagate_shared_param_variance_no_coupling_is_a_null`).

## Before/after redundancy table (real numbers) -- Monza (Italy) RBR 2023 Q, 2026-07-18

**Run paths used, stated per number (never fabricated):**
- Session load, live, `store=C:/Programs/f1Brainz/data/telemetry_store.db`: succeeded in ~7-10s each time,
  `rho=1.1480283106796993` (matches the stored row exactly -- same real weather).
- Independent Coast CdA fits (`run_coast_view_on_session(..., cda_prior=None)`): LIVE, ~11-14s each,
  genuinely fresh this session (raw car-data path, `prepare_coast_samples`; confirmed this does NOT hit
  the expensive per-driver smoother-HP calibration).
- PowerDrag CdA, b_b/b_t baseline covariances: the REAL STORED `session_estimates` row
  (`C:/Programs/f1Brainz/data/physics_estimates.db`, `fitted_at=2026-07-06T22:31:47`, a genuine historical
  fit on this exact session) -- a live re-fit was NOT needed for these (only PowerDrag's ALREADY-STORED
  numbers were used; PowerDrag/Traction/Braking's underlying data-prep ALL route through the same
  `_driver_samples`/`calibrate_session_hp` call, contrary to my initial assumption that PowerDrag/Traction
  were "cheap" -- confirmed by reading `session_traction.py::prepare_throttle_frontier`, which imports and
  calls `session_braking._driver_samples`).
- `cda_jacobian` (J) for the propagation: a bounded (300s) LIVE re-fit of `BrakingView`/`TractionView` was
  attempted (background-monitored) and **STALLED** (near-zero progress for the full 300s, consistent with
  G1's documented finding of contention under concurrently-active Ship agents in this session) -- the
  abandoned attempt is logged (`monza_demo_log.txt`). Per the handoff's explicit sanction, fell back to the
  documented ANALYTIC closed-form `J ~= drag_sign * (-rho/(2*mass))` -- the SAME form
  `systematic_budget.py::_braking_traction_budget` already uses (that module is G1, already merged,
  reviewed, and validated against a live perturbation reference on this same session).

**Real, non-fabricated finding: Red Bull Racing's own pair does not legitimately fuse.** The live
independent Coast CdA (0.805 m²) disagrees substantially with PowerDrag's CdA (1.130 m², a 29% relative
gap) -- `fuse_dual_cda` correctly REFUSES (agreement `z = 6.80 >= 5`) rather than blending a contradiction.
Contrast: a NAIVE fuse (ignoring the shared correlation entirely, raw fit sigmas) would have produced
`mu=1.072, sigma=0.0146` -- LOOKING confidently tighter than PowerDrag alone (sigma 0.0161) while its own
naive-uncorrelated z (8.52) already flags the same disagreement it silently papers over. This is real
evidence the honest-fusion design is doing genuine work, not a synthetic strawman.

Since the handoff pins Red Bull Racing as canonical, I probed the SAME session's other 4 constructors
(same track/weather/mass, same methodology, all real live independent-Coast fits) to find a pair where
fusion legitimately succeeds and complete the tightening chain end-to-end on real data. Mercedes (HAM/RUS)
does (`z = 2.03`). Both tables below are real; RBR shows the honest-refusal outcome the handoff's own
"forbidden naive fuse" concern anticipates, Mercedes shows the positive tightening-propagates outcome on
the identical session.

### Table A -- CdA fusion (both real, live + stored)

| | Red Bull Racing (canonical) | Mercedes (same session) |
|---|---:|---:|
| PowerDrag CdA (stored, real fit) | 1.1302 m² | 1.0869 m² |
| PowerDrag sigma, fit-only | 0.01612 m² | 0.03113 m² |
| PowerDrag sigma, HONEST (fit ⊕ full systematic) | 0.05120 m² | 0.05615 m² |
| Coast CdA, LIVE independent fit | 0.8048 m² | 0.9898 m² |
| Coast sigma, HONEST | 0.04896 m² | 0.04854 m² |
| Agreement z (honest, PSD-valid) | **6.80** | **2.03** |
| Fusion outcome | **REFUSED** (`disagreement_z_ge_5`) | **LEGITIMATE** (`ok`) |
| Fused CdA (mu, sigma) | n/a | 1.021 m², **0.04599 m²** |
| Fused sigma vs single-view-honest | n/a | 0.0460 < 0.0562 (**-18.1%**) |

### Table B -- propagation into b_b / b_t (Mercedes, the legitimate case; RBR stays at its stored baseline
since fusion was correctly refused there)

`cov(CdA,b)` is defined at the RAW pin sigma (0.03113 m², matching what production's
`cda_prior_closed.sigma` actually pins braking/traction with today); `V0` (the CdA-independent fit
variance) is recovered from that + the REAL stored `total_var_pin`, per `propagate_shared_param_variance`.
"honest single-view" re-propagates the SAME `V0`/`J` at PowerDrag's own HONEST sigma (0.05615 m²) --
the fair baseline for "is redundancy actually helping," since comparing the fused sigma against the
artificially-tight raw fit-only pin would be comparing honest against dishonest, not single-view against
multi-view.

| | b_b (brake_aero_decel_per_m) | b_t (traction_aero_accel_per_m) |
|---|---:|---:|
| sigma, TODAY's production (raw-pin-based, stored) | 0.0010456 | 0.0011051 |
| sigma, honest single-view CdA (0.05615 m²) | 0.0010461 | 0.0011056 |
| sigma, honest FUSED CdA (0.04599 m²) | **0.0010459** | **0.0011053** |
| Variance reduction, fused vs honest-single | **-0.048%** | **-0.043%** |

`propagate_shared_param_variance` was cross-checked against the direct formula
(`V0 + J**2*sigma_new**2`) inline in the finalize script -- both agree to floating-point precision,
confirming the persisted-term-only propagation path is exact, not an independent approximation.

**Honest characterization of the effect size:** the tightening is real, correctly signed, and traced
through the persisted `cov(CdA,b)` term (not a tautological "inverse-variance always helps" restatement --
`test_propagate_shared_param_variance_no_coupling_is_a_null` proves the SAME machinery produces ZERO
change when `cov==0`), but it is SMALL (~0.04-0.05% of b_b/b_t's own variance) because the CdA-pin
Jacobian's contribution is a small fraction of b_b/b_t's total budget -- their own frontier-FIT variance
dominates. This is NOT a surprise or a red flag: it is exactly what G1's `systematic_budget.py` module
docstring already documented ("braking/traction ... their fit sigma already dominates their systematic ...
they need no floor"). The CdA-level tightening (18.1%, Table A) is the headline redundancy win; its
downstream propagation into b_b/b_t is real but modest, consistently with G1's prior finding.

## Test mode
**Required:** test-after allowed per handoff ("the real-data demonstration is evidence, the unit tests
guard the math")
**Satisfied:** yes -- `cross_view.py` was built with `test_cross_view.py` written FIRST and observed
failing (ModuleNotFoundError) before the module existed; `cda_jacobian` and the store wiring are
test-after (numeric/behavioral, matching the handoff's allowance).

## Evidence

```bash
cd /c/Programs/f1-627
py -c "import src.physics.layer2.estimate_store as m; print(m.__file__)"
py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_braking_view.py -q
```
```
C:\Programs\f1-627\src\physics\layer2\estimate_store.py
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
collected 51 items

tests\unit\physics\layer2\test_estimate_store.py ....................... [ 45%]
.............                                                            [ 70%]
tests\unit\physics\layer2\test_braking_view.py ...............           [100%]

============================= 51 passed in 37.90s ==============================
```

Extended set (all new/touched files):
```bash
py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_braking_view.py tests/unit/physics/layer2/test_traction_view.py tests/unit/physics/layer2/test_cross_view.py -q
```
```
collected 70 items
tests\unit\physics\layer2\test_estimate_store.py ....................... [ 32%]
.............                                                            [ 51%]
tests\unit\physics\layer2\test_braking_view.py ...............           [ 72%]
tests\unit\physics\layer2\test_traction_view.py ..........               [ 87%]
tests\unit\physics\layer2\test_cross_view.py .........                   [100%]
============================= 70 passed in 53.64s ==============================
```

`git status --porcelain -- data/` -> empty (checked after every DB-touching run; nothing under `data/`
was ever modified).

Simplification limits (`py -m src.utils.simplification_limits --paths <all 8 touched/new files>`): PASS on
every file I added or genuinely modified logic in (`cross_view.py`, `estimate_store.py`). Two PRE-EXISTING
violations remain in files I touched for unrelated reasons (`traction_view.py::fit` function_lines,
`test_estimate_store.py::test_fit_quality_metadata_populated_and_round_trips` cyclomatic_complexity) --
confirmed via `git stash` that BOTH were already failing before this gate touched those files (101 lines /
26 complexity, unchanged); my one-line `cda_jacobian=J` addition to `traction_view.py::fit` briefly pushed
it to 102 and I trimmed a comment to bring it back to the pre-existing 101 (not worsened, not fixed --
out of scope for this bounded gate to refactor a 101-line pre-existing function).

**Result:** pass.

## TDD evidence, if required
- `cross_view.py`: failing test observed (`ModuleNotFoundError: No module named 'src.physics.layer2.cross_view'`
  when running `test_cross_view.py` before the module existed) -> module written -> all 9 tests green on
  first run (hand-verified GLS/propagation arithmetic matched).
- `cda_jacobian` / store wiring: test-after per handoff's explicit allowance; each new test was written
  alongside/after its behavior and confirmed green before advancing the engine gate.
- Refactor while green: yes -- `_cross_view_covariance_fields` was refactored from one 28-cyclomatic-
  complexity function into three focused helpers (`_cda_jacobian_cross_terms`, `_fused_cda_inputs`,
  `_fused_cda_fields`) after `simplification_limits` flagged it; all 45 estimate_store/cross_view tests
  stayed green through the refactor.

## Docs/contracts touched
- `estimate_store.py`'s in-module `cross_view_covariance` shape comment (above `_JSON_COLUMNS`) extended
  with `fused_cda_z`/`fused_cda_reason` and the honest-fusion rationale -- no separate doc file exists for
  this (module docstring is the established convention for `src/physics/layer2/*.py`, per G1/G2 precedent).

## Assumptions
1. **`sigma_pd`/`sigma_co` fed to `fuse_dual_cda` are the HONEST TOTAL sigma** (fit ⊕ full systematic),
   not the bare fit-only covariance the handoff's prose literally names -- see "Fusion + propagation
   design, §3" above for the empirical justification (non-PSD on 5/5 real pairs otherwise). Flagged as a
   decision candidate for Commander confirmation.
2. **`theta_R=0.15`** (the literal every de-conflation across the codebase uses) is passed to
   `systematic_budget(...)` for the CdA shared-rel lookup; its point value doesn't change the computed
   magnitude (systematic_budget uses the fixed nuisance span, not this value -- only requires `>0`).
3. **The analytic Jacobian `J ~= drag_sign*(-rho/(2*mass))`** is a session-level approximation (no
   per-car dependence) used ONLY because the live numerical re-fit stalled within its bounded window --
   explicitly documented as the fallback path used, per the handoff's own sanctioned fallback text.
4. **Coast independence** is detected via `coast.cda_pinned is False` (the field `CoastViewResult` already
   carries, unrelated to this gate) -- production's `estimate_session()` never sets this, so `fused_cda`
   is correctly inert on today's production pathway; a caller must explicitly run
   `run_coast_view_on_session(..., cda_prior=None)` to get a fusable Coast measurement.
5. **`_fused_cda_inputs`/`_fused_cda_fields` are two helpers, not one**, purely to bring
   `_cross_view_covariance_fields`'s cyclomatic complexity under the repo's `<20` simplification limit
   (was 28) -- a mechanical split, not a design decision.

## Stop conditions hit
**Partial, on the live numerical Jacobian for BrakingView/TractionView specifically** (not the whole gate):
the bounded (300s) live re-fit attempt on Red Bull Racing's session stalled with the SAME
`calibrate_session_hp`/smoother-HP-calibration contention G1 documented (near-zero progress for the full
window, consistent with 6+ other Ship agents concurrently active in this shared session). Per the
handoff's explicit sanction, fell back to the documented analytic Jacobian approximation and stated this
per-number in the before/after table -- not silently worked around. Everything else (session load,
independent Coast fits for 5 constructors, the store wiring, all unit tests) completed live/real with no
stall.

No other stop conditions: allowed scope was not exceeded; the production pinning CdA was never touched;
no `{axis}_status` was resolved; `SYSTEMATIC_FLOOR` was not replaced; `data/*.db` was never modified.

## Out-of-scope observations
- **`session_traction.py::prepare_throttle_frontier` is NOT cheap** -- it routes through the SAME
  `session_braking._driver_samples`/`calibrate_session_hp` expensive path as `prepare_braking_frontier`
  (confirmed by reading the import), contrary to what a surface read of the module docstrings suggests
  ("works directly off the RAW car-data speed sensor" describes `clean_longitudinal_from_raw`'s role
  DOWNSTREAM of `_driver_samples`, not a substitute for it). Only `session_coast.py::prepare_coast_samples`
  is genuinely cheap (reads `session.car_data` directly, no smoother-HP calibration at all). Worth a note
  in CREW_CONTEXT or the map so a future gate doesn't repeat this exploration cost.
- **The RAW `PowerDragView.covariance[1,1]` fit sigma structurally undercovers CdA's shared systematic**
  for cars whose descent is well-supported (RBR, McLaren, Ferrari: fit sigma 1.4-1.6% vs shared_rel ~3.9%)
  -- worth flagging to G4/#506 as a substantive finding, not just a fusion-formula footnote: any downstream
  consumer treating `power_drag_area_m2_sigma`'s FIT-ONLY component (pre-`_apply_floor`) as CdA's real
  uncertainty is being overconfident by roughly the same margin this gate had to correct for.
- **A 5-constructor real Coast-independence probe on Monza 2023 Q** found only Mercedes fuses legitimately
  against PowerDrag (Ferrari/McLaren/Aston Martin/Red Bull Racing all disagree at z >= 5, post-total-sigma-
  fix); this is itself a data point (independent-Coast CdA is evidently noisy/biased for MOST 2023 Monza
  cars, plausibly the MGU-K regen contamination `coast_view.py`'s own docstring warns is a modern-era
  diagnostic caveat, not a clean measurement) worth a triage candidate for whoever eventually decides
  whether/how to route independent Coast fits into production.

## Workflow Feedback

- **Handoff gaps:** the Close Criteria's literal `σ = sqrt(est.power_drag.covariance[1,1])` /
  `σ = sqrt(est.coast.covariance[1,1])` wording reads as prescriptive but is mathematically inconsistent
  with the SAME criteria's `cov ≈ shared_rel**2 * cda_pd * cda_co` formula whenever the shared systematic
  exceeds the raw fit sigma -- which, empirically, is the common case for CdA on this exact canonical
  session (5/5 real pairs). A handoff that names an exact formula this precisely reads as load-bearing;
  worth flagging so a future precise-formula handoff either (a) explicitly says "use the fit sigma, refusal
  is an acceptable/expected outcome" or (b) says "inflate to the total sigma first" -- either is fine, but
  leaving it implicit cost real investigation time to notice and justify the deviation.
- **Context rediscovered:** `prepare_throttle_frontier`'s actual cost (routes through the same expensive
  `calibrate_session_hp` as braking) had to be discovered by reading `session_traction.py`'s imports
  directly -- G1's own IMPLEMENTER_RESULT already flagged the `store=` vs `cache=` trap but didn't flag
  this cost-path fact, even though G1 also hit the identical stall. A one-line note ("only Coast's sample
  prep avoids the expensive per-driver calibration; PowerDrag/Traction/Braking all pay it") in CREW_CONTEXT
  or the map would save the next agent real time.
- **Instructions improvised around:** the handoff names Red Bull Racing as THE canonical car for the
  before/after table, but the real live data shows RBR's own PowerDrag/Coast pair genuinely disagrees (not
  a bug -- a real finding). Rather than silently substituting a different car or forcing/fabricating a
  legitimate fuse for RBR, I reported RBR's real refusal AS the primary canonical-car evidence (satisfying
  "honest fusion" + "falsifiable z" on the handoff's own named car) and additionally probed sibling
  constructors on the IDENTICAL session to find one (Mercedes) where the SAME real methodology completes
  the positive tightening/propagation half the handoff also requires. Both are reported, clearly separated,
  nothing is fabricated.
- **What would have made this easier:** a note in the handoff (or a Map Anchor) on whether "the single-view
  PowerDrag pin used today" in Close Criterion 4 means the RAW internal pin (`cda_prior_closed.sigma`, what
  braking/traction actually use mid-fit) or the STORED/reported sigma (`drag_area_closed_m2_sigma`,
  systematic-inflated) would have saved the back-and-forth needed to construct an apples-to-apples
  before/after comparison (see Table B's "honest single-view" framing and rationale).

## Return status
`complete`
