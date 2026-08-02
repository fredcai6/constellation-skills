# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3` — build `src/physics/feature_view/build_car_basis.py`

## Completed slice
Built a pure composer, `build_car_basis_posterior_records(store, year, gp_name, *,
model_version) -> list[CarBasisPosteriorRecord]`, that reads `session_estimates` rows
(via `EstimateStore.load(year=year, session_type=None, status="ok")`, one query, then
filters to `gp_name` in pandas since `EstimateStore.load` has no `gp_name` param), and
for each (constructor, session_type) row produces one `CarBasisPosteriorRecord`:
- fans the 9 `AXIS_STATUS_NAMES` status columns out to the 11 physical axis names
  (`cda`→2 axes, `theta_R`→2 axes, the other 7 status names→1 axis each), normalizing
  every raw status value via `normalize_axis_status` first;
- computes `axis_sigma` per axis via `effective_axis_sigma` (imported, not reimplemented);
- sets `chain_position` = the row's own `session_type`, and `prior_session` via a
  NEAREST-PRESENT interpretation (picked explicitly, per the handoff's Close Criteria —
  see docstring): the nearest earlier `SESSION_ORDER` session that this constructor
  actually has a row for, `None` when there is none;
- copies `row["cross_view_covariance"]` straight through, unchanged — no re-fusion;
- leaves both reserved fields (`process_noise_link`, `parc_ferme_step`) at their
  dataclass defaults (`None` / `"unresolved"`) — never sets them.

## Scope
**Files changed:**
- `src/physics/feature_view/build_car_basis.py` (new)
- `tests/unit/physics/feature_view/test_build_car_basis.py` (new)

**Specific exclusions touched:** no — `records.py`, `store.py`, `build_weekend_state.py`,
`estimate_store.py`, `estimate_store_fields.py`, `cross_view.py` were read-only references,
never edited. `cross_view.fuse_dual_cda` is not imported or called anywhere in the new file
(grep-verified, see Evidence).

## Behavior changed
Yes — new capability. No existing module's behavior changed (G1/G2 files untouched;
their tests re-run clean as part of the full suite, see Evidence).

## Map Impact
- **Structural anchors touched:** `struct:physics.feature_view` — added
  `build_car_basis.py`, the third composer alongside `records.py`/`store.py` (G1) and
  `build_weekend_state.py` (G2). Read-only against `struct:physics.layer2`
  (`estimate_store`, `estimate_store_fields`, `cross_view` — cited, never modified,
  `fuse_dual_cda` never called).
- **Capabilities added/changed/affected:** new capability
  `build_car_basis_posterior_records` — composes `CarBasisPosteriorRecord` rows from
  `EstimateStore` for a `(year, gp_name)`, ready for `FeatureViewStore.insert_car_basis_posterior`
  (G1, unmodified) to persist.
- **Constraints/assumptions touched:** `constraint:physics_region_no_evo_import` honored
  (no `evo_predictor` import anywhere in the new file — grep-verified).
- **Decision candidates / resolved decisions:** `prior_session` interpretation resolved as
  NEAREST-PRESENT (not chain-adjacent-regardless) — the handoff left this as the
  implementer's choice; documented and tested explicitly (see module docstring and
  `test_prior_session_is_nearest_present_not_chain_adjacent_regardless`).
- **Claims/evidence produced:** `cross_view_covariance` full-covariance passthrough
  verified dict-equal (source vs. produced record, round-tripped through the store's own
  JSON de/serialization); the 9-to-11 axis-status mapping verified for both
  two-axis-governing status names (`cda`, `theta_R`).
- **Triage candidates:** none raised — no defect found in G1/G2 frozen dependencies.

## Test mode
**Required:** test-first (TDD)
**Satisfied:** yes, with one honest deviation noted below (the whole composer was
implemented in one coherent pass in the first TDD cycle rather than staged
half-implemented across the three implementation gates in my own plan — see Workflow
Feedback). Every gate's tests were written before being confirmed green, and a genuine
RED was caught and fixed in the third gate (see TDD evidence).

## Evidence

```bash
cd C:/Programs/f1-629
export PATH="/c/Users/fredc/AppData/Local/Microsoft/WindowsApps:$PATH"
py -m pytest tests/unit/physics/feature_view -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1-629
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 48 items

tests\unit\physics\feature_view\test_append_only_contract.py ..          [  4%]
tests\unit\physics\feature_view\test_as_of_leakage.py .....              [ 14%]
tests\unit\physics\feature_view\test_build_car_basis.py ...............  [ 45%]
tests\unit\physics\feature_view\test_build_weekend_state.py ......       [ 58%]
tests\unit\physics\feature_view\test_records.py ..........               [ 79%]
tests\unit\physics\feature_view\test_store.py ..........                 [100%]

============================= 48 passed in 0.80s ==============================
```

```bash
py -m src.utils.simplification_limits --paths src/physics/feature_view
```
```
PASS (5 files checked)
```

```bash
grep -rn "evo_predictor\|fuse_dual_cda" src/physics/feature_view/build_car_basis.py || echo clean
```
```
clean
```

```bash
git check-ignore src/physics/feature_view/build_car_basis.py; echo "exit=$?"
git check-ignore tests/unit/physics/feature_view/test_build_car_basis.py; echo "exit=$?"
```
```
exit=1
exit=1
```

**Result:** pass — all evidence commands produced the required output on first re-run in
this turn (not copied from memory).

