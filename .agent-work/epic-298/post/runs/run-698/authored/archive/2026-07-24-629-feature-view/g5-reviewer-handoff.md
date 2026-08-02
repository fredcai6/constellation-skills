# Reviewer Handoff — G5 (final gate)

## Gate
`g5`

## Survey State Location
`.agent-work/629-feature-view/g5-review/review.json`.

## What Was Implemented
Base: `src/physics/feature_view/build_feature_view.py` (`build_feature_view_row` — primary
car-basis source / weekend-state-refinement precedence, reserved `circuit_conditional_
composite`) and `read.py` (`read_feature_view`, sole evo-facing surface). Plus import-boundary,
sole-surface, and end-to-end tests re-proving G1's two protected properties on real G2/G3-
composed data.

Addendum (Admiral-ruled, added after the base build): `FeatureViewRow` gained an additive
`transition_axis_status: dict` field; `build_feature_view_row` now applies a flat,
non-scaling sigma widening (via `effective_axis_sigma(value, sigma, "unresolved")`, `max()`
against the existing sigma) whenever `as_of_session != SESSION_ORDER[-1]` ("Q") — the composite
is standing in for an un-modeled process-noise link toward the terminal session, and its sigma
must honestly cost that. A NEW forward-looking test
(`tests/unit/physics/feature_view/test_evo_import_boundary.py`) scans all `src/evo_predictor/`
files (118 today) asserting the ONLY sanctioned import from this package is
`from src.physics.feature_view.read import read_feature_view` — vacuously true today, designed
to trip the moment a future evo module reaches past `read.py` (the exact
`regime_readiness.py`->`estimate_store._cov_list` boundary-drift shape, pre-empted).

