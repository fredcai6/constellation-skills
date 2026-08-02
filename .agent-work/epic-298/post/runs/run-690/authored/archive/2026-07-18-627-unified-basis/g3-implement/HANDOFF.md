# Implementer Handoff

## Gate
g3 (cross-view covariance population + redundancy demonstration — Tier-1 #1, NON-DEFERRABLE)

## Task
Persist REAL cross-view covariance terms and DEMONSTRATE, non-tautologically, that multi-view redundancy tightens
a SHARED parameter's uncertainty vs the single-view baseline — connecting the two (the persisted covariance must be
what carries the tightening). This is the phase's non-deferrable core.

## Protected Intent
The demonstration must NOT be a tautology (inverse-variance always tightens — that alone proves nothing) and must
USE the persisted cross-view terms. Honest σ over optimistic σ: the two CdA measurements share within-session
mass/ρ, so they are NOT independent — fuse with that correlation (a naive-independent fuse understates σ and is forbidden).

## Test Mode
test-after allowed; the real-data demonstration is evidence, the unit tests guard the math.

## Close Criteria
1. **Expose the Jacobian.** `BrakingView.fit` and `TractionView.fit` already compute
   `J = cda_frontier_jacobian(...)` (braking_view.py:242-246) then discard it. Add a `cda_jacobian: np.ndarray |
   None = None` field to `BrakingViewResult` (braking_view.py:32) and `TractionViewResult` (traction_view.py:41)
   and populate it with that `J` (a length-2 vector d[coef]/d(CdA)).
2. **Persist the cross-view terms.** In `estimate_store.record_from_estimate`, populate `cross_view_covariance`
   (the G2 sparse dict): `cov(CdA,[a_b,b_b]) = est.cda_closed.sigma**2 * est.braking.cda_jacobian` and
   `cov(CdA,[a_t,b_t]) = est.cda_closed.sigma**2 * est.traction.cda_jacobian` — deterministic, recoverable
   (x7 map (b) row 2). Round-trips through JSON (G2 wired `cross_view_covariance` into `_JSON_COLUMNS`). Null-safe
   when a view/Jacobian is absent.
3. **Honest (cov-aware) dual-CdA fusion.** The two independent-samples CdA measurements are PowerDrag descent
   (`est.power_drag.drag_area_closed_m2`, σ = sqrt(`est.power_drag.covariance[1,1]`)) and Coast envelope
   (`est.coast.coast_drag_area_m2`, σ = sqrt(`est.coast.covariance[1,1]`)). They SHARE within-session mass/ρ →
   correlated. Get CdA's SHARED relative component from G1 `systematic_budget(...)` and form the shared-nuisance
   covariance between the two CdA estimates (both scale ≈ the same way with mass/ρ, so cov ≈ shared_rel**2 *
   cda_pd * cda_co). Fuse cov-aware:
   `σ_fused² = 1 / (uᵀ Σ⁻¹ u)` with `u=[1,1]`, `Σ = [[σ_pd², cov],[cov, σ_co²]]` (generalized least squares) — the
   honest fused σ. Persist `fused_cda = (mu, sigma)` in `cross_view_covariance`. Report the AGREEMENT
   `z = |cda_pd - cda_co| / sqrt(σ_pd² + σ_co² - 2·cov)`: if `z >= ~5` the two views DISAGREE → fusion is
   ILLEGITIMATE; flag it (e.g. `fused_cda=None` + a reason) rather than silently fusing a contradiction.
4. **Non-tautological redundancy demonstration (the NON-DEFERRABLE evidence).** On the CANONICAL session
   Italy(Monza) RBR 2023 Q: take the honest fused CdA (tighter than the single-view PowerDrag pin used today) and
   PROPAGATE it through the PERSISTED `cov(CdA,b_b)` / `cov(CdA,b_t)` to show that b_b and b_t (the SHARED
   downstream params) get a tighter effective σ than under the single-view PowerDrag pin. Report a before/after
   table: PowerDrag-only pin σ_CdA vs fused σ_CdA; and the resulting b_b,b_t effective σ before/after; and the
   agreement z. This links persisted covariance (2) → tightening (4). DO NOT change the production pinning CdA
   (`est.cda_closed` / `drag_area_closed_m2`) — fused is an ADDITIONAL persisted quantity only.

## Unit tests (tests/unit/physics/layer2/, synthetic — FastF1-free)
- Cross-view terms populate non-trivially from a synthetic est with a known Jacobian + σ_CdA, and reload equal.
- The cov-aware fused σ on a CORRELATED synthetic pair is `>=` the naive-independent fused σ (asserts the honesty
  fix — naive would understate). And `<` the smaller component σ when correlation is < 1 (redundancy still helps).
- A 5σ-disagreement synthetic pair flags illegitimate fusion (fused_cda None + reason), not a silent fuse.
- The b_b/b_t propagation: given a fused σ_CdA smaller than the pin σ_CdA and a non-zero cov(CdA,b_b), the
  propagated b_b σ is smaller than the pin-baseline b_b σ (the tightening is real and connected).

