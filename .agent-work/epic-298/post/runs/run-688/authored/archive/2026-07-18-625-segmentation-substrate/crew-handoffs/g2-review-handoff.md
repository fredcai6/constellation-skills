# Reviewer Handoff

## Gate
g2 (execute.json: g2-review)

## Survey State Location
`.agent-work/625-segmentation-substrate/g2-review/review.json`

## What Was Implemented
New `src/physics/layer2/property_mixture.py`: BIC-selected, support-floored Gaussian mixture
(`MIN_COMPONENT_WEIGHT_FRAC=0.05`) over standardized `(radius, lateral_g)` descriptors
(`fit_property_mixture`, `posterior_membership`, `MixtureFit`). One additive method
`SegmentClassifier.soft_class_membership` in `src/physics/segment_classifier.py`.

## How to Inspect the Diff
Worktree `C:/Programs/f1-625` — uncommitted working tree. `git status --porcelain` then
`git diff` for tracked-file changes; `Read` the new files directly (untracked, won't show in
`git diff` body). Gate 1's changes (`arcs.py`, `corner_descriptors.py`, their tests) are
ALREADY landed and approved — do not re-review them, only Gate 2's slice:
`property_mixture.py` (new), `segment_classifier.py` (diff only), the two test files' diffs.

## Task Statement
Build the soft/fractional corner property-class mixture and an additive
`SegmentClassifier.soft_class_membership` method, per CONVERGED_PLAN.md Gate 2
(`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/CONVERGED_PLAN.md`) and the full
handoff at
`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g2-implement-handoff.md`.

## Close Criteria
- `MIN_COMPONENT_WEIGHT_FRAC = 0.05` is a pre-registered module constant — confirm it is NOT
  derived from or tuned against any real dataset (grep for any DB/file read in
  `property_mixture.py`; expect none).
- `fit_property_mixture` standardizes `(radius, lateral_g)` before fitting (confirm a
  scaler — e.g. `StandardScaler` — is actually applied, not just imported) and stores it in
  `MixtureFit` for reuse.
- Selection: rejects any `k` whose smallest fitted component weight is below
  `MIN_COMPONENT_WEIGHT_FRAC`, picks lowest-BIC among survivors, falls back to `k=1` (not a
  raise, not a silently-accepted rejected k) if every candidate is rejected. Independently
  verify the two cluster-recovery tests (2-cluster -> k=2, 3-cluster -> k=3) and the
  thin-blob/all-rejected fallback tests actually exercise this logic (read the test bodies,
  don't just trust green).
- `posterior_membership` rows sum to 1, reuses the STORED scaler (not a fresh fit on the
  query set) — verify by reading the implementation, this is easy to get subtly wrong.
- `segment_classifier.py`: `_classify_regime` and `physics_data_models._VALID_REGIMES` are
  BYTE-IDENTICAL to before this gate (diff the file — only an additive method should appear).
  `soft_class_membership` returns `None` for non-corner regime AND for zero/degenerate
  curvature corner samples; returns a membership array summing to 1 for a valid corner
  sample. Confirm the unit conversion: `lateral_g = sample.a_lateral / GRAVITY_MS2` (m/s² ->
  g-units) — this is a DIFFERENT input convention than Gate 1's `corner_descriptors.py`
  (which takes `mu_lat_p90` already in g-units from `grip_bin_obs`) — confirm the
  implementer did not confuse the two and accidentally double-convert or skip the conversion.

## Allowed Scope
`src/physics/layer2/property_mixture.py`, `src/physics/segment_classifier.py` (additive
only), `tests/unit/physics/layer2/test_property_mixture.py`,
`tests/unit/physics/test_segment_classifier.py` (additive only).

## Specific Exclusions
No DB I/O in this gate (Gate 1's `arcs.py`/`corner_descriptors.py` changes are OUT of this
review's scope — already approved). No `circuits.yaml`/production-default changes. No
`evo_predictor`/`latent_power`/`compound_prior` imports.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import` — grep the new/changed files.
- `MIN_COMPONENT_WEIGHT_FRAC` value must be exactly `0.05` (the handoff's frozen pre-registered
  value) — not adjusted to make a test pass.

## Map Anchors (inbound)
- **Structural:** `struct:physics` — `segment_classifier.py` (additive); `struct:physics.layer2`
  — new `property_mixture.py`.
- **Capability:** soft/fractional corner property-class membership (pre-ruling #1: mixtures
  over classes, never one-corner-one-property; support-driven class count).
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** pre-ruling #1.
- **Evidence expectations:** cluster recovery + support-floor fallback demonstrated on
  synthetic fixtures, not asserted only.

## Evidence Produced
See `C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g2-implement-result.md`
(claimed: 15/15 pass). Independently re-run — do not trust the transcript. Target
postcondition: `g2-integrate.c1` (test command), `g2-integrate.c2` (this verdict).

## Suggested Model Tier
Stronger — statistical-modeling review (BIC/support-floor correctness), not purely mechanical.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is unreproducible, or the
unit-conversion / byte-identical-regime claims don't hold up under direct inspection.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. Write it to
`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g2-review-result.md`
before ending your turn, and also return it as your final assistant text response.
