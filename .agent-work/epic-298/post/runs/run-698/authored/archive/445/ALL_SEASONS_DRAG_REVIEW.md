# ALL-SEASONS ERA-AWARE DRAG REVIEW

**Reviewer:** Independent (fresh eyes, read-only)
**Scope:** `src/physics/regulation_era.py` (new), `src/physics/parameter_estimator.py` (modified), `src/physics/__init__.py` (export), tests in `tests/unit/physics/test_regulation_era.py`
**Verdict:** APPROVE-WITH-NITS

---

## Test run result

```
py -m pytest tests/unit/physics tests/regression/test_physics_regression.py tests/integration/test_preprocessor_physics_interface.py tests/integration/test_physics_pipeline.py -q
295 passed, 10 skipped in 10.92s
```

All 16 new regulation-era tests pass. No regressions.

---

## CRITICAL SAFETY PROPERTY: Is coast provably never used for theta_D in ≥2014 / era=None?

**YES — provably safe.** The gate is at line 91:

```python
use_coast_for_drag = era is not None and era.coast_drag_trustworthy
```

`coast_drag_trustworthy = not mguk_regen`. For `era=None` this expression short-circuits to `False`. For any season ≥ 2014 `mguk_regen=True` → `coast_drag_trustworthy=False` → `use_coast_for_drag=False`.

The coast branch on line 175 is `elif use_coast_for_drag and coast_theta_D is not None:`. When `use_coast_for_drag=False` this elif is **never entered** regardless of the value of `coast_theta_D`. The coast theta_D is still *computed* (lines 99-126) but it is not *consumed* in hybrid/None paths.

There is NO path by which a ≥2014 or `era=None` session gets `theta_D_source="coast"`. The safety property holds by code structure, not convention.

