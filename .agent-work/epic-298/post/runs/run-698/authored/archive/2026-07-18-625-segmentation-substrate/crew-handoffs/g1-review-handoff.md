# Reviewer Handoff

## Gate
g1 (execute.json: g1-review)

## Survey State Location
`.agent-work/625-segmentation-substrate/g1-review/review.json`

## What Was Implemented
`src/physics/layer2/arcs.py`'s `_contiguous_runs` generalized to accept a `regimes: set[str]`
parameter (was hardcoded to the brake regime); new `StraightArc` dataclass +
`identify_straight_arcs` mirroring `BrakingArc`/`identify_braking_arcs`; new
`src/physics/layer2/corner_descriptors.py` module (`bin_row_to_descriptor`,
`descriptors_from_frame`) computing a lateral-g/radius descriptor axis from
`grip_bin_obs`-shaped rows.

## How to Inspect the Diff
Worktree `C:/Programs/f1-625` (branch `feat/625-segmentation-substrate`) — inspect the
UNCOMMITTED working tree, not `git diff main...HEAD`: run `git status --porcelain` then
`git diff` (not `--name-only`, to see untracked new-file content too via `git diff --stat`
plus reading the new files directly since `git diff` alone won't show untracked file bodies —
use `git status --porcelain` to find the new files, then `Read` them directly).

## Task Statement
Extend `arcs.py` to support a straight-arc grouper mirroring the existing braking-arc pattern,
and add a lateral-g/radius descriptor-axis module, per CONVERGED_PLAN.md Gate 1
(`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/CONVERGED_PLAN.md`).

## Close Criteria
- `_contiguous_runs` generalized to accept a `regimes` set (NOT duplicated into a second
  implementation) — verify `identify_straight_arcs` and `identify_braking_arcs` both call the
  SAME function.
- `identify_braking_arcs`'s public call signature is byte-identical to before this gate —
  verify by confirming all 3 pre-existing `test_arcs.py` cases pass UNMODIFIED (diff those
  specific test functions against what they must have looked like before — if you can't see
  git history in this worktree easily, at minimum confirm they exist, are unchanged in
  intent/assertions, and pass).
- `StraightArc` fields (`sample_indices`, `length_m`, `duration_s`, `top_speed_ms`) match the
  handoff's spec and are computed correctly — spot-check one hand-computable case yourself
  (pick a `test_corner_descriptors.py` or `test_arcs.py` fixture and hand-verify the number).
- `bin_row_to_descriptor` computes `radius_m = v_mean**2 / (mu_lat_p90 * GRAVITY_MS2)` and
  treats `mu_lat_p90` as ALREADY in g-units (no re-division by G) — verify against
  `src/physics/layer2/grip_bin_obs.py`'s own docstring/`lap_bin_observations` code
  (`mu_lat = a_lat / G`) yourself, don't just trust the implementer's claim.
- Guards on non-positive/NaN `mu_lat_p90`/`v_mean` behave as documented (raises `ValueError`
  per the implementer's stated choice) and are tested.
- `descriptors_from_frame` drops (not errors on) bad rows.

## Allowed Scope
`src/physics/layer2/arcs.py`, `src/physics/layer2/corner_descriptors.py`,
`tests/unit/physics/layer2/test_arcs.py`, `tests/unit/physics/layer2/test_corner_descriptors.py`.

## Specific Exclusions
`segment_classifier.py`, any DB file, `circuits.yaml`, any production default — confirm none
of these appear in `git status --porcelain`.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import` — grep the two new/changed src files for
  `evo_predictor`/`latent_power`/`compound_prior`; expect zero matches.
- No re-division of `mu_lat_p90` by G (see Close Criteria above).

## Map Anchors (inbound)
- **Structural:** `struct:physics.layer2` — `src/physics/layer2/arcs.py` (existing
  `BrakingArc`/`identify_braking_arcs` pattern, generalized not duplicated);
  `src/physics/layer2/grip_bin_obs.py` (read-only reference, unmodified — confirm it wasn't
  touched).
- **Capability:** straight-as-first-class-segment grouping (new); lateral-g/radius descriptor
  axis (new).
- **Constraints/assumptions:** `constraint:physics_region_no_evo_import`.
- **Evidence expectations:** `_contiguous_runs` is the SINGLE grouping implementation both
  arc functions call — this is the specific thing to verify, not just "tests pass."

## Evidence Produced
See `C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g1-implement-result.md`
for the implementer's full claimed evidence (16/16 tests pass, before/after diff of
`_contiguous_runs`, simplification_limits PASS). Independently re-run everything yourself —
do not trust the pasted transcript. Target postcondition: `g1-integrate.c1` (test command) and
`g1-integrate.c2` (this review-result's verdict).

## Suggested Model Tier
Simple bounded.

## Stop Conditions
Stop and return BLOCK if: the diff cannot be accessed, evidence is absent or unreproducible,
or `identify_braking_arcs`'s real callers show a behavior change you can't reconcile with
"byte-identical."

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback. Write it to
`C:/Programs/f1-625/.agent-work/625-segmentation-substrate/crew-handoffs/g1-review-result.md`
before ending your turn, and also return it as your final assistant text response.