## Allowed Scope
- EDIT `braking_view.py` (add+populate `cda_jacobian` on result), `traction_view.py` (same),
  `estimate_store.py::record_from_estimate` + its field helpers (populate `cross_view_covariance`).
- May ADD a small helper module or function for the cov-aware fusion + propagation (e.g. in `estimate_store.py`
  or a new `src/physics/layer2/cross_view.py`) — your call; document it.
- CREATE/EDIT tests under `tests/unit/physics/layer2/`.
- A bounded real-data demonstration script under `.agent-work/627-unified-basis/g3-implement/` (local-only) OR a
  `scripts/`-committed reproducer — your call; if committed, keep it ASCII + guarded.
- READ-ONLY: `systematic_budget.py` (G1), `power_drag_view.py`, `coast_view.py`, `session_estimator.py`.

## Specific Exclusions
- Do NOT change the production pinning CdA / `est.cda_closed` flow, `circuits.yaml`, gold, or any default.
- Do NOT resolve `{axis}_status` or replace `SYSTEMATIC_FLOOR` — that is G4.
- Do NOT write/commit `data/*.db`; `git checkout -- data/` after any DB-touching run.

## Constraints
- `constraint:physics_region_no_evo_import`. ASCII; `py` launcher.
- Frozen dataclasses: add the new field with a default so existing constructors keep working.
- Honest-wide fusion (cov-aware); naive-independent fuse is forbidden.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — braking_view.py::cda_frontier_jacobian/BrakingViewResult;
  traction_view.py::TractionViewResult; power_drag_view.py::PowerDragResult (cda_prior_closed/covariance[1,1]);
  coast_view.py::CoastViewResult (coast_drag_area_m2/covariance[1,1]); estimate_store.py::record_from_estimate.
- Capability: cross-view covariance persistence; multi-view redundancy tightening (NON-DEFERRABLE).
- Constraint: no production-default change; honest-wide σ.
- Evidence: honest fused CdA propagated through persisted cov(CdA,b_b/b_t) tightens b_b,b_t vs single-view pin on
  Italy RBR 2023 Q (before/after); agreement z falsifiable.
- Map confidence flag: worktree editable-.pth trap — assert `__file__` under worktree before any real-data run.

## Deliverable Path Check
- Committed — `braking_view.py`, `traction_view.py`, `estimate_store.py`, tests (edits/new, tracked).
- Local-only — any demo script under `.agent-work/...` (gitignored; state it so the reviewer doesn't expect it in the diff).

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_braking_view.py -q` — full pass; paste tail.
- The Italy(Monza) RBR 2023 Q before/after redundancy table (fused vs pin σ_CdA; b_b,b_t before/after; agreement z).
  If the live fit STALLS (G1 saw smoother-HP calibration stall under concurrent-agent contention): run with a
  BOUNDED timeout (<=10 min foreground); if it still stalls, document the stall, and provide the demonstration on
  a stored `session_estimates` row (load an existing Monza RBR 2023 Q estimate from
  `C:/Programs/f1Brainz/data/physics_estimates.db` if present) OR a realistic fixture with measured-scale σ — and
  STATE which path you used. The tightening MUST be shown on real-scale numbers; do not fabricate.

## Verification Commands
```bash
cd /c/Programs/f1-627
py -c "import src.physics.layer2.estimate_store as m; print(m.__file__)"   # assert under C:\Programs\f1-627
py -m pytest tests/unit/physics/layer2/test_estimate_store.py tests/unit/physics/layer2/test_braking_view.py -q
```

## Suggested Model Tier
stronger — the non-tautological demonstration, the cov-aware fusion honesty, and the propagation chain are the
crux of the whole phase.

## Authority
Tier/scope frozen by the launch order. You decide the fusion helper's placement + the exact cross_view_covariance
value population. You must NOT change production defaults or the production pinning CdA. If cross-view persistence
proves INFEASIBLE, STOP and return that as a blocker (it is the non-deferrable core — the Commander floats it up).

## Worktree Isolation (CRITICAL)
cwd MUST be `C:/Programs/f1-627`. Assert `py -c "import src.physics.layer2.estimate_store as m; print(m.__file__)"`
prints under `C:\Programs\f1-627` before any real-data run. Data DBs are absolute paths into
`C:/Programs/f1Brainz/data/` (telemetry_store.db, physics_estimates.db, telemetry/) — your worktree lacks the
untracked data. Do NOT commit data/*.db.

## Stop Conditions
Stop and return (blocker) if: cross-view persistence is infeasible; the redundancy tightening cannot be shown on
real-scale numbers by any bounded path; a production default must change; or a decision beyond the fusion/propagation
design is needed.

## Return Format
Write `IMPLEMENTER_RESULT` to `.agent-work/627-unified-basis/g3-implement/IMPLEMENTER_RESULT.md` AND deliver a
summary to ShipF-627 (route to team-lead if unaddressable) via SendMessage before ending your turn: completed slice,
files changed, the fusion+propagation design, the before/after redundancy table (real numbers) + which run path you
used, test tail, assumptions, stop conditions, out-of-scope observations, workflow feedback.
