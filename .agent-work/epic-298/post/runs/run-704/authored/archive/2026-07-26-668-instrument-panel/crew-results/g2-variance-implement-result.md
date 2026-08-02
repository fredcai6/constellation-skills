# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2-variance-implement` (#668 instrument panel, epic #659)

## Completed slice
Instrument 1 — the variance-decomposition instrument: a pure function
`decompose_segment_time_variance(values, drivers, classes) -> VarianceShares`
that splits segment-time variance into car-reference / driver-utilization /
residual shares via the additive `TwoWayPool` arithmetic
(`fit_two_way(values, teams=drivers, circuits=classes)` from
`src/physics/layer2/pooling.py`, unmodified), with the driver-utilization
share carried as an explicit FLOOR flag. Full synthetic-recovery TDD suite
(7 tests) built and green; pyright-clean on the new module.

## Scope
**Files changed:**
- `src/physics/instrument_panel/__init__.py` (new — package marker + docstring)
- `src/physics/instrument_panel/variance_decomposition.py` (new — `VarianceShares` + `decompose_segment_time_variance`)
- `tests/unit/physics/instrument_panel/__init__.py` (new)
- `tests/unit/physics/instrument_panel/test_variance_decomposition.py` (new — 7 synthetic-recovery tests)

**Specific exclusions touched:** no — no #660/#664/#666/#667 producer module touched, no real DB read, no interaction term added, no `f1_data_*.db` written.

## Behavior changed
Yes — new capability. `src/physics/instrument_panel/` is a brand-new package;
no existing module's behavior changed. `fit_two_way`/`TwoWayPool` in
`src/physics/layer2/pooling.py` were read-only reused, not modified.

