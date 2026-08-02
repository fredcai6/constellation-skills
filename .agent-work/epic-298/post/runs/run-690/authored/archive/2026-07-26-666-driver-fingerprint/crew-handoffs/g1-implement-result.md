# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g1-implement` (epic659/666-driver-fingerprint; issue #666, epic #659 Wave 3)

## Completed slice
Built the `src/physics/fingerprint/` package's pre-registered frozen-constant set
(`FINGERPRINT_FROZEN`, 4 exact commander-pinned values, F12 discipline) and a #675
class-axis coverage diagnostic (`scripts/fingerprint_class_coverage_675.py`) that
reproduces #665's synthetic-recovery coverage method exactly, but driven by the REAL
per-(driver, class) support counts read from the commander-provided bounded slice DB
(`fp_slice_2023Q.db`) instead of #665's proxy class-share profiles. Ran the diagnostic
and the frozen-constants test; both pass. Both plan items driven through the checklist
engine to completion (`m0-context` → `m1-frozen-constants` → `m2-coverage-script` →
`m3-verify-and-close`); plan file:
`.agent-work/666-driver-fingerprint/crew-handoffs/g1-implement-plan.json`.

## Scope
**Files changed (all NEW):**
- `src/physics/fingerprint/__init__.py`
- `src/physics/fingerprint/frozen_constants.py`
- `scripts/fingerprint_class_coverage_675.py`
- `tests/unit/physics/fingerprint/__init__.py`
- `tests/unit/physics/fingerprint/test_frozen_constants.py`

**Specific exclusions touched:** no — `pooling.py`, `student_t.py`, `driver_utility.py`,
and `layer2/frozen_constants.py` were read-only consumed (imports only), never edited.
No online FastF1 call. The slice DB was not regenerated.

## Behavior changed
Yes (additive only, new package + new script + new tests) — no existing production code
path is touched; the diagnostic script and frozen constants are new, standalone modules.

## Map Impact
- **Structural anchors touched:** `struct:physics.fingerprint frozen_constants` (NEW —
  `src/physics/fingerprint/frozen_constants.py`, module-level immutable mapping
  `FINGERPRINT_FROZEN`). Consumed `struct:physics.layer2 pooling.fit_two_way` (read-only
  import, unmodified) and `struct:common student_t.predictive_t`/`FormulaRule` (read-only
  import, unmodified).
- **Capabilities added/changed/affected:** new #675 class-axis coverage diagnostic
  capability (`scripts/fingerprint_class_coverage_675.py`), producing a per-channel/axis
  synthetic-recovery coverage verdict against a real bounded driver×class slice.
- **Constraints/assumptions touched:** F12 pre-registration discipline honored (4 values
  frozen in the plan/handoff before this run touched the real slice; none tuned to the
  observed numbers). `decision:pooled_sigma_shared_systematic_floor` — this diagnostic's
  `shared_floor_recommendation` output is the class-axis lever input for that decision,
  final apply/no-apply left to the commander (per Authority in the handoff).
- **Claims/evidence produced:** `claim: #675-coverage` — real class-axis (AND, notably,
  driver-axis — see Out-of-scope observations) empirical coverage measured vs the 0.80
  nominal level, on the actual bounded slice; see Evidence below for the full numbers.
- **Trust limitations / drift found:** the #675 "class-specific under-coverage"
  framing does not cleanly separate class from driver in THIS bounded slice — see
  Out-of-scope observations; a future consumer of this verdict should not read
  `generalizes: true` as "only the class axis is miscalibrated here."
- **Triage candidates:** whether `shared_floor` (or an analogous floor) should also be
  considered for the DRIVER axis given the symmetric under-coverage found here, and
  whether the `.gitignore` should be extended to cover `.agent-work/**/*.json` (or
  something narrower) so a local verdict artifact isn't accidentally `git add -A`-able —
  see Workflow Feedback.

## Test mode
**Required:** test-first for `frozen_constants.py` (plain assertion test); test-after /
inspection for `fingerprint_class_coverage_675.py` (research diagnostic, not promoted
logic) — per the handoff's Test Mode section.
**Satisfied:** yes — TDD red→green observed for the frozen-constants test (see TDD
evidence below); the coverage script was run to completion after being written and its
verdict JSON pasted below.

