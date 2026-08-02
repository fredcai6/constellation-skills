# Implementation Result — G2 (log-space property mixture + support-driven-k fix, #638)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g2-implement` — rework the Phase-1 corner property-class mixture so the F12 held-out-circuit
stability gate earns a GENUINE (non-gamed) PASS, by fixing the MODEL (log-radius fit space +
absolute-count support arm + domain-capped k ceiling + log-space gate normalization).

## Completed slice
All four commander-decided choices implemented EXACTLY as pre-registered in DIAGNOSIS.md /
the handoff, across 3 vertical slices driven through the engine:
- **m1** — `property_mixture.py` fits in `(log10(radius_m), lateral_g)` space via an
  encapsulated helper (`_to_log_space`), applied in BOTH `fit_property_mixture` (before
  `scaler.fit`) and `posterior_membership` (before `scaler.transform`); OR support criterion
  (`weight >= 0.05` OR `weight*N >= 150`); `k_range` default `(2, 4)`. Tests rewritten for log
  space + new large-N and mechanical support-driven-k tests.
- **m2** — `mixture_stability.py` normalizes the radius axis by `LOG_RADIUS_SCALE = 0.30`
  (renamed from `RADIUS_SCALE_M`); `LATERAL_G_SCALE`, `F12_AGREEMENT_THRESHOLD`, Hungarian
  match, k-mismatch→inf auto-fail all UNCHANGED. Discriminating test rewritten to shift
  MULTIPLICATIVELY in radius (still stable→PASS / shifted→FAIL, still able-to-fail).
- **m3** — `scripts/f12_held_out_stability.py` import/print reconciled
  (`RADIUS_SCALE_M`→`LOG_RADIUS_SCALE`, JSON key `radius_scale_m`→`log_radius_scale`); full
  layer2 suite + simplification-limits run.

## Scope
**Files changed:**
- `src/physics/layer2/property_mixture.py` — log fit space, `_to_log_space`,
  `MIN_COMPONENT_SUPPORT_COUNT=150`, OR support criterion, `k_range` default `(2,4)`.
- `src/physics/layer2/mixture_stability.py` — `RADIUS_SCALE_M`→`LOG_RADIUS_SCALE=0.30`,
  `_normalize` + docstrings updated; all other gate logic untouched.
- `tests/unit/physics/layer2/test_property_mixture.py` — log-space fixtures; new
  `MIN_COMPONENT_SUPPORT_COUNT` pin, large-N-no-over-select, mechanical support-driven-k
  (up/down + tiny-cluster floor-reject + count-arm-keeps-<5%-but->=150).
- `tests/unit/physics/layer2/test_mixture_stability.py` — log-space fixtures + imports;
  multiplicative-shift discriminating scenario; k-mismatch fixture reconciled.
- `scripts/f12_held_out_stability.py` — import/print/JSON-key rename only (no logic change).

**Specific exclusions touched:** `no` — `corner_descriptors.py`, `regime_rollup.py`,
`segment_classifier.py`, `build_regime_rollup.py` logic all UNCHANGED (their raw-descriptor
callers keep working via the encapsulated log transform; verified green, see Evidence).
`F12_AGREEMENT_THRESHOLD` and the k-mismatch auto-fail unchanged (gate not weakened).

## Behavior changed
`yes` — the property mixture now fits in log-radius space and a component is "supported" if it
clears EITHER the 0.05 relative floor OR the 150-observation absolute floor; the F12 gate
compares component locations in log10-radius units. Public API shape (`MixtureFit` fields,
`fit_property_mixture`/`posterior_membership` raw-descriptor signatures) is unchanged.

## Frozen constants + rationale comments (all pre-registered before any post-fix real run)
- `MIN_COMPONENT_WEIGHT_FRAC = 0.05` — UNCHANGED relative support arm (kept, per handoff).
- `MIN_COMPONENT_SUPPORT_COUNT = 150` (property_mixture.py) — absolute-count support arm.
  Rationale comment: 150 ≈ 30 observations per estimated Gaussian parameter (2D full-cov
  component = 5 params); "support" is fundamentally an absolute-count question, and the
  relative 5% floor is composition-brittle at F1 scale (a real 12,097-obs class was rejected
  only for being 4.27% < 5%). Supported ⟺ clears EITHER arm.
