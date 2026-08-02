# Reviewer Handoff — G2 review: log-space property mixture + support-driven-k fix (#638)

## Gate
g2-review

## Survey State Location
Create your review survey at `.agent-work/638-f12-stability-rework/g2-review/review.json`
(NOT at the worktree root). Work only in the worktree `C:/Programs/f1-638`.

## What Was Implemented
Rework of the Phase-1 corner property-class mixture so the mandatory F12 held-out-circuit
stability gate can earn a genuine PASS by fixing the MODEL. Decided design + root cause are in
`.agent-work/638-f12-stability-rework/DIAGNOSIS.md`; implementer's evidence in
`.agent-work/638-f12-stability-rework/crew-handoffs/g2-implement-result.md`. Four changes:
(1) `fit_property_mixture` fits in `(log10 radius, lateral_g)` space (encapsulated `_to_log_space`,
applied in fit + `posterior_membership`); (2) support criterion = `weight>=0.05` OR
`weight*N>=150` (new frozen `MIN_COMPONENT_SUPPORT_COUNT=150`); (3) `k_range` default `(2,4)`;
(4) gate `mixture_stability.py` normalizes the radius axis by `LOG_RADIUS_SCALE=0.30` (was
`RADIUS_SCALE_M=50`), all other gate logic unchanged.

## How to Inspect the Diff
Review the UNCOMMITTED working tree of `C:/Programs/f1-638` (NOT `git diff main...HEAD`):
`cd /c/Programs/f1-638 && git status --porcelain && git diff`. Expect exactly 5 changed files:
`src/physics/layer2/property_mixture.py`, `src/physics/layer2/mixture_stability.py`,
`tests/unit/physics/layer2/test_property_mixture.py`, `.../test_mixture_stability.py`,
`scripts/f12_held_out_stability.py` (import/print/JSON-key rename only). The IMPLEMENTER_RESULT
under `.agent-work/` is Local-only (not a defect if absent from diff).

## Task Statement
Implement the commander-decided fix EXACTLY (design + 3 frozen constants are commander-owned from
real-data diagnosis, not the implementer's to substitute). Preserve F12 falsifiability.

## Close Criteria (each a review check — verify independently, do not trust the result doc)
- Fix matches DIAGNOSIS.md: log-space fit encapsulated so callers pass RAW descriptors; OR support
  criterion; `k_range` (2,4); gate uses `LOG_RADIUS_SCALE=0.30`.
- **F12 stays FALSIFIABLE — the load-bearing check.** The discriminating test
  (`TestCheckHoldoutStabilityDiscriminating` in `test_mixture_stability.py`) must still assert
  same-generator→PASS AND shifted-generator→FAIL, and must genuinely be ABLE to fail. VERIFY this
  is real, not vacuous: temporarily break the model (e.g. make `component_agreement_stat` return 0.0,
  or revert the shift in the shifted-generator fixture) and confirm the shifted/FAIL test then FAILS
  — i.e. the test actually catches instability. Restore afterward. Report what you did and saw.
- `F12_AGREEMENT_THRESHOLD` is still `1.0`; the k-mismatch→`inf` auto-fail is intact; the Hungarian
  match is intact. (Gate not weakened.)
- k stays SUPPORT-DRIVEN, not a hardcoded constant: the mechanical support-driven-k test must show k
  responds up as genuine well-supported clusters are added and down with fewer, and a genuinely tiny
  cluster (< both arms) is floor-rejected. Confirm this test would FAIL if k were pinned.
- The three new constants (`MIN_COMPONENT_SUPPORT_COUNT=150`, `k_range` ceiling 4, `LOG_RADIUS_SCALE`
  0.30) are frozen in-module with a domain-reasoned comment (not tuned to a result).
- Region unit suites green (re-run yourself, paste output):
  `py -m pytest tests/unit/physics/layer2/test_property_mixture.py tests/unit/physics/layer2/test_mixture_stability.py -q`
  and the broader `py -m pytest tests/unit/physics/layer2/ -q` (no caller regressions in
  regime_rollup / segment_classifier / corner_descriptors).
- `py -m src.utils.simplification_limits --paths src/physics/layer2/property_mixture.py src/physics/layer2/mixture_stability.py` passes.

## Allowed Scope
The 5 files above. Test files were pre-authorized to be reseeded/rewritten (the log transform
legitimately invalidates the old raw-space scenarios).

## Specific Exclusions (flag if touched)
`corner_descriptors.py`, `regime_rollup.py`, `segment_classifier.py`, `build_regime_rollup.py`
logic must be UNCHANGED (encapsulation must keep them working). No `circuits.yaml`/gold/production-
default change. No evo import in `physics.layer2` (`constraint:physics_region_no_evo_import`).

## Constraints the Implementation Must Respect
- `MixtureFit` dataclass shape unchanged; `fit.scaler` fit on log-space descriptors so
  `scaler.inverse_transform(gmm.means_)` → `(log10 radius, lateral_g)`.
- Determinism (random_state threaded).
- Run from the worktree (editable-install `.pth` trap: `import src.physics...` must resolve under
  `C:/Programs/f1-638` — pytest is cwd-safe).

## Map Anchors (inbound)
- Structural: `property_mixture.py::fit_property_mixture`, `mixture_stability.py`.
- Capability: property-mixture-fit; f12-holdout-stability.
- Constraints: support-driven k; F12 falsifiable; no evo import.
- Decision anchors: DIAGNOSIS.md fix decision; `decision:regime_readiness_rubric`.

## Evidence Produced (from IMPLEMENTER_RESULT — reproduce, do not trust)
Import guard prints worktree path; changed-file suite 23 passed; caller surface 33 passed; full
layer2 dir 685 passed; simplification_limits PASS. The REAL-DATA 5/5 F12 PASS is NOT this gate's
evidence (commander runs it in G3) — do not require it here.

## Suggested Model Tier
stronger — falsifiability verification (actively breaking the model to confirm the gate catches it)
and multi-file coherence.

## Stop Conditions
BLOCK if: the diff cannot be accessed; the discriminating test is NOT genuinely able to fail; the
gate was weakened (threshold/auto-fail changed); k is effectively hardcoded; an excluded file's
logic changed; the region suite is red for a reason other than an intended reseed.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK) to
`.agent-work/638-f12-stability-rework/crew-handoffs/g2-review-result.md`: per-check findings
(including exactly what you did to prove the discriminating test can fail, and the re-run suite
output), blockers, out-of-scope observations, workflow feedback. Also send a short summary as your
final message.
