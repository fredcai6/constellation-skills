# Implementer Handoff — G5 Addendum (two Admiral-ruled additions before close)

## Gate
`g5` (rework of already-built base work — read the base implementer's result first:
`.agent-work/629-feature-view/g5-implementer-result.md`)

## Context
The base G5 gate (composer + read API + import-boundary/e2e tests) is built and its own
verification is green. Two additional requirements were ruled by the Admiral (team-lead) after
reviewing the plan and must land before this gate closes. Both are described precisely below —
do not re-derive the design, carry it exactly.

## Addition 1 — Reserved transition-σ widening (Admiral ruling, verbatim reasoning)

**Rule:** `SESSION_ORDER`'s last entry (`"Q"`, via `SESSION_ORDER[-1]`) is the terminal/target
session. When `build_feature_view_row`'s `as_of_session` is NOT the terminal session (i.e.
`"FP1"`/`"FP2"`/`"FP3"`), the composite is standing in for a not-yet-observed Q reading across
one or more un-modeled process-noise links (`CarBasisPosteriorRecord.process_noise_link`,
reserved per G3) — the composite's σ must HONESTLY WIDEN to cost that, via the SAME
`effective_axis_sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC` machinery already used everywhere else in
this epic, not a fabricated magnitude. When `as_of_session == "Q"` (the terminal session),
there is no forward transition — no extra widening.

**Do NOT scale by number of hops or time-to-Q** (e.g. FP1-to-Q spans 3 links, FP3-to-Q spans
1 — both get the SAME flat widening, never a bigger one for FP1). Scaling the term by
hop-count or clock-distance IS the real modeling work #654 (the filed follow-on issue) will
eventually do — this gate's widening is a flat reserved-unresolved floor, nothing more.

**Mechanical implementation (reuses existing machinery, does not invent new math):**
For every axis in the composed `axis_sigma` dict, when `as_of_session != SESSION_ORDER[-1]`:
```python
transition_widened = effective_axis_sigma(value, sigma, "unresolved")
axis_sigma[axis] = max(sigma, transition_widened) if transition_widened is not None else sigma
```
(call `effective_axis_sigma` from the SAME import `store.py` already uses — the call passes
`"unresolved"` EXPLICITLY regardless of the axis's own already-resolved/unresolved status on
its source row; this is a DIFFERENT, independent reason to widen, not a re-check of fit
quality.) Use `max()` so this never NARROWS an already-wider sigma from some other source.

**Kept separable (Admiral's explicit requirement — this must be inspectable, not silently
folded away):** Add ONE new field to `FeatureViewRow`
(`src/physics/feature_view/records.py`, G1's dataclass) — this is a small, ADDITIVE,
backward-compatible schema extension (a new field WITH a default, so every existing caller/test
that constructs a `FeatureViewRow` without it keeps working unchanged):

```python
transition_axis_status: dict = field(default_factory=dict)
```

Semantics: for EVERY axis present in `axis_sigma`, `transition_axis_status[axis] = "unresolved"`
when that axis was transition-widened (i.e. `as_of_session != SESSION_ORDER[-1]`), else
`"resolved"` (mirrors the `axis_status` vocabulary already used on `WeekendStateRecord`/
`CarBasisPosteriorRecord` — reuse "resolved"/"unresolved" literally, do not invent new labels).
Populate this dict for every axis, not just the widened ones, so a consumer can tell "this axis
carries no reserved transition cost" apart from "this axis was never checked."

This is the ONE place this gate touches G1's `records.py` — additive only (a new defaulted
field), does not change any existing field's meaning, and G1's own existing tests must still
pass unchanged after this addition (re-run `tests/unit/physics/feature_view/test_records.py`,
`test_store.py`, `test_append_only_contract.py`, `test_as_of_leakage.py` to confirm — all four
predate this field and must not need any edit themselves). `store.py`'s `_FEATURE_VIEW_ROW_COLS`
enumeration is derived from `FeatureViewRow.__dataclass_fields__` automatically, and
`_FEATURE_VIEW_ROW_JSON_COLS` needs `transition_axis_status` added to its tuple (it's a dict,
serialized as JSON like the other dict fields — mirror `axis_sigma`'s own entry there exactly).

**Tests to add:**
- As-of `"Q"`: `transition_axis_status[axis] == "resolved"` for every axis, and `axis_sigma`
  values are UNCHANGED from the source row (no widening applied).
- As-of `"FP1"` (or any non-terminal session): `transition_axis_status[axis] == "unresolved"`
  for every axis, and each axis's `axis_sigma` is `>=` the source row's own sigma for that axis
  (widened or unchanged-if-already-wider, via the `max()` rule — construct a case where the
  source sigma is ALREADY wider than `UNRESOLVED_AXIS_SIGMA_FRAC * abs(value)` and confirm it
  is NOT narrowed).
- Confirm the flat-widening claim: as-of `"FP1"` and as-of `"FP3"` for the SAME entity/axis
  produce the SAME widened sigma magnitude when their SOURCE sigmas are equal (proving no
  hop-count/distance scaling snuck in).
- Re-run the full `tests/unit/physics/feature_view` suite — must stay green, including the
  four G1 tests that predate this field.

## Addition 2 — Forward-looking evo-side import-boundary test

**Rule (Admiral):** the existing `test_no_evo_import_anywhere_in_the_whole_package` test
enforces `constraint:physics_region_no_evo_import` in ONE direction (this package never imports
evo). Add the REVERSE, forward-looking direction: a future `src/evo_predictor/` module may
import from this package ONLY via `from src.physics.feature_view.read import read_feature_view`
(or an equivalent import of exactly that symbol from exactly that module) — never `store.py`,
`records.py`, `build_*.py`, or anything under `src/physics/layer2/` directly. This pre-empts the
same boundary-drift shape `regime_readiness.py` already exhibits against `estimate_store.
_cov_list` (a documented existing precedent in this repo — cite it in your test's docstring as
the shape being guarded against).

No `src/evo_predictor/` file imports anything from this package or from `src.physics.layer2`
today — the test is VACUOUSLY TRUE right now and exists purely to trip the moment #630 (or any
future work) adds a bad import.