**Concrete example — 9-to-11 axis-status fan-out and cross_view_covariance passthrough**
(built via a one-off script exercising the composer on a synthetic `EstimateRecord` with
`cda_status="unresolved"`, `theta_R_status="resolved"`, and a populated
`cross_view_covariance`):

```
== axis_status fan-out (cda_status='unresolved', theta_R_status='resolved') ==
drag_area_closed_m2: unresolved
power_drag_area_m2 : unresolved
coast_rolling_decel_ms2: resolved
coast_drag_area_m2     : resolved

== cross_view_covariance passthrough ==
source : {'cov_cda_a_b': 0.0012, 'cov_cda_b_b': None, 'cov_cda_a_t': -0.0004, 'cov_cda_b_t': None, 'fused_cda': {'mu': 1.21, 'sigma': 0.015}, 'fused_cda_z': 1.8, 'fused_cda_reason': 'ok'}
record : {'cov_cda_a_b': 0.0012, 'cov_cda_b_b': None, 'cov_cda_a_t': -0.0004, 'cov_cda_b_t': None, 'fused_cda': {'mu': 1.21, 'sigma': 0.015}, 'fused_cda_z': 1.8, 'fused_cda_reason': 'ok'}
equal? : True

== reserved fields ==
process_noise_link: None unresolved
parc_ferme_step   : None unresolved
```

## TDD evidence, if required
- Failing test observed (module didn't exist yet):
  ```
  ModuleNotFoundError: No module named 'src.physics.feature_view.build_car_basis'
  ERROR tests/unit/physics/feature_view/test_build_car_basis.py
  Interrupted: 1 error during collection
  ```
- Genuine second RED observed (in the cross-view-passthrough gate): my own module
  docstring's prose named `fuse_dual_cda` literally (explaining why it's not called),
  which tripped `test_fuse_dual_cda_not_imported_or_called`'s literal-string grep even
  though the code itself never imports/calls it:
  ```
  FAILED tests/unit/physics/feature_view/test_build_car_basis.py::test_fuse_dual_cda_not_imported_or_called
  AssertionError: assert 'fuse_dual_cda' not in '...'
  ```
  Fixed by rewording the docstring to describe the helper without using its literal name.
- Passing test observed: `48 passed in 0.80s` (see Evidence above), 15/15 in the new file.
- Refactor while green: no separate refactor pass needed beyond the docstring-wording fix
  above (which was itself the fix for a genuine red, not a refactor).

## Docs/contracts touched
- none beyond the new module's own docstring (no shared docs/contracts files touched)

## Assumptions
- `EstimateStore.load(status="ok")` (matching its own default) is the right status filter
  for building posteriors — an `"error"` row carries no real fit to compose a posterior
  from. Not stated explicitly in the handoff; inferred from `EstimateStore.load`'s own
  default and `error_record`'s all-`None` shape.
- `prior_session` uses the NEAREST-PRESENT interpretation (handoff left this as the
  implementer's choice) — picked per the handoff's own steer ("prefer nearest-present
  ... unless you find a strong reason otherwise"); no strong reason found to deviate.
- Loading strategy: one `store.load(session_type=None)` call + pandas-side `gp_name`
  filter + groupby, rather than four separate per-session-type `load()` calls (handoff
  said "either approach is fine; state which you chose").

## Stop conditions hit
None. `EstimateRecord.cross_view_covariance`'s shape matched the handoff's description
exactly (verified directly against `estimate_store.py`'s own `_CROSS_VIEW_COVARIANCE_KEYS`
comment); no decision outside this handoff's authority was needed; scope was not exceeded.

## Out-of-scope observations
None — no defect found in G1 (`records.py`, `store.py`) or G2 (`build_weekend_state.py`);
both were read-only references and matched their own docstrings/contracts exactly as the
handoff described them.

## Workflow Feedback
- **Handoff gaps:** none — the handoff's seam citations (line numbers, exact function
  names, the 9-to-11 mapping table) were all verified accurate against the actual source
  on first read; nothing needed re-deriving from memory.
- **Context rediscovered:** none beyond ordinary source reading — the handoff's citations
  were precise enough that no additional digging was needed.
- **Instructions improvised around:** my own plan (built per the constellation-implementer
  skill's TDD-per-vertical-slice convention) staged the work as three separate
  implementation gates (status-mapping, chain-position, cross-view-passthrough), each
  expecting its own red→green cycle. In practice, once the axis-status mapping and the
  `EstimateRecord` shape were understood from the handoff, the whole composer (including
  correct `prior_session`/`cross_view_covariance` logic) was simplest to write as one
  coherent function rather than deliberately half-implementing it across gates. Gates 2
  and 3's tests therefore passed on first execution against the already-complete
  implementation rather than showing a fresh functional red — I attested this honestly at
  each step rather than fabricating a red state, and gate 3 still produced one genuine red
  (a docstring wording collision with the literal-string grep check), which was fixed and
  re-verified. Net effect: the evidence trail is honest, but a plan template that assumes
  every implementation gate produces its own fresh functional red doesn't fit a composer
  small enough to write in one pass — worth noting for future G3-shaped (single small
  composer function) handoffs.
- **What would have made this easier:** for a bounded single-function composer like this
  one, a plan shaped as "one TDD cycle covering the whole function, then N verification
  slices for named sub-behaviors" might match reality better than "N implementation gates
  each expecting its own red." Not a blocking issue — just a shape mismatch worth
  flagging.

## Return status
`complete`