## Evidence

```bash
cd C:/Programs/f1brainz-wt/epic659-666
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" scripts/fingerprint_class_coverage_675.py --slice-db .agent-work/666-driver-fingerprint/artifacts/fp_slice_2023Q.db
```
```json
{
  "generalizes": {
    "time": true,
    "energy": true
  },
  "class_vs_driver_gap": {
    "time": -0.0675,
    "energy": 0.026249999999999996
  },
  "verdict_path": ".agent-work\\666-driver-fingerprint\\artifacts\\coverage_675_verdict.json"
}
```

Full verdict JSON (`.agent-work/666-driver-fingerprint/artifacts/coverage_675_verdict.json`,
local-only, NOT in the diff):

```json
{
  "slice_db": "C:\\Programs\\f1brainz-wt\\epic659-666\\.agent-work\\666-driver-fingerprint\\artifacts\\fp_slice_2023Q.db",
  "n_real_rows": 64,
  "cell_support_real": {
    "LEC|severity:2023:v1:c0": 1361.409910305739, "LEC|severity:2023:v1:c1": 5.110791176739491,
    "LEC|severity:2023:v1:c2": 765.015080359487, "LEC|severity:2023:v1:c3": 90.46421815803444,
    "PER|severity:2023:v1:c0": 1361.409910305739, "PER|severity:2023:v1:c1": 5.110791176739491,
    "PER|severity:2023:v1:c2": 765.015080359487, "PER|severity:2023:v1:c3": 90.46421815803444,
    "SAI|severity:2023:v1:c0": 1361.409910305739, "SAI|severity:2023:v1:c1": 5.110791176739491,
    "SAI|severity:2023:v1:c2": 765.015080359487, "SAI|severity:2023:v1:c3": 90.46421815803444,
    "VER|severity:2023:v1:c0": 1361.409910305739, "VER|severity:2023:v1:c1": 5.110791176739491,
    "VER|severity:2023:v1:c2": 765.015080359487, "VER|severity:2023:v1:c3": 90.46421815803444
  },
  "unresolved_support_floor": 1.0,
  "nominal_coverage_level": 0.8,
  "under_coverage_bound": 0.6,
  "energy_scale": 0.05213894505736354,
  "n_reps": 200,
  "channels": {
    "time": {
      "injected_sigmas": {"driver_sigma": 0.15, "class_sigma": 0.3, "obs_sigma": 1.0},
      "driver": {"empirical_coverage": 0.34875, "ci_lo": 0.3157099365244287, "ci_hi": 0.38290964088718815, "hits": 279, "n": 800, "n_reps": 200},
      "class":  {"empirical_coverage": 0.28125, "ci_lo": 0.2503234007334612,  "ci_hi": 0.31379814449287774, "hits": 225, "n": 800, "n_reps": 200},
      "class_vs_driver_gap": -0.0675,
      "generalizes": true,
      "shared_floor_recommendation": {"recommended": true, "shared_floor": 0.3, "derivation": "shared_floor = class_sigma (this channel's injected between-class effect sigma) -- the naive within-group SEM fit_two_way's companion sigma is built from carries no term for the class-to-class systematic component; floor to that scale in quadrature (per pooling.py's shared_floor semantics) rather than leaving the naive SEM to understate it."}
    },
    "energy": {
      "injected_sigmas": {"driver_sigma": 0.00782084175860453, "class_sigma": 0.01564168351720906, "obs_sigma": 0.05213894505736354},
      "driver": {"empirical_coverage": 0.30875, "ci_lo": 0.276866737276098,  "ci_hi": 0.3420499964963382,  "hits": 247, "n": 800, "n_reps": 200},
      "class":  {"empirical_coverage": 0.335,   "ci_lo": 0.3023276105901509, "ci_hi": 0.36889403037305835, "hits": 268, "n": 800, "n_reps": 200},
      "class_vs_driver_gap": 0.026249999999999996,
      "generalizes": true,
      "shared_floor_recommendation": {"recommended": true, "shared_floor": 0.01564168351720906, "derivation": "shared_floor = class_sigma (this channel's injected between-class effect sigma) -- same reasoning as the time channel."}
    }
  },
  "secondary_loo_real_time_channel": {"empirical_coverage": 0.875, "hits": 56, "n": 64, "level": 0.8},
  "interpretation": "PRIMARY (synthetic-recovery, real support counts): time: driver coverage=0.349 [0.316,0.383], class coverage=0.281 [0.250,0.314] -> GENERALIZES (class under-covers); energy: driver coverage=0.309 [0.277,0.342], class coverage=0.335 [0.302,0.369] -> GENERALIZES (class under-covers). SECONDARY (descriptive, real-data LOO observation coverage, time channel only): coverage=0.875 (56/64) -- measures observation-level predictive coverage on real data, NOT the epistemic class-effect interval coverage the PRIMARY verdict targets; not used for the generalizes flag or the shared_floor recommendation."
}
```