- `k_range` default `(2, 4)` (property_mixture.py) — ceiling 4 = physically-motivated max
  corner-severity classes (tight/medium/fast/very-fast); k stays support-driven within range.
- `LOG_RADIUS_SCALE = 0.30` (mixture_stability.py) — adjacent corner classes ~factor-2 apart
  in radius, log10(2) ≈ 0.30; the log-space mirror of the old raw `RADIUS_SCALE_M=50`
  order-of-magnitude rationale. Frozen from domain reasoning, not tuned to a result.

## Map Impact
- **Structural anchors touched:** `struct: property_mixture.py::fit_property_mixture` (added
  `_to_log_space` helper; new fit space + OR support criterion + k ceiling),
  `mixture_stability.py::_normalize`/`component_agreement_stat` (log-radius normalization).
- **Capabilities affected:** `capability: property-mixture-fit` (now log-radius, absolute
  support arm) and `capability: f12-holdout-stability` (compares in log-radius units) — both
  observable via the unit suites; the real 5/5 confirmation is G3's job (not run here).
- **Constraints touched:** `constraint: support-driven k` honored (k mechanically responds to
  structure — new test); `constraint: F12 falsifiable` honored (discriminating test still
  FAILs on shifted data); `constraint: physics_region_no_evo_import` honored (no evo import).
