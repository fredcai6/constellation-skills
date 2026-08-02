# Implementer Handoff

## Gate
g2 (execute.json: g2-implement)

## Task
Build the soft/fractional corner property-class mixture (`src/physics/layer2/
property_mixture.py`) and wire an additive membership method onto `SegmentClassifier`.

## Protected Intent
Corners must be represented as MIXTURES over property classes, never one-corner-one-property
(pre-ruling #1 of the governing launch order). `SegmentClassifier._classify_regime` and
`physics_data_models._VALID_REGIMES` must stay byte-identical — this is additive metadata,
not a regime-tag rename.

## Test Mode
Test-after with synthetic fixtures (project norm). Both pieces are testable in isolation:
the mixture math needs no DB, no telemetry.

## Close Criteria
- New `src/physics/layer2/property_mixture.py`:
  - Module-level constant `MIN_COMPONENT_WEIGHT_FRAC = 0.05`, defined and documented BEFORE
    any real-data fit is attempted anywhere in this codebase (Gates 3/4 will run the real
    fit later — this gate only needs the constant to exist and be honored by the selection
    logic; it must NOT be tuned by looking at real `grip_bin_obs` results, since Gate 2 has
    no access to that data path — this is a hard constraint, not a choice).
  - `fit_property_mixture(descriptors: np.ndarray, k_range: tuple[int, int] = (2, 6),
    min_component_weight_frac: float = MIN_COMPONENT_WEIGHT_FRAC, random_state: int = 0) ->
    MixtureFit` — a small frozen dataclass/namedtuple `MixtureFit` carrying at least: the
    fitted `sklearn.mixture.GaussianMixture` (or its `means_`/`covariances_`/`weights_`
    arrays plus whatever you need to reconstruct posterior calls), the chosen `k`, the
    `StandardScaler` (or equivalent) used to standardize (radius, lateral_g) before fitting
    (mixtures are fit on STANDARDIZED features — physically radius and lateral_g have very
    different scales/units, unstandardized fitting would let radius dominate), and the BIC
    score per candidate k tried.
  - Selection logic: for each `k` in `range(k_range[0], k_range[1]+1)`, fit
    `GaussianMixture(n_components=k, random_state=random_state)` on the standardized
    descriptors; REJECT any `k` whose fitted `weights_.min() < min_component_weight_frac`
    (support-driven floor — a component nobody in the data actually needs is not a real
    class); among the surviving candidates, pick the lowest-BIC `k`. If EVERY candidate `k`
    in the range is rejected by the floor, fall back to `k=1` (a single global class — the
    honest "no support for splitting" answer) rather than raising or silently picking a
    rejected k.
  - `posterior_membership(fit: MixtureFit, descriptors: np.ndarray) -> np.ndarray` shape
    `(N, fit.k)` — each row sums to 1 (use `GaussianMixture.predict_proba` on the SAME
    standardization transform used at fit time — do not re-fit a new scaler on the query
    descriptors, reuse the stored one).
  - Both functions carry docstrings citing why standardization matters (unit mismatch
    between radius in meters, potentially large numbers, and lateral_g in g-units, roughly
    O(1)) and why the support floor exists (pre-ruling #1: class count is support-driven).
- `src/physics/segment_classifier.py`: read the current file first (a prior gate — Gate 1 —
  did NOT touch this file, so it is exactly as it was before this run started). Add ONE new
  method to `SegmentClassifier`: `soft_class_membership(self, sample: KinematicSample, fit:
  "MixtureFit") -> Optional[np.ndarray]` — import `MixtureFit`/`posterior_membership` from
  `src.physics.layer2.property_mixture` (a new, LOCAL import inside this module or at module
  top — your call, follow the existing import style in the file). Returns `None` when
  `sample.regime != "corner"`. For a corner sample, you need `(radius, lateral_g)` — the
  sample itself does NOT carry a pre-computed radius; derive it from `sample.curvature`
  (radius = `1.0 / sample.curvature` when `abs(sample.curvature) > 1e-9`, else treat as
  degenerate/return `None` — a corner-regime sample with ~zero curvature is a
  classification-boundary edge case, not a valid mixture query) and `lateral_g =
  sample.a_lateral / GRAVITY_MS2` (import `GRAVITY_MS2` from `src.physics.constants`, same
  as Gate 1's `corner_descriptors.py` — NOTE this is a DIFFERENT unit convention than
  `corner_descriptors.py`'s `bin_row_to_descriptor`, which takes `mu_lat_p90` ALREADY in
  g-units from `grip_bin_obs` — `sample.a_lateral` here is in m/s², so IT does need dividing
  by `GRAVITY_MS2`; do not confuse the two call sites). Do not modify `_classify_regime`,
  `_VALID_REGIMES`, or any other existing method/behavior.
- Do NOT wire `soft_class_membership` into `classify_samples`'s main loop (that would require
  passing a fitted `MixtureFit` through the whole classifier pipeline — out of this gate's
  scope; it stays a standalone additive method callers can invoke post-hoc when they have a
  fitted mixture, consistent with `_VALID_REGIMES` staying untouched).

## Allowed Scope
`src/physics/layer2/property_mixture.py` (new), `src/physics/segment_classifier.py` (edit,
additive method only), `tests/unit/physics/layer2/test_property_mixture.py` (new),
`tests/unit/physics/test_segment_classifier.py` (edit, additive test cases only — do not
remove or weaken any existing test).

## Specific Exclusions
No DB I/O anywhere in this gate (pure functions/synthetic fixtures only — the real
`grip_bin_obs` data is Gates 3/4's job). No changes to `circuits.yaml` or production
defaults. No `evo_predictor`/`latent_power`/`compound_prior` imports
(`constraint:physics_region_no_evo_import`).

## Constraints
- `MIN_COMPONENT_WEIGHT_FRAC = 0.05` — pre-registered NOW, before any real-data fit exists in
  this codebase (Gates 3/4 will import and reuse this exact constant, not redefine it).
- `sklearn` (1.9.0) and `scipy` (1.17.1) are already installed dependencies — use
  `sklearn.mixture.GaussianMixture` and `sklearn.preprocessing.StandardScaler` (or equivalent
  manual standardization if you prefer, but `StandardScaler` is the project-idiomatic choice
  given sklearn is already a dependency).
- `_classify_regime`/`_VALID_REGIMES` byte-identical — a reviewer will diff-check this.

## Map Anchors (inbound)
- **Structural:** `struct:physics` — `src/physics/segment_classifier.py`, module (additive
  method only); `struct:physics.layer2` — new `property_mixture.py`, module.
- **Capability:** soft/fractional corner property-class membership (new) — pre-ruling #1:
  corners are mixtures over classes, NEVER one-corner-one-property; class count
  support-driven.
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** pre-ruling #1 (soft/fractional membership, support-driven class
  count, per-corner identity deferred).
- **Evidence expectations:** BIC + min-support-floor selection demonstrated on synthetic
  2- and 3-cluster Gaussian blobs (true k recovered when clusters are well-separated; floor
  collapses selection toward fewer components on a thin/unsupported blob).
- **Map confidence flags:** none for this gate (real `grip_bin_obs` data quality is Gate
  3/4's concern, not this gate's synthetic-fixture scope).

## Deliverable Path Check
- **Committed** — `src/physics/layer2/property_mixture.py`; `git check-ignore -v` exited 1 (not ignored). New file — untracked until staged.
- **Committed** — `src/physics/segment_classifier.py`; exited 1 (not ignored).
- **Committed** — `tests/unit/physics/layer2/test_property_mixture.py`; exited 1 (not ignored). New file.
- **Committed** — `tests/unit/physics/test_segment_classifier.py`; exited 1 (not ignored).

## Required Evidence
- `py -m pytest tests/unit/physics/layer2/test_property_mixture.py tests/unit/physics/test_segment_classifier.py -v` — full output, all PASS, count of pre-existing `test_segment_classifier.py` cases before vs after (none removed).
- Synthetic 2-cluster test: assert `fit.k == 2` when generating two well-separated Gaussian blobs (e.g. means far apart relative to their spread, enough samples per cluster to clear the support floor).
- Synthetic 3-cluster test: same idea, `fit.k == 3`.
- Thin-blob test: a blob where one candidate split would create a component below `MIN_COMPONENT_WEIGHT_FRAC` — assert the selection does NOT pick that k (i.e. behaves per the floor rule).
- `posterior_membership` rows sum to 1 (`np.allclose(rows.sum(axis=1), 1.0)`).
- `SegmentClassifier.soft_class_membership` test: a corner sample returns a membership array summing to 1; a straight sample returns `None`; a zero-curvature corner-regime sample (degenerate) returns `None`.

## Verification Commands

```bash
cd /c/Programs/f1-625
py -m pytest tests/unit/physics/layer2/test_property_mixture.py tests/unit/physics/test_segment_classifier.py -v
```

## Suggested Model Tier
Stronger — genuine statistical-modeling judgment calls (BIC selection, standardization,
support-floor fallback behavior), not pure mechanical code.

## Authority
CONVERGED_PLAN.md (frozen after plan-alternatives + cold critic review) governs gate
boundaries — do not re-scope. `MIN_COMPONENT_WEIGHT_FRAC`'s VALUE (0.05) is fixed by this
handoff per the critic's pre-registration requirement — do not change it even if a synthetic
test seems to want a different number; adjust the TEST fixtures to fit the frozen constant,
not the reverse.

## Stop Conditions
Stop and return if: `segment_classifier.py`'s actual current structure doesn't match what's
described here (report the real structure); a decision outside this handoff's scope is
needed (e.g. whether to wire membership into the main classify loop — that's explicitly OUT
per Close Criteria above); required evidence cannot be produced.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence
produced, assumptions used, stop conditions hit, out-of-scope observations, workflow
feedback. Write it to
`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g2-implement-result.md`
before ending your turn, and also return it as your final assistant text response.
