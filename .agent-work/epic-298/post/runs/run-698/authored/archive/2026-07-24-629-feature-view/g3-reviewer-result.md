# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g3` — `src/physics/feature_view/build_car_basis.py`

## Result
`APPROVE`

## Handoff compliance
`build_car_basis_posterior_records(store, year, gp_name, *, model_version)` matches the
handoff's signature and intent exactly: a pure composer over `EstimateStore` rows producing
`CarBasisPosteriorRecord` rows, never writing to `EstimateStore`, never fitting anything.
All five Close Criteria were verified against source (not memory) and, where the handoff
asked for adversarial construction, via my own independent probes rather than re-reading the
implementer's tests:

1. **9-to-11 axis-status mapping** — `_STATUS_TO_AXES` in `build_car_basis.py` matches
   `estimate_store.AXIS_STATUS_NAMES` (`cda, p_max, a_b, b_b, a_t, b_t, A0, A2, theta_R`) and
   `estimate_store_fields._axis_statuses`'s own construction verbatim: `cda`→
   {`drag_area_closed_m2`, `power_drag_area_m2`}, `p_max`→{`max_power_w`}, one axis each for
   `a_b/b_b/a_t/b_t/A0/A2`, `theta_R`→{`coast_rolling_decel_ms2`, `coast_drag_area_m2`}.
   `normalize_axis_status` is applied once per status name in `_axis_status_dict` BEFORE the
   value is assigned to both governed axes — confirmed correct order (a raw `None` normalizes
   to `"unresolved"` before fan-out, not after).
