# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g2 (execute.json: g2-review)` — Soft/fractional corner property-class membership

## Result
`APPROVE`

## Handoff compliance
All 6 close criteria from `g2-implement-handoff.md` independently verified against the actual
diff/new files, not the transcript:
- `MIN_COMPONENT_WEIGHT_FRAC = 0.05` is a pre-registered module-level constant in
  `property_mixture.py`; grep for DB/file I/O in that file returned no matches — it is a pure
  statistical core.
- `fit_property_mixture` calls `StandardScaler().fit_transform(descriptors)` and stores the
  fitted `scaler` on `MixtureFit` for reuse (confirmed by reading the source, not just the
  docstring claim).
- Selection logic: loops `k` over `range(k_range[0], k_range[1]+1)`, rejects any `k` with
  `gmm.weights_.min() < min_component_weight_frac`, picks `min(candidates, key=bic)` among
  survivors, and falls back to a freshly-fit `k=1` `GaussianMixture` (not a raise, not a
  silently-accepted rejected `k`) when `candidates` is empty. Read the four selection-relevant
  test bodies directly: the 2-/3-cluster recovery tests use well-separated blobs; the
  thin-blob test (190 pts vs 8 pts, 8/198≈0.0404<0.05) asserts `fit.k == 1` (not merely
  `!= 2`), which genuinely exercises the fallback across the whole `k_range=(2,6)`, not just
  the naturally-matching `k=2`.
- `posterior_membership` transforms query descriptors via `fit.scaler.transform` (never
  `fit_transform`) and calls `fit.gmm.predict_proba` — confirmed by reading the implementation
  line-by-line, per the handoff's explicit warning that this is "easy to get subtly wrong."
  Rows sum to 1 (`np.allclose` test present and independently reproduced).
- `segment_classifier.py`'s diff is purely additive: `git diff` shows only a new import block
  and one new method (`soft_class_membership`) inserted after `classify_samples`; everything
  from `_classify_regime` onward is byte-for-byte unchanged (no lines touched below the
  insertion point). `physics_data_models.py` has zero diff (`_VALID_REGIMES` untouched).
  `soft_class_membership` returns `None` for `sample.regime != "corner"` and for
  `abs(sample.curvature) <= 1e-9`; returns a `(k,)` array summing to 1 for a valid corner
  sample — all three branches independently test-verified.
- Unit conversion confirmed correct and correctly DIFFERENT from Gate 1's convention:
  `soft_class_membership` computes `lateral_g = sample.a_lateral / GRAVITY_MS2` because
  `KinematicSample.a_lateral` is raw m/s² (built from `_compute_long_lat(velocity,
  acceleration)` in `classify_samples`, confirmed by reading `segment_classifier.py:60-89`).
  This matches how the REST of the codebase treats `a_lateral` — `lateral_report.py:76` and
  `session_lateral.py:68` both divide `a_lateral` by `_G` to reach g-units — so this is
  consistent with existing convention, not a one-off. Gate 1's `corner_descriptors.py`, by
  contrast, takes `mu_lat_p90` which is ALREADY in g-units per `grip_bin_obs.py`'s own
  `mu_lat = a_lat / G` derivation, and does NOT re-divide. The implementer did not confuse the
  two call sites.

## Scope drift
None. Diff touches exactly the allowed files: `src/physics/layer2/property_mixture.py` (new),
`src/physics/segment_classifier.py` (additive method only), `tests/unit/physics/layer2/
test_property_mixture.py` (new), `tests/unit/physics/test_segment_classifier.py` (additive
`TestSoftClassMembership` class, 3 pre-existing cases untouched). `arcs.py`/
`corner_descriptors.py`/their tests are also present as uncommitted worktree changes but are
Gate 1's already-approved slice — correctly excluded from this review per the handoff.
Specific exclusions respected: no DB I/O (grep-clean), no `circuits.yaml`/production-default
changes, no `evo_predictor`/`latent_power`/`compound_prior` imports (independently re-ran the
grep over all 4 touched files — exit 1, zero matches).

## Evidence verdict
Required evidence present and reproduced. Independently re-ran (after confirming the worktree
resolves correctly — `py -c "import src.physics.layer2.property_mixture as m; print(m.__file__)"`
prints `C:\Programs\f1-625\src\physics\layer2\property_mixture.py`, not the main checkout):

```
cd /c/Programs/f1-625
py -m pytest tests/unit/physics/layer2/test_property_mixture.py tests/unit/physics/test_segment_classifier.py -v
```
→ 15 passed, same 15 test IDs as `g2-implement-result.md`'s transcript, byte-for-byte match.

Also independently re-ran `py -m src.utils.simplification_limits --paths <4 touched files>` →
`PASS (4 files checked)`, matching the implementer's claim.

