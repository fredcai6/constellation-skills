# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2 (execute.json: g2-implement)` — Soft/fractional corner property-class mixture

## Completed slice
New `src/physics/layer2/property_mixture.py` implementing a BIC-selected, support-floored
Gaussian mixture over standardized `(radius, lateral_g)` descriptors
(`MIN_COMPONENT_WEIGHT_FRAC = 0.05`, `MixtureFit`, `fit_property_mixture`,
`posterior_membership`), plus one additive method `SegmentClassifier.soft_class_membership`
in `src/physics/segment_classifier.py` that queries a fitted mixture for a single corner
sample. Both close criteria in the handoff are met.

## Scope
**Files changed:**
- `src/physics/layer2/property_mixture.py` (new)
- `src/physics/segment_classifier.py` (edit — additive method only, +43/-1 lines; the `-1`
  is a single blank-line adjustment around the new import block, not a behavior change)
- `tests/unit/physics/layer2/test_property_mixture.py` (new — 9 cases)
- `tests/unit/physics/test_segment_classifier.py` (edit — added `TestSoftClassMembership`,
  3 new cases; all 3 pre-existing cases untouched and still pass)

**Specific exclusions touched:** no — no DB I/O anywhere (both `fit_property_mixture` and
`posterior_membership` are pure functions over `np.ndarray`; `soft_class_membership` takes an
in-memory `KinematicSample` + `MixtureFit`); no `circuits.yaml`/production-default writes; no
`evo_predictor`/`latent_power`/`compound_prior` imports anywhere in the new/changed code
(verified: `grep -rn "evo_predictor\|latent_power\|compound_prior"` over all four touched
files returned no matches, exit 1).

## Behavior changed
Yes, additively only. `SegmentClassifier._classify_regime` and
`physics_data_models._VALID_REGIMES` are byte-identical to before this gate — confirmed by
`git diff` on both files: `segment_classifier.py`'s diff shows only a new import block and one
new method inserted after `classify_samples`, with no lines touched below that insertion
point (`_classify_regime` and everything after it unchanged); `physics_data_models.py` has
zero diff (`git diff` produced no output).

`soft_class_membership`'s new logic:
```python
def soft_class_membership(
    self, sample: KinematicSample, fit: "MixtureFit"
) -> Optional[np.ndarray]:
    if sample.regime != "corner":
        return None
    if abs(sample.curvature) <= 1e-9:
        return None
    radius = 1.0 / sample.curvature
    lateral_g = sample.a_lateral / GRAVITY_MS2
    descriptor = np.array([[radius, lateral_g]], dtype=float)
    membership = posterior_membership(fit, descriptor)
    return membership[0]
```
Not wired into `classify_samples`'s main loop, per the handoff's explicit exclusion.

## Map Impact
- **Structural anchors touched:** `struct:physics.layer2` — new `src/physics/layer2/
  property_mixture.py` module (`MIN_COMPONENT_WEIGHT_FRAC`, `MixtureFit`,
  `fit_property_mixture`, `posterior_membership`, all public). `struct:physics` —
  `src/physics/segment_classifier.py`, additive method `soft_class_membership` only.