2. **`cross_view_covariance` passthrough** — `fuse_dual_cda` is grep-clean in
   `build_car_basis.py`; line 209 (`row.get("cross_view_covariance")`) is a direct copy. I
   built my own `EstimateRecord` with a distinct `cross_view_covariance` dict (different
   values from the implementer's own test fixture), round-tripped it through a real
   (non-implementer) `EstimateStore`/SQLite instance, and confirmed the produced record's
   `cross_view_covariance` is dict-equal to the source AND not the same object (proves a real
   JSON deserialize round-trip, not aliasing or a coincidental re-derivation).
3. **Reserved fields never fabricated** — `build_car_basis_posterior_records`'s own signature
   has no `process_noise_link`/`parc_ferme_step` parameter, and its `CarBasisPosteriorRecord(...)`
   call site never passes either. I directly constructed a `CarBasisPosteriorRecord` with
   `process_noise_link={"leaked": True}` and separately with `parc_ferme_step={"leaked": True}`
   — both raised `ValueError` from G1's `__post_init__` guard, live-confirmed (not just read).
4. **`prior_session` nearest-present semantics** — reproduced the implementer's own
   FP1/FP2/Q(FP3-missing) case, then probed the specific edge case the handoff named as
   likely uncovered: only FP3 and Q present (no FP1/FP2). Result: `Q.prior_session == "FP3"`,
   `FP3.prior_session is None` — correct nearest-present behavior in the one case the
   implementer's 15 tests do not directly exercise.
5. **No `src.evo_predictor` import** — grep-clean in both `build_car_basis.py` and the test
   file (the test file's only occurrence is the literal search string inside
   `test_no_evo_import` itself, which is correct).

## Scope drift
None. Allowed scope was `build_car_basis.py` (new) + `test_build_car_basis.py` (new).
`git status --porcelain=v1 --untracked-files=all` shows only these two files plus the
already-existing G1/G2 untracked files in this worktree; file mtimes show G1/G2 files
(`records.py`, `store.py`, `build_weekend_state.py`, their `__init__.py`s and tests) last
touched well before G3's edit window, consistent with them being untouched. Read
`estimate_store.py`, `estimate_store_fields.py`, `cross_view.py` directly: read-only
references only, as claimed. Specific Exclusions (G1, G2 CLOSED) respected.

## Evidence verdict
All required evidence independently reproduced verbatim in this review, not accepted on the
implementer's report alone:
- `py -m pytest tests/unit/physics/feature_view -q` → **48 passed** (matches claim).
- `py -m src.utils.simplification_limits --paths src/physics/feature_view` → **PASS (5 files
  checked)**.
- `grep -rn "evo_predictor\|fuse_dual_cda" build_car_basis.py` → clean.
- `git check-ignore` on both new files → exit=1 (not ignored), as claimed.

Test mode (test-first/TDD) required; satisfied with the implementer's honestly-disclosed
deviation (the whole composer written in one coherent pass rather than three separately-red
gates) — disclosed, not hidden, and the 15 new tests exercise real behavior against a real
SQLite-backed `EstimateStore` fixture (via `tmp_path`), not stubs.

## Code/doc quality
Minimal, maintainable, matches surrounding conventions. Four handoff constraints each checked
individually (recorded as survey sub-items r4a–r4d): no-evo-import, passthrough-only,
reserved-fields-never-fabricated, tests-use-`tmp_path` — all pass. Cross-checked against
`CREW_CONTEXT.md`: no mutable module-level state, no DB singleton, missingness handled via
explicit `None`/`normalize_axis_status` (never zeroed/imputed), one canonical loading path.

**Fowler refactoring pass** (`.agent-work/629-feature-view/g3-review/fowler_pass.json`,
`verify_fowler_pass.py` exit 0): 12/12 baseline smells rendered a verdict.
- **Flagged**: `duplicated-code` — `build_car_basis.py`'s `_none_if_nan` is a near-identical
  duplicate of `build_weekend_state.py`'s `_none_if_nan` (same package). Non-blocking:
  `build_weekend_state.py` is G2/CLOSED, out of this gate's scope to fix. Logged as triage
  candidate `tc1`.
- **Overridden** (each with a logged repo standard + reason): `data-clumps` (the
  `axis_values`/`axis_sigma`/`axis_status` parallel-dict shape is G1's own documented
  convention, mirrored from `EstimateRecord`'s schema); `primitive-obsession` (bare axis-name/
  session-type strings match the codebase's established TEXT-column/tuple schema, not a new
  convention introduced here); `comments-as-deodorant` (the dense docstrings record non-obvious
  domain decisions per the project's own "Agent-facing. Dense by design." doctrine — the
  underlying logic is simple and does not itself need decoding).
- **Absent**: long-method, large-class, feature-envy, long-parameter-list, shotgun-surgery,
  divergent-change, message-chains, speculative-generality.

## Map impact verdict
- **Evidence supports claimed change:** yes — every Map Impact claim was independently checked
  against source and/or reproduced, not accepted on the report.
- **Constraints not violated:** yes — `constraint:physics_region_no_evo_import` honored;
  `cross_view_covariance` passthrough-only honored (`fuse_dual_cda` never called).
- **Notes match the diff:** yes — the third-composer addition, read-only relationship to
  `struct:physics.layer2`, and the new `build_car_basis_posterior_records` capability all match
  what the diff actually contains.
- **Decision candidates surfaced:** yes — `prior_session` NEAREST-PRESENT was correctly
  surfaced as a resolved implementer decision (the handoff left it open), documented in the
  module docstring and tested explicitly.
- **Durable context routed:** yes — the one out-of-scope observation (the `_none_if_nan`
  duplication) is routed as triage candidate `tc1` in this review's survey rather than silently
  dropped or fixed out-of-scope.

## Reconciliation check
No architecture-map divergence. The new module is exactly the third composer the epic's
structural map anticipated (`struct:physics.feature_view`), read-only against
`struct:physics.layer2` as required.

## Blockers
- none

## Out-of-scope observations
- `tc1` (non-blocking, filed in this review's survey): `_none_if_nan` is duplicated between
  `build_car_basis.py` (G3) and `build_weekend_state.py` (G2, CLOSED). Worth factoring into one
  shared helper in a later gate once the `feature_view` package's composer count stabilizes —
  not fixable within G3's own scope since G2 is frozen.

## Workflow Feedback
- **Handoff gaps:** none — the handoff's source citations (the 9-name mapping table, the
  `EstimateRecord` shape, the FP3+Q-only edge case to try) were all precise and verified
  accurate on first read; nothing needed re-deriving from memory.
- **Context rediscovered:** none beyond ordinary source reading — the handoff's citations were
  precise enough that no additional digging was needed. (One incidental discovery, not a gap:
  the `_none_if_nan` duplication with G2's `build_weekend_state.py`, surfaced during the Fowler
  pass — filed as `tc1`, not something the handoff needed to have caught since G3 didn't yet
  exist when G2 closed.)
- **Instructions improvised around:** none — the reviewer skill's survey + Fowler-pass
  templates matched this review cleanly; no step needed working around.
- **What would have made this easier:** none — the handoff's explicit adversarial pointers
  (construct a real `cross_view_covariance` test yourself; try to break the reserved-field
  guarantee; probe FP3+Q-only) were exactly the right shape for a reviewer to act on directly
  without having to invent the adversarial angle from scratch.

## Return status
`complete`