**Mechanical implementation:** a test (e.g. `tests/unit/physics/feature_view/
test_evo_import_boundary.py`) that:
1. Enumerates every `.py` file under `src/evo_predictor/` (recursively).
2. For each file's source text, checks for any substring reference to `src.physics.feature_view`
   or `src.physics.layer2` (or their relative-import equivalents, e.g. `from ...physics.layer2`
   — a plain substring scan for `physics.feature_view`/`physics.layer2` is sufficient; do not
   over-engineer an AST resolver for this).
3. Where such a reference exists, assert the ONLY sanctioned form is a line matching
   `from src.physics.feature_view.read import read_feature_view` (or `import
   src.physics.feature_view.read` used as `.read_feature_view`) — anything else (a `layer2`
   reference, a `feature_view.store`/`feature_view.records`/`feature_view.build_*` reference)
   fails the test with a message naming the offending file and the disallowed import.
4. Where NO such reference exists in a file (today's universal case), that file passes
   trivially — the test's overall assertion is "zero violating imports found," and it must
   emit the count of `evo_predictor` files scanned (a sanity check mirroring
   `test_import_boundary.py`'s own vacuous-check guard: assert the scanned file count is
   non-trivial, e.g. `>= 10`, so an empty/near-empty `evo_predictor` directory wouldn't make
   the assertion vacuous by accident).

## Allowed Scope (this addendum)
- `src/physics/feature_view/records.py` — ONE additive field on `FeatureViewRow`
  (`transition_axis_status`) only. No other change to this file.
- `src/physics/feature_view/store.py` — add `transition_axis_status` to
  `_FEATURE_VIEW_ROW_JSON_COLS`. No other change.
- `src/physics/feature_view/build_feature_view.py` — the widening logic in
  `build_feature_view_row`.
- New test file(s) under `tests/unit/physics/feature_view/`.

## Specific Exclusions
Do not touch `build_weekend_state.py`, `build_car_basis.py`, `build_lap_evidence.py`, or any
other existing field on any record. Do not modify `read.py`'s existing behavior (it already
passes `transition_axis_status` through generically via `store.load_feature_view_rows`'s JSON
deserialization — confirm this, don't hand-add a new parameter to `read_feature_view`).

## Constraints
- `constraint:physics_region_no_evo_import`.
- The new `FeatureViewRow` field must be additive/defaulted — no existing construction call
  anywhere in the codebase may break.
- No fabricated widening magnitude beyond `effective_axis_sigma`'s own existing
  `UNRESOLVED_AXIS_SIGMA_FRAC` constant — do not invent a new constant.

## Required Evidence
- Full pytest output for the whole `tests/unit/physics/feature_view` suite (must stay green,
  including all four G1 tests unchanged).
- A concrete before/after example: the SAME entity's axis_sigma at as-of `"FP1"` vs as-of
  `"Q"`, showing the FP1 reading widened and the Q reading unchanged.
- The flat-widening proof (FP1 vs FP3 giving the same widened magnitude for equal source sigmas).
- The evo-side import-boundary test's scanned-file-count sanity assertion output.
- `simplification_limits --paths src/physics/feature_view` clean.

## Verification Commands

```bash
export PATH="/c/Users/fredc/AppData/Local/Microsoft/WindowsApps:$PATH"
py -m pytest tests/unit/physics/feature_view -q
py -m src.utils.simplification_limits --paths src/physics/feature_view
```

## Suggested Model Tier
Simple bounded — both additions are fully mechanical, precisely specified above.

## Authority
Both additions are Admiral-ruled and fully specified here — do not re-decide the design. If
implementing either forces a real magnitude/scaling choice beyond what's specified (Admiral's
own stop condition), STOP and report as a blocker rather than inventing one.

## Stop Conditions
Stop and return if: `FeatureViewRow`'s field addition breaks any existing construction call
site (name it, do not silently patch every call site without flagging it first if there are
many); implementing the widening forces a real magnitude/scaling choice not covered above.

## Return Format
Return IMPLEMENTER_RESULT (append to the existing g5-implementer-result.md or write a new
addendum result file — your choice, name it clearly): completed slice, files changed, evidence
produced, assumptions used, stop conditions hit, workflow feedback.