- **Capabilities added/changed/affected:** soft/fractional corner property-class mixture
  (new) — support-driven `k` selection (BIC among floor-surviving candidates, `k=1` fallback
  when every candidate is floor-rejected) over standardized `(radius, lateral_g)`; per-sample
  posterior membership query via `SegmentClassifier.soft_class_membership` (corner-only,
  `None` for straights and degenerate zero-curvature corners). Both are the named Phase-1
  deliverable-1 pieces of this gate; `property_mixture.py` is a pure statistical core with no
  caller yet beyond this gate's own tests and `soft_class_membership` (Gates 3/4's job to wire
  against real `grip_bin_obs` data).
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` — honored
  (only `src.physics.*`/`sklearn` imports added). Pre-ruling #1 (soft/fractional membership,
  support-driven class count, never one-corner-one-property) — honored throughout:
  `posterior_membership` always returns a full `(N, k)` probability simplex, never a hard
  argmax tag; `MIN_COMPONENT_WEIGHT_FRAC` is pre-registered at 0.05 and not tuned against any
  real-data fit (Gate 2 has no access to that data path, per the handoff).
- **Decision candidates / resolved decisions:** `bic_scores` records BIC for every candidate
  `k` fitted in `k_range` (both accepted and support-floor-rejected), not just the selected
  `k` — read as a diagnostic-transparency choice consistent with "tried," not "accepted," per
  the handoff's own wording ("BIC score per candidate k tried"); flagged here in case Gate 3/4
  expected accepted-only. `soft_class_membership` returns the single-row posterior as a 1-D
  `(k,)` array (`membership[0]`) rather than the 2-D `(1, k)` row — the handoff left this
  choice open ("your call, document it"); documented in the method's docstring test
  (`membership.shape == (fit.k,)`).
- **Claims/evidence produced:** BIC+floor selection recovers the true `k` on well-separated
  synthetic 2- and 3-cluster blobs (`test_two_well_separated_clusters_recovers_k_equals_2`,
  `test_three_well_separated_clusters_recovers_k_equals_3`); the floor collapses selection
  toward `k=1` on a thin/unsupported-component blob (190 vs 8 points, minority weight
  ~0.040 < 0.05) across the WHOLE `k_range=(2,6)`, not just the naturally-matching `k=2`
  (`test_thin_component_split_is_rejected_falls_back_to_k1`,
  `test_all_candidate_ks_rejected_uses_k1_gmm_not_raise`); `posterior_membership` rows always
  sum to 1 including for out-of-fit-distribution queries reusing the stored scaler
  (`test_reuses_stored_scaler_not_a_refit_one`); `soft_class_membership`'s three branches
  (corner-valid / straight-any-of-three / corner-degenerate-curvature) each independently
  verified.
- **Trust limitations / drift found:** none found — handoff's structural description of
  `segment_classifier.py` matched the real file exactly (Stop Condition check at m0-context
  passed cleanly, no discrepancy to report).
- **Triage candidates:** none raised by this gate's work.

## Test mode
**Required:** `test-after` (handoff's Test Mode section: "Both pieces are testable in
isolation... test-after with synthetic fixtures, project norm")
**Satisfied:** yes — TDD red→green was additionally run for both m1 and m2 (test file written
first, observed failing via `ModuleNotFoundError` / `AttributeError`, then implementation
written to green) as the plan's own discipline, which is a strict superset of the handoff's
minimum test-after requirement.

## Evidence

```bash
cd /c/Programs/f1-625
py -m pytest tests/unit/physics/layer2/test_property_mixture.py tests/unit/physics/test_segment_classifier.py -v
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0 -- ...\python.exe
collecting ... collected 15 items

tests/unit/physics/layer2/test_property_mixture.py::TestConstant::test_min_component_weight_frac_pinned_at_0_05 PASSED [  6%]
tests/unit/physics/layer2/test_property_mixture.py::TestFitPropertyMixtureClusterRecovery::test_two_well_separated_clusters_recovers_k_equals_2 PASSED [ 13%]
tests/unit/physics/layer2/test_property_mixture.py::TestFitPropertyMixtureClusterRecovery::test_three_well_separated_clusters_recovers_k_equals_3 PASSED [ 20%]
tests/unit/physics/layer2/test_property_mixture.py::TestSupportFloorRejection::test_thin_component_split_is_rejected_falls_back_to_k1 PASSED [ 26%]
tests/unit/physics/layer2/test_property_mixture.py::TestSupportFloorRejection::test_all_candidate_ks_rejected_uses_k1_gmm_not_raise PASSED [ 33%]
tests/unit/physics/layer2/test_property_mixture.py::TestFitPropertyMixtureStandardization::test_fit_stores_a_scaler_fitted_on_the_descriptors PASSED [ 40%]
tests/unit/physics/layer2/test_property_mixture.py::TestFitPropertyMixtureStandardization::test_bic_scores_recorded_per_candidate_k PASSED [ 46%]
tests/unit/physics/layer2/test_property_mixture.py::TestPosteriorMembership::test_rows_sum_to_one PASSED [ 53%]
tests/unit/physics/layer2/test_property_mixture.py::TestPosteriorMembership::test_reuses_stored_scaler_not_a_refit_one PASSED [ 60%]
tests/unit/physics/test_segment_classifier.py::TestALongSource::test_clean_case_both_sources_agree PASSED [ 66%]
tests/unit/physics/test_segment_classifier.py::TestALongSource::test_noisy_accel_state_speed_derivative_wins PASSED [ 73%]
tests/unit/physics/test_segment_classifier.py::test_segment_classification_regimes PASSED [ 80%]
tests/unit/physics/test_segment_classifier.py::TestSoftClassMembership::test_corner_sample_returns_membership_summing_to_one PASSED [ 86%]
tests/unit/physics/test_segment_classifier.py::TestSoftClassMembership::test_straight_sample_returns_none PASSED [ 93%]
tests/unit/physics/test_segment_classifier.py::TestSoftClassMembership::test_zero_curvature_corner_regime_returns_none PASSED [100%]

