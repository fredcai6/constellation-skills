# Implementation Result — g3-replication-implement

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3-replication-implement` (#668 instrument panel, epic #659) — the LOAD-BEARING instrument.

## Completed slice
Built Instruments 2 + 3 in `src/physics/instrument_panel/replication.py` (pure, synthetic-tested,
F12-independent) plus its falsifier suite:

1. **Golf-correction = DOUBLE-CENTERING** — `grand_two_way_center(grid)` computes the two-way
   ANOVA interaction residual `residual[d,c] = v[d,c] − driver_mean[d] − class_mean[c] + grand_mean`,
   a pure arithmetic data transform (no fitted parameter, no interaction model term — owner ruling 4).
   `per_driver_demean(grid)` (removes ONLY the driver main effect) is provided solely as the WRONG
   correction for the negative control. `interaction_replication_r(grid_a, grid_b, *, center=…)`
   correlates the double-centered per-driver interaction-residual profile across the shared
   (driver,class) cells between two halves; `center` is injectable.
2. **Injected thresholds + r_floor** — `ReplicationThresholds(threshold, min_support_n, r_floor_cap,
   r_floor_support_ref, channel_tie_margin)` frozen dataclass; `r_floor(n, thresholds)` implements the
   registered support-scaling. NO frozen `REPLICATION_*` import (not minted; G6 wires it). Tests inject
   the proposal defaults (0.5 / 15.0 / 0.7 / 100.0 / 0.1).
3. **Per-class channel comparison** — `CellValue(driver, class_id, value, support)` observations;
   `compare_channels_by_class(channel_halves, thresholds)` returns a per-class `ClassChannelVerdict`
   (resolved+winner / unresolved / unmeasurable). The split is INJECTED (core takes two pre-split
   halves per channel), so cross-circuit 2v2 and lap-parity both plug in with no code change. Tie-break
   channel is read from `FINGERPRINT_CHANNELS[0]` ("utilization"), not a baked literal.
4. **OUT-OF-SAMPLE σ-honesty** — `CoverageCheck`, `CoverageReport`, `build_predictive`,
   `out_of_sample_coverage`. The estimate (mu/sigma/n_eff from the training half) NEVER sees the
   held-out value; interval built with `predictive_t(…, nu_loss=DEFAULT_NU_LOSS, rule=FormulaRule())`
   (Student-t, non-Gaussian — owner ruling 5).

## Scope
**Files changed:**
- `src/physics/instrument_panel/replication.py` (NEW)
- `tests/unit/physics/instrument_panel/test_replication_channel.py` (NEW; synthetic generator lives in the test file, per allowed scope)

**Specific exclusions touched:** no. No real DB / `f1_data_*.db` read or touched (`git status --short data/`
empty). No frozen `REPLICATION_*` import. No `join.py` routing. No #660/#664/#666/#667 producer touched.
`scripts/pooling_imbalance_validation_665.py` was NOT modified — its additive generative model is extended
(with the true driver×class interaction term) in the test file, as the allowed scope directs.

## Behavior changed
Yes — new capability: a golf-corrected split-half replication instrument that measures driver-utilization
reproducibility, discriminates it from overall-skill and shared-class artifacts, sizes it per class per
channel, and reports out-of-sample σ-calibration. It SIZES; it never gates.

## Map Impact
- **Structural anchors touched:** new module `src/physics/instrument_panel/replication.py` (sibling to
  `variance_decomposition.py`); reuses `src/common/student_t.py` (`predictive_t`) and
  `src/physics/fingerprint/address.py` (`FINGERPRINT_CHANNELS`) read-only.
- **Capabilities added:** driver-utilization measurement — replication sizing (golf-corrected split-half r)
  + per-class channel selection + out-of-sample σ-honesty coverage.
- **Constraints honored:** `constraint:lowest-dimensionality` (no new model params — pure data transform);
  `constraint:no-baked-normality` (Student-t predictive); `constraint:no-frame-kill` (unmeasurable/
  unresolved are COMPLETE verdicts; a fully support-filtered class still returns `unmeasurable`).
- **Decision anchors realized:** `decision:golf-correction-is-DOUBLE-CENTERING` — implemented as the
  two-way interaction residual on raw observations, proven necessary vs per-driver-demean.
- **Claims/evidence produced:** `claim:golf-correction-removes-skill` (3-arm + negative control);
  `claim:coverage-is-distribution-not-gaussian` (heavy-tail path exercised); σ-honesty out-of-sample.

## Test mode
**Required:** test-first (TDD red→green each slice).
**Satisfied:** yes — each slice observed RED (m1 ModuleNotFound; m2/m3 ImportError on new symbols;
m2 additionally surfaced a real `KeyError` no-frame-kill gap that drove a fix) then GREEN.

## Evidence

### LOAD-BEARING 1 — 3-arm falsifier + negative control (all pass)
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest \
  tests/unit/physics/instrument_panel/test_replication_channel.py -q
# 18 passed in 3.35s
```
Measured r values (deterministic, seeded):
- arm (a) pure overall-skill, double-centered r = **0.011** (≈0 → does NOT replicate)
- arm (b) pure shared-class, double-centered r = **0.0006** (≈0 → does NOT replicate) — the distinguishing arm
- arm (b) pure shared-class, **per-driver-demean-only r = 0.685** (HIGH → FLATTERS)
- arm (c) injected interaction, double-centered r sweep = **0.063 → 0.738 → 0.917 → 0.978** (monotone in strength, clears threshold 0.5)