```bash
cd C:/Programs/f1brainz-wt/epic659-666
PYTHONPATH=. "C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/unit/physics/fingerprint/test_frozen_constants.py -q
```
```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: C:\Programs\f1brainz-wt\epic659-666
configfile: pyproject.toml
plugins: anyio-4.13.0, hypothesis-6.152.9, cov-7.1.0, mock-3.15.1
collected 4 items

tests\unit\physics\fingerprint\test_frozen_constants.py ....             [100%]

============================== 4 passed in 0.35s ===============================
```

**Result:** pass — both verification commands from the handoff run foreground and
succeed, reproducibly (re-run a second time immediately before writing this result, same
output).

## TDD evidence, if required
- Failing test observed: `PYTHONPATH=. ...python.exe -m pytest tests/unit/physics/fingerprint/test_frozen_constants.py -q`
  → `ModuleNotFoundError: No module named 'src.physics.fingerprint'` (package did not
  exist yet).
- Passing test observed: same command, after writing `src/physics/fingerprint/__init__.py`
  + `frozen_constants.py` → `4 passed in 0.35s` (pasted above).
- Refactor while green: no refactor needed (small, single-mapping module).

## Docs/contracts touched
- none — no doc file edited; this gate is code + test + diagnostic script only.

## Assumptions
- **Energy-channel injected sigmas:** `ENERGY_SCALE = std(deployment_share) / std(time_deficit_s)`
  computed once from the 64 real severity-class rows (= 0.052139...). Applied uniformly
  to scale #665's time-channel sigma triple (`driver_sigma=0.15, class_sigma=0.30,
  obs_sigma=1.0`) onto the energy channel (`0.00782, 0.01564, 0.05214` respectively) —
  preserves the SAME relative structure #665 uses, rescaled to the energy channel's own
  real magnitude (deployment_share's spread is ~19x smaller than time_deficit_s's).
  Stated in the script's module docstring ("Energy-channel sigma derivation").
- **shared_floor derivation:** `shared_floor = class_sigma` for that channel (0.30 for
  time, 0.01564 for energy) — reasoned as: `fit_two_way`'s naive companion SEM is a
  within-group MEASUREMENT-noise-only quantity and carries no term for the class-to-class
  systematic component; flooring to the injected class_sigma's own scale in quadrature
  (mirroring `pool_random_effects`'s `shared_floor` semantics in `pooling.py`) is the
  natural size for the missing term. This is a diagnostic-only recommendation from
  synthetic ground truth; the commander adjudicates the actual G3 value.
- **Cell resolution:** a (driver, class) cell's real support (`n_points` summed across
  the 4 circuits) is rounded to the nearest int for the synthetic draw count; a cell
  below `FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR` (1.0) is treated as unresolved/excluded
  (0 synthetic draws) — none of the 16 real cells in this slice fell below that floor
  (min real support ≈5.11 laps' worth, `LEC|severity:...:c1`), so this floor had no
  effect on THIS run's numbers but is implemented and exercised in code.
- **Secondary/LOO scale:** used `sqrt(pool.var_resid)` from the training refit as the
  predictive scale (rather than a per-cell naive SEM), since the secondary measure is
  explicitly descriptive/observation-level, not the epistemic axis-effect measure the
  PRIMARY verdict requires.

## Stop conditions hit
- None. The slice DB was present and well-formed (64 rows, 4 drivers × 4 severity
  classes × 4 circuits, matching the handoff's description); the #665 method was
  reproducible faithfully with `fit_two_way`/`predictive_t` used unmodified; no
  constant needed a value other than the 4 pre-registered ones; no forbidden file needed
  editing.

## Out-of-scope observations
- **Driver axis under-covers almost as badly as the class axis in THIS bounded slice.**
  Time channel: driver coverage 0.349 [0.316,0.383] vs class 0.281 [0.250,0.314] (driver
  is actually WORSE here, gap −0.0675). Energy channel: driver 0.309 [0.277,0.342] vs
  class 0.335 [0.302,0.369] (gap +0.026, class only marginally worse). I verified
  analytically (not a code bug) that this is expected: #665's original harness used all
  ~20 real F1 drivers (giving the driver axis many group-levels and good calibration)
  and only k=4 classes (poorly calibrated) — hence #665 found the miscalibration
  class-specific. This #675 diagnostic's bounded slice restricts BOTH axes to k=4
  (4 drivers × 4 severity classes, per the handoff's fixed entity set), so the SAME
  "few-groups" pathology (the naive within-group SEM never captures the estimated
  grand-mean's own reference uncertainty, which scales as σ/√(#groups), not
  1/√(observations)) now hits the driver axis too. Per the pre-registered rule, the
  `generalizes` flag is defined ONLY on the class axis's CI-upper vs
  `FINGERPRINT_UNDER_COVERAGE_BOUND`, and it fires `true` for both channels exactly as
  specified — I did not alter the rule. But the commander should read `generalizes:true`
  here as "the class axis fails the 0.60 gate," NOT as "only the class axis is
  miscalibrated" — the driver axis fails a symmetric gate too in this particular 4×4
  bounded slice. Whether G3's `shared_floor` fix should also cover the driver axis (or
  whether the real production driver axis, with more than 4 real drivers, would recover
  its calibration) is a genuine open question for the commander/G3, not something I
  resolved or am positioned to resolve from this diagnostic alone (test scope: THIS
  bounded 4-driver slice only, not the full-grid production case — a scoped null, not a
  class-spanning claim).
- **`.gitignore` does not actually cover the verdict JSON.** `git check-ignore` on
  `.agent-work/666-driver-fingerprint/artifacts/coverage_675_verdict.json` exits 1 (NOT
  ignored) — only `.agent-work/**/*.db` (etc.) patterns exist, not a `.json` pattern, so
  the `.db` slice input IS covered (exit 0) but the `.json` verdict is not. I did not
  stage or commit it (no `git add` was run), so the constraint is honored in practice,
  but a future careless `git add -A` in this worktree would pick it up. Flagged as a
  triage candidate; not fixed here since editing `.gitignore` was outside this gate's
  Allowed Scope.

## Workflow Feedback
- **Handoff gaps:** none — the handoff's coverage-method pin (n_eff semantics, real
  support-count allocation, energy-channel scope for implementer discretion) was precise
  enough to implement without needing to guess; the one place I made an explicit choice
  (energy sigmas, shared_floor derivation) was correctly flagged as mine to decide and
  state.
- **Context rediscovered:** none beyond the ordinary read of `pooling_imbalance_validation_665.py`,
  `student_t.py`, and `pooling.py` that the handoff already pointed at directly.
- **Instructions improvised around:** the plan template's `m1` example step names a
  single TDD slice; I split the work into 3 implementation slices (m1 frozen-constants,
  m2 coverage-script, m3 verify-and-close) rather than 1, since the coverage script's
  test mode (test-after/inspection) genuinely differs from the frozen-constants test's
  mode (test-first) and conflating them into one item would have hidden that TDD-vs-
  inspection distinction from the engine's own gating. This felt like the intended use
  of "one item per implementation step," not a deviation.
- **What would have made this easier:** none — the handoff's exact pinning of the
  coverage method (down to `n_eff` semantics and the binomial-CI requirement) was
  unusually load-bearing-precise and made this a straightforward-if-careful build; no
  concrete gap to report beyond the `.gitignore` triage candidate above.

## Return status
`complete`