============================= 15 passed in 4.36s ==============================
```

**Result:** `pass` — count-before-after: 3 pre-existing `test_segment_classifier.py` cases
before this gate started (verified by running the file before editing, at the m2 step);
3 pre-existing + 3 new = 6 in `test_segment_classifier.py` after, plus 9 new in
`test_property_mixture.py` = 15 total. No pre-existing case removed or weakened.

Additional evidence — `simplification_limits` on touched files (project norm):
```bash
py -m src.utils.simplification_limits --paths src/physics/layer2/property_mixture.py src/physics/segment_classifier.py tests/unit/physics/layer2/test_property_mixture.py tests/unit/physics/test_segment_classifier.py
```
```
PASS (4 files checked)
```

Deliverable-path check (project norm — not gitignored, real new/edited files):
```bash
git check-ignore -v src/physics/layer2/property_mixture.py   # exit 1 (not ignored)
git check-ignore -v tests/unit/physics/layer2/test_property_mixture.py  # exit 1 (not ignored)
```

## TDD evidence, if required
- Failing test observed (m1): `py -m pytest tests/unit/physics/layer2/test_property_mixture.py -v`
  → `ModuleNotFoundError: No module named 'src.physics.layer2.property_mixture'` (1 error
  during collection, before `property_mixture.py` existed).
- Failing test observed (m2): `py -m pytest tests/unit/physics/test_segment_classifier.py -v`
  → 3 pre-existing tests PASSED, 3 new `TestSoftClassMembership` tests FAILED with
  `AttributeError: 'SegmentClassifier' object has no attribute 'soft_class_membership'`
  (before the method existed).
- Passing test observed: both files above, full green (9/9 and 6/6 respectively; combined
  15/15 in the Evidence section above).
- Refactor while green: no refactor pass was needed — both implementations were correct on
  first attempt after the red observation.

## Docs/contracts touched
- none — both new pieces are additive pure-function/method code with docstrings; no committed
  contract/schema doc governs this module.

## Assumptions
- `MixtureFit.bic_scores` records BIC for every candidate `k` fitted in `k_range`, including
  ones later rejected by the support floor (not just the selected `k`) — chosen because the
  handoff says "the BIC score per candidate k tried," and "tried" reads as the full attempted
  set, useful for diagnosing why a particular `k` was rejected. If Gate 3/4 expects
  accepted-only BIC scores, this is a one-line change (filter `bic_scores` to `candidates`'
  keys) — flagged under Map Impact above.
- `soft_class_membership` returns the single-row posterior as a 1-D `(k,)` array
  (`posterior_membership(...)[0]`), not the 2-D `(1, k)` row — the handoff explicitly offered
  either ("your call, document it"); chosen for ergonomic single-sample use
  (`membership.sum()` reads naturally without an axis argument) and documented in the method's
  docstring.
- The support-floor fallback re-fits a fresh `GaussianMixture(n_components=1, ...)` rather
  than reusing any k=1-adjacent computation — there is no k=1 in the normal `k_range` sweep
  (`k_range` starts at 2 per the handoff's default `(2, 6)`), so this is the only place k=1 is
  ever fit; it is fit on the same standardized descriptors as every other candidate.
- Test fixtures (`_make_blobs` counts/stds/means) were chosen and iterated to make the
  thin-blob support-floor scenario deterministic under the fixed `MIN_COMPONENT_WEIGHT_FRAC =
  0.05`, per the handoff's Authority section — the constant's value was never adjusted; only
  the synthetic fixture shapes were tuned to exercise it.

## Stop conditions hit
None — `segment_classifier.py`'s actual structure matched the handoff's description exactly
(verified at m0-context); no scope-exceeding decision was needed; all required evidence was
producible and is included above.

## Out-of-scope observations
None beyond the Map Impact/Assumptions items above (both are documented choices within the
handoff's explicit "your call" latitude, not new out-of-scope findings).

## Workflow Feedback
- **Handoff gaps:** none material. Two points were explicitly left as "your call, document
  it" (regimes-set-shaped `bic_scores` scope; 1-D vs 2-D single-row return) and both had a
  documentation clause, so resolving and documenting them was in-scope, not an improvisation.
- **Context rediscovered:** none beyond what the anchors already pointed at — Gate 1's
  `corner_descriptors.py` (read for import/docstring-style consistency, as the handoff itself
  suggested via the "NOTE this is a DIFFERENT unit convention" callout) was sufficient context
  to get the `GRAVITY_MS2` division direction right on the first attempt.
- **Instructions improvised around:** none.
- **What would have made this easier:** nothing concrete to flag — the handoff's unit-
  convention warning (radius/lateral_g direction differing between `corner_descriptors.py` and
  `segment_classifier.py`) was precise enough to implement directly without needing to
  cross-check `corner_descriptors.py`'s docstring a second time.

## Return status
`complete`
