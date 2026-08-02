# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g5` (final gate, base + addendum) — closes epic #629

## Result
`APPROVE`

## Handoff compliance
Both the base gate (composer + read API + import-boundary/sole-surface/e2e tests) and the addendum
(reserved transition-sigma widening + forward evo-import-boundary test + the `read.py` round-trip
fix) do what their handoffs asked, within allowed scope. All close criteria independently
reconstructed with fresh cases (not just re-reading the implementer's own tests):

- **Primary/refinement precedence** (Case 1/2 in my scratch probe): a resolved `car_basis_posterior`
  value (7.77, sigma 0.01) survives an unresolved `weekend_state` axis untouched; the reverse — a
  resolved `weekend_state` value (3.33) — overrides a resolved `car_basis` value; confirmed
  per-axis (a second, weekend_state-unresolved axis survives from car_basis at 42.0 in the same row).
- **`circuit_conditional_composite`**: grepped `build_feature_view.py` — the only assignment is the
  literal `None` in the `FeatureViewRow(...)` construction. Always `None`.
- **σ-widening (addendum)**: as-of `"Q"` → no widening, `transition_axis_status[axis]=="resolved"`
  (Case 3). As-of `"FP1"` → widens to `UNRESOLVED_AXIS_SIGMA_FRAC * abs(value)`,
  `transition_axis_status[axis]=="unresolved"` (Case 4). `max()` never narrows an already-wider
  source sigma (50.0 stays 50.0 against a reserved floor of 10.0, Case 5). FP1-cutoff and FP3-cutoff
  against the identical source sigma produce IDENTICAL widened magnitude (Case 6) — proving the
  widening is flat, not scaled by hop-count (FP1→Q spans 3 links, FP3→Q spans 1) or clock distance,
  per the Admiral's explicit "keep it simple" ruling. Traced the mechanism to source:
  `effective_axis_sigma`/`UNRESOLVED_AXIS_SIGMA_FRAC` (=1.0) in `estimate_store_fields.py` take only
  `(value, sigma, status)` — no session-distance parameter exists to smuggle scaling into.
- **`read.py` fix**: reproduced the `transition_axis_status` round-trip with a fresh two-axis case
  (Case 7) distinct from the implementer's own regression test — confirmed it survives
  `read_feature_view` reconstruction.
- **Forward import-boundary test's bite**: called the test module's own `_GUARDED_SUBSTRINGS`/
  `_line_is_sanctioned` primitives directly against 6 independent synthetic disallowed-import
  strings (direct `store.py`/`records.py`/`build_feature_view.py` reach-through, `layer2` direct +
  relative-import reach-through, qualified-module-attribute reach-through) — all 6 correctly
  flagged, without touching any real `src/evo_predictor/` file. The primary protection direction
  (would it catch a bad import) is real, not vacuous theater.
- `py -m pytest tests/unit/physics/feature_view -q` → **85 passed in 2.35s**, reproduced fresh,
  matching the addendum result's claimed count exactly.
- `simplification_limits --paths src/physics/feature_view` → **PASS (8 files checked)**, reproduced.

## Scope drift
None. Only `src/physics/feature_view/{records.py, store.py, build_feature_view.py, read.py}` and
`tests/unit/physics/feature_view/` are touched. Confirmed via `git diff main` that
`src/physics/layer2/`, `src/physics/weekend_state/`, `src/physics/mass_model.py` (Specific
Exclusions) have zero diff — untouched. `git status` shows only untracked new paths, no modified
tracked files outside scope. (The repo's `docs/architecture/*` shows as differing from `main`, but
`git log`/`merge-base` confirm this branch is one commit BEHIND `main` — a docs-reconcile commit
`main` picked up after this branch's base — not new work from this branch.)

## Evidence verdict
Required evidence present and independently reproduced (see Handoff compliance above); test mode
was test-after for the addendum per its own "Simple bounded / fully mechanical" model-tier framing
(no TDD red-capture required by that handoff) and TDD for the base gate. `read.py`'s sole-surface
contract (`__all__ == ["read_feature_view"]`) reproduced directly via a fresh import, independent of
the test file.

**One evidence gap, non-blocking**: `g5-implementer-result.md` (the base implementer's result file)
is referenced by the reviewer handoff, the addendum handoff, `crew-runs.json`, and `execute.json`,
but is genuinely **absent from disk** (confirmed via directory listing and `find`). The underlying
work is real and independently re-verified via `g5-implementer-plan.json`'s attestation trail (6
`why` entries covering milestones m1–m6, each naming concrete test counts and behavior) plus direct
source/test inspection — this review does not rest on the missing file's claims, only on what I
reproduced myself. Flagged under Workflow Feedback.

## Code/doc quality
Docstrings are extensive and used to record real design decisions (the precedence rule, the
reserved-field rationale, the constructor-grain approximation), consistent with `global-crew.md`'s
"document a real design decision" expectation — not confusion-masking.

**Fowler refactoring pass** (r6-fowler, recorded to `g5-review/fowler_pass.json`,
`verify_fowler_pass.py` exits 0): 12/12 baseline smells visited. 8 absent (long-method, large-class,
feature-envy, shotgun-surgery, divergent-change, message-chains, speculative-generality,
comments-as-deodorant). 4 overridden with a logged repo-standard + reason each, no smell flagged as
a genuine defect:
- **duplicated-code** — the four near-identical `insert_X`/`load_X` wrapper pairs in `store.py`
  mirror the project's own documented `fit_store.py`/`wear/store.py` precedent (cited in `store.py`'s
  own module docstring); the real duplication (SQL/JSON-serialization logic) is already factored
  into the shared generic `_insert`/`_load` helpers every wrapper delegates to.
- **data-clumps** / **long-parameter-list** — the `(year, gp_name, constructor, as_of_session,
  model_version)` natural-key tuple threaded positionally through `build_feature_view_row`/
  `read_feature_view` is G1's own established signature shape (`load_as_of` already fixed it),
  carried forward, not a new pattern this gate introduced; forking it into a value object for 2 of N
  package functions would be exactly the speculative abstraction `global-crew.md`'s
  "no speculative abstraction" rule warns against.
- **primitive-obsession** — bare-`str` session/constructor identifiers and axis-keyed dicts are an
  explicit, documented design choice (`records.py`'s own docstring: configurable axis list, not a
  hardcoded schema; fail-visible `session_ordinal` validation) rather than an unexamined default.

## Map impact verdict
- **Evidence supports claimed change:** yes — the addendum's claimed behavior (honest σ widening,
  inspectable `transition_axis_status`) and the `read.py` fix are both independently reproduced.