- **Decision anchors:** implements the DIAGNOSIS.md fix decision (log space + OR-support +
  cap-4 + log gate scale); `decision:regime_readiness_rubric` (#512) context unchanged.
- **Trust limitations / drift found:** `docs/architecture/packets/physics.md:979` still
  documents the gate's normalization as `RADIUS_SCALE_M = 50` — now stale. OUT OF SCOPE for
  this gate (Cartographer map doc); flagged for reconcile (see Triage candidates).

## Test mode
**Required:** `test-after` (fast synthetic/unit tests; NO real DB).
**Satisfied:** `yes` — synthetic unit tests only; the ~6-min real-data F12 was NOT run (G3).

## Evidence

### Verification command 1 — editable-install `.pth` trap guard (import resolves to worktree)
```bash
cd /c/Programs/f1-638 && PYTHONIOENCODING=utf-8 py -c "import src.physics.layer2.property_mixture as m; print(m.__file__)"
```
**Result:** pass — `C:\Programs\f1-638\src\physics\layer2\property_mixture.py` (under the worktree).

### Verification command 2 — the two changed-file unit suites
```bash
cd /c/Programs/f1-638 && PYTHONIOENCODING=utf-8 py -m pytest tests/unit/physics/layer2/test_property_mixture.py tests/unit/physics/layer2/test_mixture_stability.py -q
```
```
collected 23 items
tests\unit\physics\layer2\test_property_mixture.py ...............       [ 65%]
tests\unit\physics\layer2\test_mixture_stability.py ........             [100%]
============================= 23 passed in 11.50s =============================
```
**Result:** pass (23 passed).

### Verification command 3 — simplification limits on both touched src paths
NOTE: the handoff's positional form errors (argparse); the CLI requires `--paths`
(confirmed by `docs/agents/CREW_CONTEXT.md`). Ran the `--paths` form:
```bash
cd /c/Programs/f1-638 && PYTHONIOENCODING=utf-8 py -m src.utils.simplification_limits --paths src/physics/layer2/property_mixture.py src/physics/layer2/mixture_stability.py
```
```
PASS (2 files checked)
```
**Result:** pass.

### Caller-regression surface (direct callers of the changed modules)
```bash
cd /c/Programs/f1-638 && PYTHONIOENCODING=utf-8 py -m pytest tests/unit/physics/layer2/test_regime_rollup.py tests/unit/physics/test_segment_classifier.py tests/unit/physics/layer2/test_corner_descriptors.py -q
```
```
tests\unit\physics\layer2\test_regime_rollup.py ..................       [ 54%]
tests\unit\physics\test_segment_classifier.py ......                     [ 72%]
tests\unit\physics\layer2\test_corner_descriptors.py .........           [100%]
============================= 33 passed in 28.08s =============================
```
**Result:** pass (33 passed) — `regime_rollup` + `segment_classifier` + `corner_descriptors`
all green via the encapsulated log transform; no caller regression.

### Broader layer2 suite (no caller regressions) — full dir
```bash
cd /c/Programs/f1-638 && PYTHONIOENCODING=utf-8 py -m pytest tests/unit/physics/layer2/ -q
```
```
================ 685 passed, 2 warnings in 3358.60s (0:55:58) =================
```
**Result:** pass (685 passed, exit 0). Full `tests/unit/physics/layer2/` dir green — no
caller regressions anywhere in layer2. (Long wall-time is CPU contention with concurrent
sibling-agent test runs, not the change; the 33-test caller surface above ran in ~28s.)

## Confirmation the discriminating test still FAILs on shifted data
`TestCheckHoldoutStabilityDiscriminating::test_shifted_generator_two_circuits_gives_fail`
asserts `result.headline_verdict == "FAIL"`, `result.n_pass == 0`, and
`result.max_statistic > F12_AGREEMENT_THRESHOLD` — and PASSES (shown in command #2 above,
8/8 in test_mixture_stability). The shift is multiplicative in radius (100x = log10 gap of 2,
normalized 2/0.30 ≈ 6.7 per matched pair) plus a lateral shift, so it exceeds the 1.0
threshold in the gate's log-radius comparison space. The same-generator scenario PASSES. The
check is still able to FAIL; the gate was not weakened.

## TDD evidence
Test mode is test-after: tests were rewritten/added alongside the change and observed green
(commands above). No red-first step required.

## Docs/contracts touched
- `docs/architecture/packets/physics.md` — NOT edited (out of scope; stale `RADIUS_SCALE_M`
  reference flagged for Cartographer, see Triage candidates).

## Assumptions
- `_to_log_space` assumes strictly-positive `radius_m` (upstream `corner_descriptors` derives
  `radius = v_mean^2 / (mu_lat_p90 * g)` with `mu_lat_p90 > 0`; degenerate zero/negative radii
  are an upstream data defect, not guarded here — consistent with the module's existing
  fail-visibly posture and no new guard requested).
- k_range ceiling 4 is applied as the default; callers passing an explicit range still control
  it (the gate and callers use the default).

## Stop conditions hit
- `none` — no frozen constant appeared wrong; no excluded file needed changing; the region
  suites go green without weakening the gate; the discriminating test stayed able-to-fail.

## Out-of-scope observations / Triage candidates
- `docs/architecture/packets/physics.md:979` documents the F12 gate normalization as
  `RADIUS_SCALE_M = 50` (raw metres). After #638 this is `LOG_RADIUS_SCALE = 0.30` (log10).
  Cartographer reconcile should update the packet. (Map doc — out of this gate's scope.)

## Workflow Feedback
- **Handoff gaps:** Verification command 3 (`py -m src.utils.simplification_limits <paths>`
  positional) is WRONG — the CLI rejects positional paths (`unrecognized arguments`) and
  requires `--paths`. `docs/agents/CREW_CONTEXT.md` documents the correct `--paths` form. The
  handoff copied the positional form verbatim; I used `--paths` and noted it.
- **Context rediscovered:** The handoff said "run the broader layer2 suite" but the full
  `tests/unit/physics/layer2/` dir is 685 tests (mostly unrelated physics/estimation suites:
  stint estimators, pooling, damage, views) that take a long time under concurrent-agent CPU
  contention. The actual caller-regression surface is just `test_regime_rollup` +
  `test_segment_classifier` + `test_corner_descriptors` (33 tests, ~28s) — which I ran
  directly and green. A narrower "caller-regression command" in the handoff would have been
  more tractable than the whole dir.
- **Instructions improvised around:** none beyond the two above — confirmed after review: the
  engine plan drove cleanly (attest-precondition → start → advance per gate).
- **What would have made this easier:** fix the simplification-limits command to `--paths`
  form in the handoff template, and point the broader-suite check at the specific caller test
  files rather than the whole 685-test layer2 dir.

## Return status
`complete`