`theta_R` from coast is used in all eras (lines 168-173, also in the fallback-longitudinal case where it is simply the prior). This is correct: coast `theta_R` is not regen-contaminated (the constant-regen offset was absorbed into the coast `theta_R` intercept in Phase 0, but the engine never uses coast `theta_R` as the drag estimate — it's a rolling diagnostic regardless of era).

---

## Numbered Findings

### FINDING 1 — BLOCKER (safety-adjacent bug): ZeroDivisionError when theta_D == 0.0

**Files:** `src/physics/parameter_estimator.py` lines 153 and 192

Both plausibility blocks execute `fit_D_std / abs(fit_D)` as Python float division. If `fit_D == 0.0` (possible on degenerate synthetic data, or from `fit_drag_rolling` on a perfectly flat speed segment), `abs(0.0) == 0.0` and Python raises `ZeroDivisionError`. The `fit_D < 0` guard immediately before does NOT catch `fit_D == 0.0`.

This affects both the throttle path (line 153) and the coast path (line 192). The pre-2014 synthetic fixture in the tests is designed with a non-zero CdA, so it does not hit this case. No test covers `theta_D == 0`.

**Fix:** change `fit_D_std / abs(fit_D)` to `fit_D_std / max(abs(fit_D), 1e-12)` in both places, or add `elif fit_D == 0.0: implausible = True; fallback_reason_long = "zero_theta_D"` before the SNR check.

**Severity:** BLOCKER — uncaught exception in production if a degenerate fit returns zero drag.

---

### FINDING 2 — NIT (inaccurate comment): covariance assembly comment is throttle-centric

**File:** `src/physics/parameter_estimator.py` lines 226–228

Comment reads: "theta_D variance from the throttle fit, theta_R variance from the coast diagnostic." In the coast path (`theta_D_source="coast"`) `theta_D_std` comes from `fit_drag_rolling`, not the throttle fit. The comment is correct only for the throttle path.

**Fix:** Generalize: "theta_D variance from the active drag fit (throttle or coast), theta_R variance from the coast diagnostic. Cross term is 0 (independent regimes)."

---

### FINDING 3 — NIT (subtle limitation, undocumented): implausible throttle blocks coast fallback in pre-2014 era

**File:** `src/physics/parameter_estimator.py` lines 139-174 vs 175

When `throttle_fit is not None` but is implausible (e.g. negative theta_D), the `if` block at line 139 executes with `fallback_longitudinal=True`, then control falls to the `else` on line 212. The `elif use_coast_for_drag ...` at line 175 is **never evaluated** in this case.

This means: for a 2012 session where `fit_drag_throttle` returns a non-None result with a negative theta_D (plausible on short-lap / low-speed synthetic data), the clean coast data is not consulted — the engine goes straight to full fallback.

The design document's intent is ambiguous here ("throttle fit succeeds + passes plausibility → use it; throttle None AND coast_trustworthy → use coast"). The current code matches the stated priority ("if throttle non-None, always use it or fall back — don't cascade to coast"), which is defensible, but creates a scenario where pre-2014 sessions lose the coast path due to a non-None but implausible throttle fit.

**Recommendation:** Document this explicitly in the code comment (one sentence: "Note: an implausible-but-non-None throttle fit blocks the coast fallback in all eras.") and add a test that exercises this case for pre-2014.

---

### FINDING 4 — DESIGN OBSERVATION (not a defect): throttle-preferred in 2011-2013

The design prefers throttle-DRS even in 2011-2013 (coast is the fallback, not the primary). The design document's table says 2011-2013 should use "coast-drag (cleaner: power-free, no degeneracy)" — but that was written for the case where DRS data is available on both paths. The current implementation uses coast only when throttle returns `None` (no DRS lever, or insufficient bins). For a 2012 session WITH DRS-open samples, the throttle path wins.

This is operationally safe (the throttle path has SNR gating and plausibility checks) but deviates from the design document's stated hierarchy. The design doc is pre-implementation thinking; the current code's approach (throttle-first, coast-fallback) is internally consistent and produces correct results for the tested synthetic case. However, the deviation from the design table is not acknowledged anywhere in the code.

**Recommendation:** Add a one-line comment near `use_coast_for_drag` explaining that throttle-DRS takes priority even in ≤2013 because it is the validated path when a DRS lever is available, with coast reserved for sessions without any DRS-open data.

---

### FINDING 5 — PROCESS: 2024 blessed fixtures are NOT byte-identical; they have been re-blessed

The integration plan document says "2024 blessed fixtures (Spain/Monza/Monaco) byte-identical — `era=None` default path is unchanged."

**This claim is incorrect.** `git status` shows all three `blessed_params.json` files are modified relative to HEAD, and `git diff` confirms substantial changes (e.g. Monza: `theta_D` 0.001→0.000627, `fallback_longitudinal` 1.0→0.0, `n_samples_used` 1695→652, `mean_theta_P` 300.0→608.9). The `processed_telemetry.parquet` files are also modified (calibration port + a_long fix).

The re-bless is *legitimate* — it is documented in the calibration port and a_long fix sections of the integration plan — but the "byte-identical" claim in the all-seasons section is stale. The all-seasons era-aware change itself does not re-bless the fixtures, but the fixtures are not in the same state as when the all-seasons claim was written (the a_long fix and calibration port re-blessed them first).

**Impact:** The "byte-identical" regression guarantee for the all-seasons feature is not verifiable in isolation because it cannot be separated from the calibration-port + a_long-fix bless. This is a review paperwork issue, not a code correctness issue.

---

### FINDING 6 — ABSTRACTION QUALITY: RegulationEra is clean and genuinely extensible

`RegulationEra` is a well-designed hook. The frozen dataclass pattern (all flags computed in `__post_init__` via `object.__setattr__`) correctly prevents mutation while supporting derived fields. The `coast_drag_trustworthy` property as `not mguk_regen` is clean and self-documenting.

The extension pattern in the docstring is concrete and actionable: it shows both the field declaration (with `field(init=False)`) and the `__post_init__` assignment line, with real F1-physics examples (`ground_effect`, `kers`). The downstream consumption pattern in `parameter_estimator.py` is shown. The validation note (synthetic-only) is honest and prominently placed.

**Minor gap:** There is no guard for nonsensical input (e.g. `season=1900` or `season=-1`). The constructor accepts any int. An assertion or `ValueError` for `season < 1950` would prevent silent misuse, though current callers are all well-typed.

---

### FINDING 7 — TEST RIGOR: routing tests are sound; coast recovery test is adequate; SNR gate coverage has a gap

- `TestRegulationEraFlags` (9 tests): boundary years 2010/2011/2012/2013/2014/2024 all explicitly tested. Frozen-dataclass mutation test present. The parametric loop over 2005–2026 for `coast_drag_trustworthy == not mguk_regen` is a useful invariant check.
- `TestEraAwareDragRouting` (3 tests): pre-2014 → "coast", modern → "throttle_drs_joint", `era=None` → same as 2024. All assert `theta_D_source` and `fallback_longitudinal`. The `era=None` test additionally checks that `theta_D` is numerically identical between the two modern paths (rel=1e-9), which is a strong identity check.
- `TestCoastPathKnownAnswer`: uses `np.gradient(speed_ms, t_s)` for `a_longitudinal` (the physics-integrated speed approach is correct), recovers CdA to <5% and theta_R to <10%. Adequately validates the coast path mechanically.
- `TestSNRGateBothPaths`: mock-injects a high-rel-sigma coast fit and verifies fallback with correct reason. The "good fit passes" test exercises the clean synthetic data. This is adequate.
- **Gap:** No test covers `theta_D == 0.0` (Finding 1). No test covers "implausible non-None throttle blocks coast in pre-2014" (Finding 3).

---

## Summary

**Verdict: APPROVE-WITH-NITS**

**Safety property (item 1): CONFIRMED.** Coast theta_D can NEVER reach a ≥2014 or `era=None` session. The `use_coast_for_drag` gate is structurally correct and double-gated (`era is not None` AND `era.coast_drag_trustworthy`). The only finding touching the safety boundary is Finding 3 — an implicit limitation that is not a safety violation but is undocumented.

**Blocker:** Finding 1 (ZeroDivisionError on theta_D == 0.0) is the only BLOCKER. It affects both drag paths and has no test coverage.

**Abstraction quality (item 6): GOOD.** `RegulationEra` is a genuine, extensible hook — not a thin one-off. The docstring's extension guidance is concrete (shows exact field declaration and post_init lines). The only gap is no input validation for obviously nonsensical season years.

**Remaining findings are nits** (comment accuracy, implicit behavior of implausible-non-None throttle, fixture-state claim in integration plan) — none block merge after the ZeroDivisionError fix.