## Map Impact
- **Structural anchors touched:** `src/physics/layer2/pooling.py` (`TwoWayPool`/`fit_two_way`, file-level) — READ-ONLY reuse, no edits. `src/physics/instrument_panel/` (new package, file-level) — new structural anchor: `variance_decomposition.py` (`VarianceShares`, `decompose_segment_time_variance`).
- **Capabilities added/changed/affected:** new capability — driver-utilization / car-reference variance sizing (Instrument 1 of the #668 instrument panel), exposed as `decompose_segment_time_variance`. Pure, deterministic, no I/O.
- **Constraints/assumptions touched:** `constraint:lowest-dimensionality` honored (no interaction term added — the additive `fit_two_way` pool has none, and `decompose_segment_time_variance` adds no model on top of it). `constraint:no-frame-kill` honored — `driver_utilization_is_floor` is always `True` and carried as an explicit field on every `VarianceShares`, not an implicit convention.
- **Decision candidates / resolved decisions:** the car-reference=`frac_circuit` / driver-utilization=`frac_team` axis mapping and the no-interaction-term rule were pinned by the handoff (commander authority, from the launch order + #665/#675 convention) and were NOT re-litigated here — followed as given.
- **Claims/evidence produced:** `car_reference_share`/`driver_utilization_share`/`residual_share` each recover their synthetic ground-truth coefficient direction (monotone-in-b, near-zero cross-share under a pure-car or pure-driver signal) — see Evidence below.
- **Triage candidates:** none raised by this slice; this instrument is deliberately scoped to pure math over synthetic data (F12-independent), consistent with the handoff's exclusions.

## Test mode
**Required:** `test-first (TDD)`
**Satisfied:** yes — RED observed (`ModuleNotFoundError: No module named 'src.physics.instrument_panel'`) before any production code existed, then GREEN after implementation.

## Evidence

```bash
cd /c/Programs/f1brainz-wt/epic659-668 && "/c/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pyright src/physics/instrument_panel/variance_decomposition.py && "/c/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/instrument_panel/test_variance_decomposition.py -q
```
Output:
```
0 errors, 0 warnings, 0 informations
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1brainz-wt\epic659-668
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 7 items

tests\unit\physics\instrument_panel\test_variance_decomposition.py ..... [ 71%]
..                                                                       [100%]

============================== 7 passed in 0.51s ==============================
```

**Result:** pass (this is the engine-run command check for m2-pyright-evidence.c1)

## TDD evidence, if required

- Failing test observed: `python -m pytest tests/unit/physics/instrument_panel/test_variance_decomposition.py -q` → `ImportError ... ModuleNotFoundError: No module named 'src.physics.instrument_panel'`, `1 error in 0.72s` (module + package did not yet exist).
- Passing test observed: same command → `7 passed in 0.51s` (see Evidence above), after implementing `src/physics/instrument_panel/__init__.py` + `variance_decomposition.py`.
- Refactor while green: no — the implementation is a single thin pass-through over `fit_two_way`; nothing to refactor.

### Confirmatory: shares sum to ~1.0 and lie in [0,1] on a spot example
Every test uses `_assert_valid_shares` which asserts each share is finite and
in `[0, 1]` and that `car_reference_share + driver_utilization_share +
residual_share == pytest.approx(1.0, abs=1e-6)`; this holds on the
`a=1.0, b=1.0` balanced-grid case (`test_shares_are_valid_and_sum_to_one`) and
on both degenerate single-class/single-driver cases.

### Synthetic-recovery detail (per-share falsifiability)
- `test_driver_utilization_share_rises_monotonically_with_b`: fixed `a=1.0`,
  `b` swept `(0.0, 0.5, 1.0, 2.0)` with the SAME seed (so car/driver effect
  draws and the noise sequence are identical across the sweep — only `b`
  changes) → `driver_utilization_share` strictly non-decreasing and the
  top-vs-bottom gap `> 0.1` (real movement, not jitter).
- `test_pure_car_signal_gives_near_zero_driver_utilization_share` (`b=0.0`):
  `driver_utilization_share < 0.1` and `car_reference_share >
  driver_utilization_share`.
- `test_pure_driver_signal_gives_near_zero_car_reference_share` (`a=0.0`):
  `car_reference_share < 0.1` and `driver_utilization_share >
  car_reference_share`.
- `test_driver_utilization_share_is_flagged_as_a_floor`: `driver_utilization_is_floor is True`.
- `test_degenerate_single_class_input_returns_sane_result` /
  `test_degenerate_single_driver_input_returns_sane_result`: no crash, all
  shares still valid and summing, floor flag still `True`.

## Docs/contracts touched
- none — this is a new, self-contained pure module; no existing contract or doc changed.

## Assumptions
- The handoff's axis pin (`teams=drivers` → `frac_team` = driver-utilization,
  `circuits=classes` → `frac_circuit` = car-reference) was followed literally
  and verified against `src/physics/layer2/pooling.py`'s actual field names
  and `fit_two_way` signature before use (not just taken from the handoff's
  prose).
- `VarianceShares` carries an `n` (observation count) field beyond the three
  required shares + floor flag, for provenance — a natural, low-risk addition
  since `TwoWayPool.n` was already available; happy to drop it if Commander
  prefers a stricter four-field shape.

## Stop conditions hit
- none — the additive pool expressed all three shares cleanly; no interaction
  term was needed or added; no real DB read was required.

## Out-of-scope observations
- none beyond what the handoff already scoped out (Build-2 producer modules,
  real-data validation) — this instrument is deliberately synthetic-only per
  the handoff's own exclusions.

## Workflow Feedback
- **Handoff gaps:** none — the handoff's Close Criteria, Authority, and Map
  Anchors sections gave an unambiguous axis mapping and a concrete synthetic
  test recipe; no field was missing or contradictory.
- **Context rediscovered:** none beyond ordinary reuse-verification — read
  `src/physics/layer2/pooling.py`'s `TwoWayPool`/`fit_two_way` source directly
  (CREW_CONTEXT.md's "verify a cited seam against source" rule) rather than
  trusting the handoff's field list from memory; it matched exactly.
- **Instructions improvised around:** none — the handoff's suggested function
  signature and dataclass field names were followed as given; `n` was the one
  small addition beyond the four named fields (see Assumptions).
- **What would have made this easier:** nothing concrete to flag — this was a
  clean, well-scoped, single-file pure-math slice.

## Return status
`complete`