One caveat on evidence depth (not a blocker): `test_reuses_stored_scaler_not_a_refit_one`
only asserts output shape and row-sum-to-1 — both would hold whether or not the scaler were
actually reused vs. refit (GaussianMixture's `predict_proba` normalizes to 1 regardless of
input scale). The real guarantee was confirmed by reading the implementation
(`fit.scaler.transform`, never `fit_transform`, inside `posterior_membership`), not by this
test alone — flagged for awareness, not blocking, since the source-level check is the stronger
verification the handoff itself asked for ("verify by reading the implementation").

## Code/doc quality
Minimal, maintainable, tested, project-rule compliant. `CREW_CONTEXT.md` rules checked: no
print() in library code (grep-clean); module-level state limited to the immutable
`MIN_COMPONENT_WEIGHT_FRAC` constant; units explicit in code and docstrings, including an
explicit inline warning distinguishing this call site's unit convention from Gate 1's.
`MIN_COMPONENT_WEIGHT_FRAC = 0.05` is exactly the frozen value from the handoff's Authority
section, defined before any real-data path exists in the codebase, not tuned post-hoc.

Fowler code-smell pass (`r6-fowler`, recorded to `.agent-work/625-segmentation-substrate/
g2-review/g2-fowler-pass.json`, `scripts/verify_fowler_pass.py` exit 0): 10 of 12 baseline
smells absent. `duplicated-code` **flagged** (non-blocking observation): the support-floor
fallback (`k=1`) re-fits a `GaussianMixture` and records its BIC using the same 3-line
create/fit/record pattern as the main `k_range` loop body — a small `_fit_one` helper would
remove it, but it's minor and clearly commented. `divergent-change` **overridden**: the additive
method gives `SegmentClassifier` two reasons to change (regime classification + soft membership
query), but `CONVERGED_PLAN.md`'s "Recommendation"/"Untaken roads" sections show this was a
deliberate, critic-reviewed plan decision (reject candidate B's isolated `soft_regime.py`
adapter in favor of candidate A's literal in-place placement, per the launch order's own
wording) — a documented repo-standard decision subordinates the smell, and the statistical
core stays isolated in `property_mixture.py` so the risk is contained to a thin delegation.

## Map impact verdict
- **Evidence supports claimed change:** yes — every claim in `g2-implement-result.md`'s Map
  Impact section was independently checked against the diff/source and holds.
- **Constraints not violated:** yes — `constraint:physics_region_no_evo_import` and pre-ruling
  #1 (soft/fractional membership, never a hard tag) both independently confirmed.
- **Notes match the diff:** yes — structural/capability anchors match exactly what changed; no
  overstated or missing impact.
- **Decision candidates surfaced:** the two "your call, document it" choices (whether
  `bic_scores` includes floor-rejected `k`'s BIC; 1-D vs 2-D single-row `posterior_membership`
  return) were genuinely within the handoff's own delegated latitude, both documented in
  docstrings/tests — no undisclosed decision requiring authority beyond what was already
  delegated.
- **Durable context routed:** no new triage candidates from this review; `g1-integrate`'s
  pre-existing `tc1` (session_braking.py mis-citation) is unrelated to this gate's slice.

## Reconciliation check
No divergence from `CONVERGED_PLAN.md` Gate 2 requiring Commander reconciliation. The
additive-in-`segment_classifier.py` placement and the separate `property_mixture.py`
statistical core match the frozen, critic-reviewed plan exactly.

## Blockers
- none

## Out-of-scope observations
- `duplicated-code` (Fowler pass): minor 3-line duplication between the fallback `k=1` fit and
  the main loop body's fit/record pattern in `fit_property_mixture` — candidate for a small
  `_fit_one` extraction if touched again, not worth a standalone follow-up issue at this size.

## Workflow Feedback
- **Handoff gaps:** none material. The handoff's explicit call-out of the two-call-site unit
  convention difference (`corner_descriptors.py` vs `segment_classifier.py`) was precise enough
  that verifying it required only reading both files once, no back-and-forth.
- **Context rediscovered:** confirmed `KinematicSample.a_lateral`'s m/s² convention isn't
  documented on the dataclass field itself (no inline unit comment on
  `physics_data_models.py:69`) — had to cross-reference `segment_classifier.py`'s own
  `_compute_long_lat` call site and two other consumers (`lateral_report.py`,
  `session_lateral.py`) to independently confirm the unit rather than trusting the new
  docstring's claim at face value. Not a defect in this gate's diff, but a pre-existing
  documentation gap the handoff correctly warned around rather than fixed (out of scope here).
- **Instructions improvised around:** none — the reviewer skill's engine-drive workflow and the
  Fowler-pass rail both applied cleanly to this gate's small, additive diff.
- **What would have made this easier:** none — none — confirmed after review: the handoff's
  Close Criteria section already enumerated exactly the checks this review needed to run, in
  the same order they were verified.

## Return status
`complete`
