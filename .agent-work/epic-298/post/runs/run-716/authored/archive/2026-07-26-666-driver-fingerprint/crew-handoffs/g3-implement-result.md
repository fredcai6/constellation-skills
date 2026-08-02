# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3-implement` (epic659/666-driver-fingerprint; issue #666, epic #659)

## Completed slice
Built `src/physics/fingerprint/fit.py` — the G3 hierarchical Student-t shrinkage fit:
`fit_driver_fingerprints(observables_db_path, store, driver, *, as_of_round, era, vocabulary,
season, session_type="Q", map_version=None, channels=FINGERPRINT_CHANNELS,
what_measure=DEFAULT_WHAT_MEASURE, allow_unverified=False)`. Reads #664's
`driver_class_observables` (raw read-only `sqlite3` query, own-db, never edited), applies the
strictly-pre cutoff over the ENTIRE input set, recency-weights each (driver, class) cell,
feeds `fit_two_way(values, teams=drivers, circuits=classes)`, prices sigma at one structural
site (#675 class-level `shared_floor = sqrt(var_circuit)` per channel via
`pool_random_effects`), and writes exactly `vocabulary.k` cells per channel (both
`utilization`/`time_deficit_s` and `energy`/`deployment_share`) through
`DriverFingerprintStore.write_fingerprint`. All 6 plan items driven through the checklist
engine to completion (`m0-context` -> `m1-scaffold-required-arg` -> `m2-cutoff-keystone` ->
`m3-sigma-composition` -> `m4-recency-and-k-cells` -> `m5-verify-and-close`); plan file:
`.agent-work/666-driver-fingerprint/crew-handoffs/g3-implement-plan.json`.

## Scope
**Files changed (all NEW):**
- `src/physics/fingerprint/fit.py`
- `tests/unit/physics/fingerprint/test_fit.py`

**Specific exclusions touched:** no — `pooling.py`, `student_t.py`, `driver_utility.py`,
`address.py`, `vocabulary.py`, `store.py`, `frozen_constants.py` were read-only consumed
(imports/reference only), never edited. The G2 store schema was not changed. No online/full-
season pipeline run. No G4 end-to-end validation built.

## Behavior changed
Yes (additive only, one new production module) — no existing production code path is
touched; `fit.py` is new and standalone. It is a slow-offline mutation function only: never
invoked from `store.py`'s read path (verified — `store.py`'s own existing structural test,
`test_store_module_imports_no_fit_or_observables_module`, still passes unmodified, and this
gate added no import from `store.py` into any fit/pooling module).

## Map Impact
- **Structural anchors touched:** NEW `struct:physics.fingerprint.fit`
  (`fit_driver_fingerprints`, `_read_observable_rows`, `_aggregate_cells`,
  `_price_sigma_with_shared_floor`, `_compose_sigma`, `_fit_channel`). Consumed (read-only)
  `struct:physics.layer2.pooling` (`fit_two_way`, `pool_random_effects`),
  `struct:common.student_t` (imported names available for a downstream consumer;
  `predictive_t`/`FormulaRule`/`DEFAULT_NU_LOSS` are NOT called inside `fit.py` itself — per
  the handoff, "build it where consumed" — a G4 consumer builds the `PredictiveT` from the
  stored `(mean, sigma, support_n)`, not this gate), and the G2
  `struct:physics.fingerprint {address,vocabulary,store}` modules.
- **Capability:** the DriverFingerprint can now be FIT from real #664 observables (previously
  only the empty-store/synthetic-cell store existed, no producer). A batch/offline caller can
  now populate `driver_fingerprint_cells` for a (driver, era, vocabulary) across both
  channels, honoring the strictly-pre cutoff and the #675 shared-floor ruling.
