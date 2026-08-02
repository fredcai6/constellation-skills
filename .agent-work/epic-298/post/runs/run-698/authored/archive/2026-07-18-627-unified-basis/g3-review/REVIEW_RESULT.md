# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3 (cross-view covariance population + redundancy demonstration -- Tier-1 #1, NON-DEFERRABLE)`

## Result
`APPROVE`

## Handoff compliance
All four close criteria met, verified independently (not accepted on the implementer's report alone):

1. **Jacobian exposed.** `cda_jacobian: np.ndarray | None = None` added to `BrakingViewResult`/`TractionViewResult`, populated with the SAME `J` used to build `.covariance` (confirmed by diff read + `test_fit_exposes_cda_jacobian`'s independent sigma->1e-9 finite-difference cross-check in both view test files).
2. **Cross-view terms persisted.** `_cda_jacobian_cross_terms` computes `cov(CdA,[a_b,b_b])`/`cov(CdA,[a_t,b_t]) = cda_sigma**2 * cda_jacobian`, null-safe, and round-trips through the store's existing JSON column (`test_cross_view_jacobian_terms_populate_and_round_trip`).
3. **Honest cov-aware fusion.** `fuse_dual_cda` builds `Sigma=[[sigma_pd**2,cov],[cov,sigma_co**2]]` with `cov` from G1's `systematic_budget(...)["cda"]` shared_rel, reports a falsifiable agreement `z`, and refuses (`mu=sigma=None`) at `z>=5` or non-PSD `Sigma`. Independently re-ran the implementer's local `monza_finalize.py` against the real `physics_estimates.db` stored row (`fitted_at=2026-07-06T22:31:47`, confirmed present) and reproduced the exact numbers in the report: RBR `z=6.804` refused, Mercedes `z=2.033` legitimate, `fused_sigma=0.045994 < 0.056154` (honest single-view).
4. **Non-tautological demonstration.** RBR's genuine PowerDrag/Coast disagreement is correctly refused; Mercedes (same session) shows real tightening propagated through `propagate_shared_param_variance`, which is null-tested (`cov==0` -> unchanged variance) to prove the tightening is carried BY the persisted covariance term, not a disjoint "inverse-variance always helps" restatement. Independently reproduced `sigma_bb_fused=0.0010459` vs `sigma_bb_honest_single=0.0010461` etc., matching the report exactly.

Production pinning CdA (`est.cda_closed`/`drag_area_closed_m2`) is untouched -- `fused_cda` has no other consumer anywhere in `src/` (grep confirms). `data/` clean throughout (`git status --porcelain -- data/` empty). Required test command reproduced twice: `70 passed`.

## Scope drift
None. `git status --porcelain` matches the allowed scope exactly: `braking_view.py`, `traction_view.py`, `estimate_store.py` (modified); `cross_view.py`, `test_cross_view.py` (new); the three touched test files; `.agent-work/627-unified-basis/` (local-only, gitignored). Specific exclusions all respected: no `{axis}_status` resolution added (the one "status" hit in the diff is a pre-existing, unchanged comment line), no `SYSTEMATIC_FLOOR` touch, `circuits.yaml`/`params/gold` untouched, no evo import (grep confirms), no `data/*.db` write.

## Evidence verdict
Both required evidence items reproduced independently:
- `py -m pytest tests/unit/physics/layer2/test_estimate_store.py test_braking_view.py test_cross_view.py test_traction_view.py -q` -> `70 passed`, run twice by the reviewer.
- The Monza (Italy) RBR 2023 Q / Mercedes before/after table: re-ran directly, byte-for-byte matching numbers. Additionally independently recomputed the "naive fuse looks falsely tighter" claim (`mu=1.0722, sigma=0.014612, z_naive_uncorrelated=8.519` -- matches exactly) and independently verified the PSD claim that motivates the honest-sigma switch: bare fit-only sigmas give `var_diff=-0.00127` (non-PSD, un-computable) for the RBR pair, honest total sigmas give `var_diff=+0.00229` (valid) -- the switch is mathematically required for the fusion to run at all on this real pair, not a convenience.

Test mode (test-after allowed per handoff) satisfied: `cross_view.py` built test-first (failing `ModuleNotFoundError` observed before the module existed), `cda_jacobian`/store wiring test-after per the explicit allowance.

## Code/doc quality
Fowler refactoring pass run (`.agent-work/627-unified-basis/g3-review/fowler_pass.json`, verified via `verify_fowler_pass.py` -> `fowler pass ok: smells=12`). One non-blocking observation (`data-clumps`: an 8-element internal helper tuple, mechanical complexity-limit split, single call site). Two smells legitimately overridden with a logged repo standard + reason (`duplicated-code`: matches the file's own pervasive per-axis-helper convention; `comments-as-deodorant`: matches CREW_CONTEXT's explicit-physics-reasoning requirement). `simplification_limits` PASS on every file with new/changed logic; the two remaining violations (`traction_view.py::fit` 101 lines, a test's cyclomatic complexity 26) were independently confirmed pre-existing and unchanged via `git stash` diff against the base commit.

## Map impact verdict
- **Evidence supports claimed change:** yes -- independently reproduced, see above.
- **Constraints not violated:** yes -- `constraint:physics_region_no_evo_import` (grep confirms no evo import), frozen-dataclass defaults (`@dataclass(frozen=True)` confirmed on both `*ViewResult` classes, new field defaulted), honest-wide fusion (independently confirmed the fused sigma is never silently substituted with the tighter naive-independent value, except at the documented zero-correlation limit).
- **Notes match the diff:** yes -- Map Anchors (`struct:physics.layer2`, new `cross_view.py`, `estimate_store.py::record_from_estimate`) match exactly what changed.
- **Decision candidates surfaced:** yes -- the honest-total-sigma switch (a deviation from the handoff's literal formula wording) was self-flagged by the implementer and is routed to Commander here as `tc1`, with the reviewer's independent PSD verification attached so Commander can ratify with evidence in hand rather than re-deriving it.
- **Durable context routed:** yes -- `tc2` routes three implementer out-of-scope observations (prepare_throttle_frontier's real cost, PowerDragView fit-sigma undercoverage relevant to #506/G4, the 5-constructor Coast-independence probe finding) to Triage.

## Reconciliation check
No unreconciled architecture divergence blocks this gate. The one genuine judgment call (honest-sigma switch) is a correctness fix, independently verified as mathematically necessary rather than a pass-forcing hack, and is surfaced as a decision candidate rather than silently baked in.

## Blockers
- none

## Out-of-scope observations
- tc1 (decision candidate, routed to Commander): ratify the honest-total-sigma convention in `fuse_dual_cda` inputs as the canonical approach going forward.
- tc2 (triage candidate): `prepare_throttle_frontier` cost-path note for CREW_CONTEXT/map; `PowerDragView` fit-sigma undercoverage relevant to #506/G4; the 5-constructor Coast-independence probe finding (only Mercedes fuses legitimately against PowerDrag on this session).

## Workflow Feedback
- **Handoff gaps:** the g3-implement HANDOFF.md's Close Criterion 3 names an exact formula (`sigma = sqrt(est.power_drag.covariance[1,1])`) that reads as prescriptive but is mathematically inconsistent with the same criteria's shared-covariance formula whenever the shared systematic exceeds the raw fit sigma -- which is the empirical common case here (5/5 real pairs). The Required Evidence section's stall-fallback sanction was clear and well-used; a similar explicit sanction for "the exact sigma formula may need honest-inflation if PSD fails" would have removed the implementer's (and my) need to independently re-derive that this deviation was warranted.
- **Context rediscovered:** none beyond what the implementer already flagged (prepare_throttle_frontier's real cost) -- I did not need to rediscover it myself since IMPLEMENTER_RESULT.md stated it clearly; routed to Triage as tc2 rather than treated as reviewer-rediscovered friction.
- **Instructions improvised around:** the reviewer HANDOFF's "confirm the demo USES the persisted terms (connected)" was satisfiable via a literal DB round-trip read only for a session that had gone through this gate's code with a live fit; since the real Monza stored row predates G3 (fitted 2026-07-06, before this code existed) and the live re-fit stalled (documented, sanctioned fallback), the actual demo recomputes the identical formula (`cda_jacobian_covariance`'s `sigma_cda**2 * J`) via the SAME `propagate_shared_param_variance` function rather than reading a literal round-tripped JSON blob. I judged this satisfies "connected" in spirit (same formula, same function, cross-checked against the direct math inline) given the g3-implement HANDOFF's own explicit sanction for this exact stall scenario, but flag the distinction for anyone auditing this gate later: the unit-level round-trip (`test_cross_view_jacobian_terms_populate_and_round_trip`) is what proves persistence-and-reload; the real-data demo proves the propagation math on real numbers using the same formula, not a literal reload of a stored JSON blob (no such populated row exists yet in production).
- **What would have made this easier:** none -- the g3-review HANDOFF's framing of the two hardest judgments (connectedness, honest-sigma-switch-vs-hack) was precise enough to drive straight at the load-bearing verification (re-running the real script, independently checking the PSD math) rather than guessing what mattered.

## Return status
`complete`