Commander-applied fix (found by the addendum crew, excluded from its own scope by the
handoff's own file-touch restriction, applied directly + regression-tested): `read.py`'s
`read_feature_view` was NOT passing `transition_axis_status` through on reconstruction — a real
bug that would have silently hidden the reserved-transition tag from the ONE surface that
matters. Fixed (1-line addition) with a new regression test,
`test_transition_axis_status_survives_the_read_round_trip`.

## How to Inspect the Diff
Uncommitted working tree, `C:/Programs/f1-629`, branch `feat/629-feature-view`. Read
`build_feature_view.py`, `read.py`, `records.py` (the one new field), `store.py` (the one new
JSON-column entry), and all new/changed test files directly.

## Task Statement
Full detail: `.agent-work/629-feature-view/g5-implementer-handoff.md` (base) and
`.agent-work/629-feature-view/g5-addendum-handoff.md` (addendum). Full evidence:
`.agent-work/629-feature-view/g5-implementer-result.md`,
`.agent-work/629-feature-view/g5-addendum-result.md`.

## Close Criteria
- **Primary/refinement precedence** (base): construct a case yourself where car_basis is
  resolved and weekend_state is unresolved for the same axis on the same row — confirm
  car_basis survives; and the reverse (weekend_state resolved, overrides) — confirm it wins.
  Confirm the override is per-axis (a second axis left untouched).
- **`circuit_conditional_composite`** always `None` — confirm no code path sets it.
- **σ-widening (addendum)**: construct your own case at as-of `"Q"` (must NOT widen,
  `transition_axis_status[axis] == "resolved"`) and as-of a non-terminal session (MUST widen,
  `transition_axis_status[axis] == "unresolved"`, sigma `>=` source). Construct a case where the
  source sigma is ALREADY wider than the flat widening floor and confirm it is NOT narrowed
  (the `max()` rule). Construct two as-of cutoffs (e.g. `"FP1"` and `"FP3"`) against the SAME
  equal source sigma and confirm the widened magnitude is IDENTICAL — proving no hop-count or
  clock-distance scaling was smuggled in (Admiral's explicit "keep it simple" requirement).
- **The `read.py` fix**: confirm `transition_axis_status` now round-trips through
  `read_feature_view` (reproduce the new regression test yourself with a fresh case, not just
  reading the implementer's test).
- **Forward import-boundary test**: confirm it scans a real, non-trivial file count (should be
  ~100+ files under `src/evo_predictor/`); confirm it would actually FAIL if you added a
  disallowed import (construct one in a scratch copy, do not edit real `src/evo_predictor/`
  files, and confirm the test's logic would catch it — e.g. call the scan function directly
  against a synthetic string).
- No `src.evo_predictor` import in the whole `feature_view` package (already covered by
  `test_import_boundary.py`, reproduce it).
- `read.py`'s sole-surface contract (`__all__ == ["read_feature_view"]`) still holds.
- Constructor-grain approximation documented (not silently assumed) — confirm the docstring
  states it explicitly.
- `py -m pytest tests/unit/physics/feature_view -q` green — reproduce count (85 expected:
  27+6+15+9+ ... the running total across all 5 gates + addendum + the read.py fix's new test).
- `simplification_limits --paths src/physics/feature_view` clean.
- **Regression slice** (`tests/unit/physics/layer2 tests/unit/physics/weekend_state -q`): the
  commander is running this separately in the background (a 959-test suite, long-running) —
  you do NOT need to re-run it yourself; note in your result whether the commander's run had
  completed by the time you finished, if known, but do not treat it as a close criterion you
  must personally satisfy.

## Allowed Scope
Everything under `src/physics/feature_view/` and `tests/unit/physics/feature_view/` — this is
the final gate, review the whole component's end state, not just this gate's diff in isolation.

## Specific Exclusions
`src/physics/layer2/`, `src/physics/weekend_state/`, `src/physics/mass_model.py` are read-only
consumers — confirm untouched.

## Constraints the Implementation Must Respect
- `constraint:physics_region_no_evo_import`.
- `read.py` is the sole evo-facing surface, in both directions now (feature_view doesn't
  import evo; a future evo module may only import `read_feature_view`).
- No fabricated widening magnitude — only `effective_axis_sigma`'s existing
  `UNRESOLVED_AXIS_SIGMA_FRAC`.
- `FeatureViewRow`'s new field is additive/defaulted (no existing call site broke).

## Map Anchors (inbound)
- **Structural:** `struct:physics.feature_view` (the whole component, closing out).
- **Capability:** the as-of-stamped feature view — THE evo-facing surface, now
  bidirectionally boundary-tested.
- **Constraints:** `constraint:physics_region_no_evo_import`.
- **Decision anchors:** `struct:physics.feature_view` as a new sibling component — RATIFIED by
  the Admiral this run (was initially floated as a design-it-twice candidate vs. a layer2-
  embedded hybrid); record this at reconcile. The reserved `process_noise_link`/
  `parc_ferme_step` (G3) and the σ-widening's own reserved framing — both explicit-unknown,
  never fabricated; #654 filed as the modeling follow-on.
- **Evidence expectations:** append-only + as-of leakage re-verified on real composed data;
  σ-widening's flat/non-scaling property; DB-only / bidirectional sole-read-surface.

## Evidence Produced
See `.agent-work/629-feature-view/g5-implementer-result.md` and
`.agent-work/629-feature-view/g5-addendum-result.md`. Commander independently re-ran the
full feature_view suite after each stage (76 -> 84 -> 85 passed) and applied + tested the
`read.py` fix directly.

## Suggested Model Tier
Stronger (Sonnet) — this is the culminating gate closing out a 5-gate epic; the σ-widening's
flat-not-scaled property and the forward import-boundary test's actual bite are both worth
genuine adversarial verification, not a surface read.

## Stop Conditions
Stop and return BLOCK if: the precedence rule is wrong; σ-widening scales with hop-count/
distance (violates the Admiral's explicit "keep it simple" ruling); the forward import test
would not actually catch a disallowed import; `read.py` still drops any field; evidence is
unverifiable.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.