- **Constraints not violated:** yes — `constraint:physics_region_no_evo_import` reinforced (now
  bidirectional); no fabricated widening magnitude (traced to the existing
  `UNRESOLVED_AXIS_SIGMA_FRAC` constant, no new one introduced); `FeatureViewRow`'s new field is
  additive/defaulted (verified by constructing a row without naming it).
- **Notes match the diff:** yes.
- **Decision candidates surfaced:** yes — `struct:physics.feature_view` as a new sibling component is
  explicitly named as Admiral-ratified in both handoffs, with an explicit "record this at reconcile"
  instruction to Commander.
- **Durable context routed:** yes — `#654` (the real hop-count/distance-scaling modeling follow-on)
  is named as the filed follow-on issue in both the addendum handoff and `build_feature_view.py`'s
  own inline comment.

## Reconciliation check
`struct:physics.feature_view` does not yet appear anywhere in `docs/architecture/index.md` or
`docs/architecture/packets/physics.md` (grepped, zero hits) — a real divergence Commander must
reconcile at closeout. Not a defect of this gate: the surfacing obligation is already met (both
handoffs explicitly flag it as a decision anchor for Commander's reconcile step), and reconciling it
is Commander's job, not this gate's code.

## Blockers
- none

## Out-of-scope observations
- **Import-boundary test's second sanctioned form is under-tested against itself (non-blocking).**
  The addendum handoff and the test's own docstring both claim TWO sanctioned import forms: `from
  src.physics.feature_view.read import read_feature_view` and `import
  src.physics.feature_view.read` "used as `.read_feature_view`". I constructed a synthetic 2-line
  case reproducing the second form exactly (`import src.physics.feature_view.read` on line 1, then
  `src.physics.feature_view.read.read_feature_view(...)` used on line 2) via the test module's own
  `_GUARDED_SUBSTRINGS`/`_line_is_sanctioned` primitives: line 2 is FALSELY flagged as an offender,
  because `_line_is_sanctioned` only recognizes the import-statement line itself, not a subsequent
  qualified-attribute usage line that also contains the guarded substring `"physics.feature_view"`.
  This is over-strict, not under-strict — it would block a legitimate future use of the second
  sanctioned form, but it never lets a real disallowed import through, so
  `constraint:physics_region_no_evo_import` is not compromised in the dangerous direction, and the
  vacuously-true-today test has zero effect on current behavior. `read.py`'s own docstring already
  steers future callers to the `from ... import read_feature_view` form in practice, so this gap is
  unlikely to bite — flagging as a triage candidate for a small follow-up fix (either drop the
  second sanctioned form from the docstring/handoff claim, or special-case usage lines that begin
  with the already-sanctioned import's bound name).
- **Layer2/weekend_state regression slice (959 tests, commander's background run)** had NOT
  completed as of this review's completion (~80% through, zero failures observed in the visible
  tail of `layer2-regression.output`) — per the handoff this is not a personal close criterion, noted
  here for Commander's awareness at closeout.

## Workflow Feedback
- **Handoff gaps:** `g5-implementer-result.md` is cited by name in the reviewer handoff, the
  addendum handoff, `crew-runs.json`, and `execute.json`, but is genuinely absent from disk — a
  broken evidence pointer. Worth either regenerating it from the plan.json attestation trail before
  the next reviewer dispatch, or correcting the handoff to point at the plan.json trail directly.
- **Context rediscovered:** none beyond normal source reading — the addendum handoff's mechanical
  snippet and the module docstrings were sufficient without re-deriving any design.
- **Instructions improvised around:** the handoff's close criterion "call the scan function directly
  against a synthetic string" assumed the import-boundary test exposes a standalone per-file scan
  function; it doesn't (the offender-detection loop is inline in the test body). I instead imported
  the test module's own `_GUARDED_SUBSTRINGS`/`_line_is_sanctioned` primitives and re-implemented the
  identical loop against synthetic text in a scratch script — functionally equivalent, and this is
  exactly what surfaced the second-sanctioned-form false-positive gap above.
- **What would have made this easier:** fixing the missing `g5-implementer-result.md` before
  dispatch would have removed the one gap this run had to route around by reconstructing evidence
  from the plan.json trail instead.

## Return status
`complete`