**The negative-control assertion (quoted from `test_negative_control_per_driver_demean_fails_arm_b`):**
```python
# double-centering: the shared-class artifact is GONE -> no replication
assert abs(r_double) < _NULL_R_MAX          # 0.0006 < 0.2   PASS
# per-driver-demean-ONLY: the shared-class artifact FLATTERS a high r
assert r_demean > _STRONG_R_MIN             # 0.685 > 0.6    PASS
# and the gap is large -- the two corrections are not interchangeable
assert r_demean - abs(r_double) > 0.4       # 0.684 > 0.4    PASS
```
This proves per-driver-demean-ONLY FAILS arm (b) (reports HIGH r on pure shared-class), so the falsifier
genuinely discriminates and double-centering is load-bearing, not cosmetic.

### LOAD-BEARING 2 — σ-honesty detects understated σ out-of-sample
- correct stated σ → empirical coverage **0.906 ≈ nominal 0.90** (within CI band)
- understated σ (0.35×) → empirical coverage **0.504**, materially below nominal (detected)
- heavy-tail path (n_eff=1): nu=**3.5** (< DEFAULT_NU_LOSS=4), interval half-width **4.16 > 1.96·scale=2.77**
  → Student-t, NOT ±1.96σ Gaussian.

### LOAD-BEARING 3 — pyright-0 on the new module
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pyright src/physics/instrument_panel/replication.py
# 0 errors, 0 warnings, 0 informations
```

### Confirmatory — channel-comparison decision paths
winner (util r=1 beats energy r=0 by margin), tie-default→utilization (both r=1 within margin),
unresolved (both r=0 < floor), unmeasurable (support<15 filtered; and <2 resolved drivers) — all green.
`r_floor` math: base 0.5 at n≥100, cap 0.7 at n=0, 0.65 at n=25, monotone non-increasing in support.

**Result:** pass (18/18 in the file; 25/25 across the instrument_panel dir — g2 sibling intact).

## TDD evidence
- Failing test observed: m1 `ModuleNotFoundError: No module named 'src.physics.instrument_panel.replication'`;
  m3 `ImportError: cannot import name 'CoverageCheck'`; m2 `KeyError 'c0'` (real no-frame-kill defect).
- Passing test observed: full file 18 passed; per-slice `-k` subsets green at each advance.
- Refactor while green: m1 arm-r stabilized by averaging r over 25 independent split-half noise draws
  (the pre-registered "average r over partitions" — a null arm's single-split sampling scatter, 0.365 on
  one unlucky seed, collapses to ≈0.01 when averaged).

## Docs/contracts touched
- None beyond the new module's own docstrings.

## Assumptions
- **The interaction-residual replication correlation spans CLASSES** (the per-driver profile over the
  (driver,class) cells), not a single-class across-drivers vector. This is the crux resolution: only a
  cross-class correlation exposes the shared-class artifact that per-driver-demean leaves behind — an
  across-drivers-within-one-class r is invariant to class-centering and could not make the negative
  control discriminate. Documented in the module and flagged below.
- Double-centering on a ragged/unbalanced grid uses unweighted one-pass main-effect means (exact ANOVA
  residual on a balanced grid; honest additive centering otherwise — introduces no model parameter).
- Exactly one `CellValue` per (driver,class) per half (the split unit aggregates its circuits upstream).
- The σ-honesty synthetic world is itself Student-t (drawn from the true predictive), consistent with
  owner ruling 5, so correct-σ coverage lands at nominal rather than the over-coverage a Gaussian world
  would produce against t intervals.

## Stop conditions hit
- None. No real-DB / frozen-module import was needed; the negative control DID fail arm (b) as required
  (the correction is correct); no interaction MODEL term was required (double-centering is a data transform).

## Out-of-scope observations
- None requiring triage. (G6 will wire the frozen `REPLICATION_*` values into `ReplicationThresholds`;
  the caller-side partition averaging over the 3 distinct 2v2 partitions is left to the caller per the
  handoff — the core takes two halves.)

## Workflow Feedback
- **Handoff gaps:** the split-half r description — *"per-driver interaction-residual profile … (correlation
  across drivers)"* combined with *"Per class"* — reads as an across-drivers-within-one-class correlation,
  but that reading CANNOT satisfy the load-bearing negative control: subtracting the class mean is a
  constant across drivers within a class, so double-centering and per-driver-demean give identical
  per-class-across-drivers r, and a pure-shared-class arm is ≈0 under BOTH. The only reading under which
  per-driver-demean FLATTERS arm (b) (as the handoff demands) is a correlation that SPANS classes. I
  resolved in favor of the negative-control requirement (the stated crux) and made the primary
  interaction-replication r a cross-class/cell correlation; the per-class channel-comparison r is a
  separate across-drivers-within-class quantity. Recommend the handoff state explicitly that the
  replication profile spans classes.
- **Context rediscovered:** the exact `predictive_t` construction (scale = σ·√(1+1/n_eff), nu = min(nu_loss,
  nu_prior+k·n_eff)) mattered for making correct-σ coverage land at nominal — had to read `student_t.py` to
  see the world must be t(nu_loss), not Gaussian, for that. The handoff's `predictive_t` pointer was enough
  to find it but the calibration subtlety was not called out.
- **Instructions improvised around:** none material — the engine plan template and slice discipline fit.
- **What would have made this easier:** one sentence in the handoff pinning that the replication correlation
  spans classes (or a worked micro-example of the negative control's arithmetic).

## Return status
`complete`