- **Constraints/assumptions touched:** DB-BLOB guard (#632/#656) honored — `fit.py` never
  writes to the observables DB, tests use `tmp_path` only, no committed DB. #675's
  class-only-floor ruling honored (driver-overall level never floored — `shared_floor` enters
  ONLY inside `_price_sigma_with_shared_floor`, called on the class-cell sigma, never on any
  driver-overall/parent quantity, which this module does not even materialize as a separate
  stored value).
- **Decision anchors resolved:**
  - `decision:c1_driver_utilization_design` (strictly_pre load-bearing, 14.6x precedent) —
    CONFIRMED at the G3 fit boundary: the cutoff is a single SQL predicate
    (`round_idx <= ?`) applied to the entire `driver_class_observables` read, before any
    grouping/pooling, so it protects the target cell, the class-across-drivers parent, and
    the field mean uniformly. Regrade stays `settled/measured` — this run adds a second,
    independent measured confirmation (the keystone test's genuine RED demonstration below),
    it does not re-open the decision.
  - `decision:pooled_sigma_shared_systematic_floor` (#675 class-axis shared_floor) —
    CONFIRMED as specified: `shared_floor = sqrt(fit_two_way(...).var_circuit)` per channel,
    applied via `pool_random_effects(shared_floor=...)`'s own `k==1` branch, at exactly one
    call site (`_price_sigma_with_shared_floor`), exactly once per resolved cell (proven by a
    call-count spy, not just documentation).
- **Claims/evidence produced:** `claim: cutoff-leakage` (keystone, both poison forms, genuine
  RED+GREEN), `claim: sigma-priced-once` (single-site spy + idempotence, genuine RED+GREEN),
  `claim: G-byte-identical` (point invariant under g_sigma_onesided=0 vs >0, genuine
  RED+GREEN) — see Evidence below for all three, pasted with the sabotage-and-restore RED
  proof for each.
- **Trust limitations / drift found:** none discovered in existing code. One belt-and-
  suspenders finding (not a gap): `store.write_fingerprint` independently re-checks
  `support_n >= FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR` before marking a cell resolved, so even
  if `fit.py`'s own floor check in `_fit_channel` were removed, a thin cell would still be
  written unresolved by the store. Confirmed during the m4 RED demonstration (see Assumptions
  below) — kept `fit.py`'s own check for clarity/efficiency (skips computing `TwoWayPool`
  math for cells that would be discarded anyway) even though the store enforces the floor
  independently.
- **Triage candidates:** none new. The pre-existing G2 triage candidate (vocabulary-drift
  migration path) is untouched by this gate.

## Test mode
**Required:** TDD (test-first) — the acceptance invariants ARE the test surface, per the
handoff's Test Mode section.
**Satisfied:** yes. `m1`'s two tests were written before `fit.py` existed (RED =
`ModuleNotFoundError`). For `m2`/`m3`/`m4` — where the relevant code path already existed
from an earlier slice by the time the specific test was written (because the same module
implements several invariants at once) — RED was proven by temporarily sabotaging the exact
code path under test (removing the cutoff clause, double-calling `pool_random_effects`,
dropping the g/lapsampling terms, dropping recency from the averaging weight, fitting only
one channel), observing the corresponding test(s) fail, then reverting the sabotage and
confirming GREEN. This is documented per-slice below and is a stronger proof than a trivial
`ModuleNotFoundError` red, since it demonstrates the test actually discriminates the
invariant it claims to guard.

## Evidence

### Full `test_fit.py` run (final, all 14 tests)
```bash
cd C:/Programs/f1brainz-wt/epic659-666
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_fit.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1brainz-wt\epic659-666
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 14 items

tests\unit\physics\fingerprint\test_fit.py ..............                [100%]

============================== 14 passed in 0.58s ==============================
```

### Whole fingerprint package regression (G2 + G3 together)
```bash
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/ -q
```
```
collected 83 items
tests\unit\physics\fingerprint\test_address.py ......................... [ 30%]
tests\unit\physics\fingerprint\test_fit.py ..............                [ 50%]
tests\unit\physics\fingerprint\test_frozen_constants.py ....             [ 55%]
tests\unit\physics\fingerprint\test_store.py .................           [ 75%]
tests\unit\physics\fingerprint\test_vocabulary.py ....................   [100%]
============================= 83 passed in 0.70s ==============================
```

### Layer2 regression (confirms read-only consumption of `pooling.py` caused no drift)
```bash
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/ tests/unit/physics/layer2/ -q
```
```
============================== 1006 passed, 2 warnings in 754.98s (0:12:34) =================
```
(2 warnings are pre-existing pandas `FutureWarning`s in `test_regime_capability_dashboard.py`,
unrelated to this gate.)

### LOAD-BEARING: cutoff-leakage keystone (both poison forms)
```bash
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_fit.py -k cutoff -q -v
```
```
tests/unit/physics/fingerprint/test_fit.py::TestCutoffLeakageKeystone::test_target_driver_future_row_is_noop PASSED
tests/unit/physics/fingerprint/test_fit.py::TestCutoffLeakageKeystone::test_non_target_driver_future_row_is_noop PASSED
2 passed, 2 deselected in 0.44s
```
**Genuine RED proof (m2):** temporarily removed the `AND round_idx <= ?` clause from
`_read_observable_rows`'s SQL query and reran `-k cutoff`:
```
E   ValueError: round_idx=5 is after as_of_round=2; the strictly-pre cutoff should have
    excluded this row upstream
2 failed, 2 deselected in 0.50s
```
Both tests failed loudly (the module's own `Δround >= 0` defensive guard in
`_recency_weight` fired, since an un-cut future row produces a negative `Δround`) — proving
the cutoff clause is load-bearing, not decorative. Clause restored; reran green (above).
Cites #628's measured 14.6x materiality precedent
(`docs/architecture/decisions/c1-driver-utilization-design.md`, "Extension (2026-07-19, #628
Phase 3b)") in the test docstring.

### LOAD-BEARING: sigma-priced-once (single-site + idempotence)
```bash
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_fit.py -k "SigmaPricedAtSingleSite or SigmaIdempotence" -q -v
```
```
tests/unit/physics/fingerprint/test_fit.py::TestSigmaPricedAtSingleSite::test_shared_floor_priced_once_per_resolved_cell PASSED
tests/unit/physics/fingerprint/test_fit.py::TestSigmaIdempotence::test_rerun_on_identical_inputs_is_byte_identical PASSED
tests/unit/physics/fingerprint/test_fit.py::TestSigmaIdempotence::test_helper_single_application_not_equal_to_naive_double_application PASSED
3 passed, 7 deselected in 0.46s
```
**Genuine RED proof (m3):** temporarily made `_price_sigma_with_shared_floor` call
`pool_random_effects` TWICE (double-apply) and reran the single-site test:
```
E   AssertionError: assert 8 == 4
E    +  where 8 = <MagicMock name='pool_random_effects' ...>.call_count
```
(8 calls observed vs 4 resolved cells expected — the spy caught the exact double-call.)
Restored to a single call; reran green.

### LOAD-BEARING: G byte-identical point
```bash
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_fit.py -k GByteIdenticalPoint -q -v
```
```
tests/unit/physics/fingerprint/test_fit.py::TestGByteIdenticalPoint::test_g_sigma_onesided_changes_sigma_not_mean PASSED
1 passed, 9 deselected in 0.44s
```
**Genuine RED proof (m3, combined with the sigma_lapsampling sabotage):** temporarily
changed `_compose_sigma` to `return math.sqrt(base ** 2)` (dropping the
`g_sigma_onesided`/`sigma_lapsampling` terms):
```
E   AssertionError: assert 1.9999999999999996 > 1.9999999999999996
```
(sigma stopped differing between g=0 and g=3 once the term was dropped — the test caught it.)
Restored the full composition; reran green.

### `simplification_limits`
```bash
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m src.utils.simplification_limits --paths src/physics/fingerprint/fit.py tests/unit/physics/fingerprint/test_fit.py
```
```
PASS (2 files checked)
```
(One intermediate iteration flagged `_aggregate_cells: cyclomatic_complexity=20` (limit
`<20`); refactored into `_row_to_bucket_item`/`_optional_weighted_mean`/`_combine_bucket`
helpers — same behavior, `test_fit.py` re-ran green after the refactor, then
`simplification_limits` passed.)

### Git status / check-ignore
```bash
git status --porcelain
```
```
?? .agent-work/663-grip-g/            <- pre-existing, not this gate's output
?? .agent-work/666-driver-fingerprint/
?? scripts/fingerprint_class_coverage_675.py   <- from g1, not this gate
?? src/physics/fingerprint/
?? tests/unit/physics/fingerprint/
```
```bash
git check-ignore -v src/physics/fingerprint/fit.py tests/unit/physics/fingerprint/test_fit.py
```
Exit code 1 (not ignored — correctly trackable). Nothing staged; no `data/` or `.agent-work`
blob was ever staged or committed this gate.

**Result:** pass — all verification commands run foreground to completion, reproducibly
(re-run immediately before writing this result, same output).

## TDD evidence, if required
- **m1 (scaffold + required-arg):** RED — `ModuleNotFoundError: No module named
  'src.physics.fingerprint.fit'` (test file written before `fit.py` existed). GREEN — both
  tests pass after the initial `fit.py` implementation.
- **m2 (cutoff keystone):** RED via sabotage (cutoff clause removed) -> both tests fail
  loudly; GREEN after restore. See Evidence above.
- **m3 (sigma composition):** RED via sabotage (double-call `pool_random_effects`; drop
  g/lapsampling terms) -> 4 tests fail (single-site, idempotence-helper, G-byte-identical,
  lapsampling-widens); GREEN after restore. See Evidence above.
- **m4 (recency + k-cells):** RED via sabotage (drop recency from the averaging weight;
  fit only the first channel) -> 2 tests fail (recency-skew, both-channel); GREEN after
  restore. A third sabotage (drop `fit.py`'s own unresolved-floor check) did NOT produce a
  failure, because `store.write_fingerprint` independently re-enforces the same floor —
  documented as a belt-and-suspenders finding, not a test gap, in Map Impact above.
- Refactor while green: yes — the `_aggregate_cells` complexity refactor (see
  `simplification_limits` above) was applied after all 14 tests were green, and the full
  suite was re-run green immediately after.

## Docs/contracts touched
- none — no doc file edited; this gate is code + test only. `decision:*` anchors are recorded
  here (Map Impact) for a future Cartographer reconcile pass, not edited in
  `docs/architecture/` directly (out of this crew's authority).

## Assumptions
- **`sigma0` base definition:** `sigma0 = sqrt(pool.var_resid / n_eff_cell)` — the two-way
  fit's own residual variance (a channel-wide "typical unexplained noise per raw cell")
  divided by the cell's recency-effective support, i.e. the SEM of the cell mean under that
  noise level. Chosen over a per-cell empirical variance (many real cells have only 1-2 raw
  rows, too few to estimate their own variance robustly) — this is explicitly one of the two
  alternatives the handoff itself sanctions ("the within-group naive SEM ... **or the fit's
  residual scale**"). Floored at `1e-9` (matches `pooling.py`'s own `sigma_floor` default) so
  a perfect-fit degenerate case never yields a literal-zero sigma feeding a downstream
  `predictive_t`.
- **Recency-aggregation mechanics:** each row's averaging weight is `recency * n_points`
  (recency alone would ignore how many points backed a given row's own deficit/share
  estimate; `n_points` alone would ignore staleness) — the SAME weight defines both the
  cell's recency-weighted VALUE and, summed alone, the recency-effective support `n_eff`
  (handoff: "a recency-weighted cell value + a recency-effective support n_eff
  (recency-weighted sum of n_points)"). `g_sigma_onesided`/`sigma_lapsampling` are aggregated
  the same way over non-NULL rows only (present-but-zero default when every row in a cell is
  NULL for that column).
- **`(driver, class)` fit_two_way input:** one row per resolved cell (the recency-weighted
  aggregate), not one row per raw observation — matches the handoff's literal wording
  ("Feed the per-(driver,class) values to fit_two_way(...)"), and keeps the two-way ANOVA
  from being dominated by classes/drivers with simply more raw rows rather than more
  genuine information (recency + n_points already folded the raw-row information into each
  cell's single value/n_eff pair).
- **"idempotence" test interpretation:** the handoff's phrase "re-invoking the pricing op on
  an already-floored σ == applying it once (no double-floor)" is tested two ways: (1)
  rerunning the WHOLE fit on identical raw inputs is byte-identical across runs (proves no
  state persists between runs that would compound); (2) a direct helper-level check that
  naively feeding `_price_sigma_with_shared_floor`'s own output back through itself produces
  a strictly LARGER value than applying it once (proves the fit's actual single-call design
  is the only correct choice — a caller who mistakenly chained two calls would get a visibly
  wrong, larger number). Both are documented in the test docstrings.
- **`shared_floor_applied` semantics:** set `True` on every resolved `CellObservation` (the
  pricing OPERATION always ran), even in the edge case `var_circuit == 0` (floor value itself
  is then `0.0`) — this records "did the fit apply the floor-pricing step", not "was the
  resulting floor value positive".
- **Channel name mapping:** `"utilization"` -> `time_deficit_s`, `"energy"` ->
  `deployment_share`, per `address.py`'s `FINGERPRINT_CHANNELS = ("utilization", "energy")`
  (the handoff's own "time"/"energy" phrasing maps onto these two address.py channel names —
  confirmed by cross-reading `address.py`'s docstring, which calls both Build-1 FIT axes).

## Stop conditions hit
- None. Every crown invariant was made structural within this gate's authority:
  `as_of_round` required-no-default falls out of Python's own keyword-only argument binding;
  the cutoff is a single SQL predicate over the whole read; the sigma composition has one
  call site for `pool_random_effects`; the G/point independence and the
  `sigma_lapsampling` present-but-zero default both fell out of the aggregation design
  without needing any special-casing. `fit_two_way`'s outputs (`var_resid`, `var_circuit`,
  `predict`) supported the hierarchy exactly as specified. No forbidden file was edited; no
  G2 schema change was needed.

## Out-of-scope observations
- **Belt-and-suspenders floor enforcement** (see Map Impact) — `fit.py`'s own
  unresolved-floor check in `_fit_channel` is redundant with `store.write_fingerprint`'s
  independent re-check of the same floor. Not a defect (defense-in-depth is good), just
  worth noting for a future reader wondering why the m4 sabotage of `fit.py`'s check alone
  didn't produce a failing test.
- **`predictive_t` construction is deliberately NOT in `fit.py`** — the handoff says "build
  it where consumed"; this gate stores only `(mean, sigma, support_n)`. A future G4 consumer
  should confirm `predictive_t(mean, sigma, support_n, nu_loss=DEFAULT_NU_LOSS,
  rule=FormulaRule())` constructs without error from every resolved cell this fit writes
  (sigma is always `> 0` by construction, `support_n` is always `>= 1.0` for a resolved cell)
  — not verified end-to-end here since it is out of this gate's scope, but the invariants
  that would make it fail (a zero/negative sigma, a zero/absent `n_eff`) are structurally
  excluded by this implementation.

## Workflow Feedback
- **Handoff gaps:** none material. The handoff's function-signature sketch
  (`fit_driver_fingerprints(observables_db_path, store, *, as_of_round, era, vocabulary,
  season, ...)`) omitted the `driver` parameter from the visible signature (folded into
  "..."); I placed it as a third positional parameter before the keyword-only `*` — a
  reasonable, low-risk placement given the Authority section explicitly delegates mechanics
  not pinned by the crown invariants.
- **Context rediscovered:** none beyond the ordinarily-pointed-at reference seams
  (`pooling.py`, `student_t.py`, `frozen_constants.py`, `address.py`/`vocabulary.py`/
  `store.py`, `reference_utilization_store.py`'s `driver_class_observables` schema, and the
  #675 diagnostic script) — the handoff and `notes-666.md` named all of these directly.
- **Instructions improvised around:** the handoff's Tests section names "idempotence" for
  the sigma-priced-once invariant without fully disambiguating "rerun the whole fit twice"
  vs "feed a helper's own output back into itself" — I implemented and documented BOTH
  readings (see Assumptions) rather than picking one, since they are complementary and
  cheap to prove together.
- **What would have made this easier:** nothing significant — this handoff was unusually
  precise about the exact hierarchy, sigma-composition formula, and derivation source
  (`sqrt(fit_two_way(...).var_circuit)`), which left very little genuine ambiguity to
  resolve. The one recurring friction across G1/G2/G3 gates in this epic (per the g2 result's
  own Workflow Feedback) — the `simplification_limits` CLI needing `--paths` — was already
  fixed in this handoff's Verification Commands.

## Return status
`complete`
