# Phase 4 review — apex-pace feature + capability API (#445)

**Reviewer:** independent (fresh eyes, did not author). READ-ONLY.
**Date:** 2026-06-16
**Scope:** `src/physics/apex_extract.py`, `src/physics/capability.py`, their two test files, `src/physics/__init__.py` exports.

## Verdict: **APPROVE-WITH-NITS**

The capability API and apex-pace regression are clean, correct, well-documented, and honestly scoped. The ideal lap is genuinely untouched. One real **soundness gap** (M1: corner segmentation diverges from the validated envelope method — merged corners collapse) and a **rigor gap** (M2: the "corr >0.99" envelope cross-check is near-tautological) keep this off a clean APPROVE, but neither is a blocker for an additive, relative, not-yet-wired pace feature. Both should be filed as follow-ups before this feature is trusted on real multi-car fields.

## Test run (guardrail suite)
`py -m pytest tests/unit/physics tests/regression/test_physics_regression.py tests/integration/test_physics_pipeline.py -q`
→ **259 passed, 10 skipped, 12 warnings in 10.18s.** Matches the claimed 238→259 (+21: 12 apex-extract + 9 capability). MC suite green (11 passed).

## Fixtures unchanged by this phase — CONFIRMED
`git status`: the three `processed_telemetry.parquet` + `blessed_params.json` ARE modified in the working tree, but those deltas belong to the earlier calibration-port / a_long-fix / SNR-gate work (documented in the plan), **not Phase 4**. Phase 4 adds two source modules + two test files + 8 lines of `__init__.py` exports. Neither new module imports the simulator; `capability.py` only *mentions* `monte_carlo_laps` in its docstring as a future product. `test_monte_carlo.py` passes byte-for-byte. **The ideal lap / simulator is genuinely untouched.**

---

## (a) Explicit call: apex-detection soundness — **PARTIALLY SOUND; one real divergence**

The new extractor is **not a faithful port** of the validated envelope `apex_extract.py` at the layer that matters most — corner *segmentation*:

| Step | Envelope (validated) | New port | Consequence |
|---|---|---|---|
| Corner detection | `scipy.signal.find_peaks(a_lat(s), prominence=4.0, distance=4)` — one peak **per genuine corner** | one `argmin(v)` per **contiguous `corner`-regime run** | a run spanning 2 corners → **1 apex** (second lost) |
| Apex within corner | argmin(v) in a **±4-node window** around the a_lat peak | argmin(v) over the **whole run** | long sweeper / merged S → apex can land at a sub-corner or run edge |
| Radius | **adaptive circle-fit** over ±5 position nodes (geometrically robust) | `1/\|curvature\|` at the single apex node, curvature = `cross(v,a)/speed³` | inherits the noisy per-axis accel state |

For a **single, well-separated** corner the port is correct (synthetic tests confirm v_apex/R to <5%, and the real-fixture sanity passes). But the headline correctness property — **one apex per corner** — is only guaranteed when the `SegmentClassifier` happens to break the regime between adjacent corners. Chicanes, double-apex corners, and S-curves joined by sustained curvature (κ ≥ 0.005, i.e. R ≤ 200 m) produce **one contiguous `corner` run** and therefore **collapse to a single apex** — silently dropping the second. The validated method explicitly separated these via prominence+distance. The docstrings claim the method "matches the envelope's `argmin(v)`", which is true for the apex *within* a window but **misleading about the segmentation**, which is where double-apex handling lives. No test exercises a merged two-corner run (the synthetic `_two_corner_lap` inserts a straight between them, so the regime always breaks).

Edge cases are otherwise handled well: empty lap → `[]`; no-corner lap → `[]`; runs <3 samples dropped; R→∞ (curvature≈0) falls back to the run's median finite radius then discards if none; R clipped to [8, 3000] m; v<5 m/s floor. Monotonic-speed within a run is fine (argmin picks an endpoint, but a real corner always has an interior minimum).

**On real fixtures the bigger latent risk is radius/a_lat noise**: the fixtures carry no `curvature` column (verified), so curvature and `a_lateral` both derive from `cross(v,a)/speed³` and `cross(v,a)/speed` — the **same noisy Matérn per-axis acceleration state** the team deliberately *abandoned* for `a_longitudinal` (switched to `d/dt speed`, see `_compute_a_long_series`). So `radius_m` and `a_lat` are computed from a channel the engine already distrusts. The sanity tests only assert *physical-band membership* (R∈[8,3000], v∈[5,110]), which a noisy radius easily satisfies — they do **not** check radius accuracy against geometry. Verdict: sound for isolated corners on clean synthetic data; **under-validated and potentially noisy on real data**, with a genuine merged-corner blind spot.

## (b) Explicit call: envelope cross-check rigor — **WEAK (near-tautological)**

`test_ordering_matches_envelope_q90_offsets` does **not** reproduce the envelope's computation. It reads the envelope's persisted per-team `apex_speed_q90` offsets, then **uses those offsets directly as the per-car intercept `alpha` to GENERATE synthetic apexes** (`alpha = a0 + off`, β=0.5, zero noise), and asserts `apex_pace` recovers the same ordering and correlates >0.99 with the *injected* offsets. Because the data-generating model is exactly the regression's own model (`log v = β log R + α_car`) with α set to the target and **no noise**, recovery is algebraically guaranteed — the >0.99 is essentially testing that least-squares inverts a noiseless linear system it was handed. It confirms the **regression FORM round-trips** (shared β, per-car intercept, q90-on-limit, weekend-centring) but does **not** independently re-derive the envelope's −0.89 nor run new apex data through the validated pipeline. `test_validated_spearman_is_documented` merely asserts a persisted constant (`apexq90_sp == −0.89`). So the cross-check is a **form-equivalence + documentation** check, not a reproduction. The phase notes are honest that the −0.89 "cannot be reproduced from the fixtures" (single-driver VER only) — the limitation is correctly stated and not overclaimed — but the test *name* and the plan's "correlates >0.99 ... reproduces the regression" wording oversell what is being validated. Rigor is adequate for "the regression form is the envelope's form"; it is **not** evidence the feature reproduces the envelope's empirical result.

---

## Findings

### M1 — MEDIUM — `apex_extract.py:182-220` (and docstring 21-32)
**What:** Corner segmentation is one `argmin(v)` per contiguous `corner`-regime run, whereas the validated envelope uses `find_peaks(prominence, distance)` to separate corners. A `corner` run spanning a chicane / double-apex / sustained-curvature S collapses to a single apex; the second corner is silently dropped.
**Why:** Loses observations and biases the per-car apex set toward whichever sub-corner is slowest. Diverges from the method that produced the validated −0.89. The "one apex per corner" correctness claim only holds when the classifier happens to break the regime between corners.
**Fix:** Within each run, detect interior `a_lat` (or `1/R`) peaks with a prominence + min-distance criterion (mirror the envelope), emit one apex per peak; or document the single-apex-per-run limitation prominently and add a merged-two-corner regression test. Currently no test covers a merged run.

### M2 — MEDIUM — `test_capability.py:165-204`
**What:** The envelope cross-check feeds the envelope's own q90 offsets in as the synthetic generating `alpha` (zero noise), so recovering them at corr>0.99 is near-tautological; the −0.89 assertion is a documentation check, not a reproduction.
**Why:** Overstates rigor — it validates the regression *form*, not that this code reproduces the envelope's empirical result on apex data.
**Fix:** Either (a) inject noise and assert robust ordering recovery (still form-level, but less trivial), or (b) rename/reframe the test as a "regression-form equivalence" check and drop the implication of empirical reproduction. The real reproduction must wait on multi-driver season data (already correctly flagged as a follow-up).

### L1 — LOW — `apex_extract.py:196-204`, real fixtures
**What:** `radius_m` and `a_lat` derive from `1/|curvature|` and `|a_lateral|`, both computed from `cross(v,a)/speed^n` off the noisy per-axis Matérn acceleration state — the channel the engine abandoned for `a_longitudinal`.
**Why:** On real data the radius can be noisy; the median-fallback only triggers at exact-zero curvature, not at noisy-but-finite curvature. Sanity tests check band membership only, not accuracy.
**Fix:** Consider an adaptive circle-fit radius from the position channel (as the envelope does), or at least a windowed-median curvature at the apex; add a radius-accuracy assertion against known geometry on a noise-injected synthetic.

### L2 — LOW — `capability.py:73` / `apex_extract.py` real-fixture interaction
**What:** `DEFAULT_MIN_APEXES = 10`, but single-driver fixtures yield ~15/12/29 apexes total of which the **on-limit** subset (the only ones `apex_pace` uses) may be <10. `apex_pace` is never actually run on the fixtures (only `extract_apex_observations` is), so this is untested at the integration boundary.
**Why:** When the feature is first wired to real per-weekend data, sparse on-limit counts could silently drop most cars. Not a correctness bug now, but an un-exercised real-data path.
**Fix:** When wiring to real weekends, log dropped cars and reconsider the default vs the relaxed value; add an integration test that runs `apex_pace` on a real multi-driver weekend once such data exists.

### N1 — NIT — `apex_extract.py:38`
`Iterable` imported but unused.

### N2 — NIT — docstring accuracy, `apex_extract.py:21-23` and `capability.py:28`
The "ported from the validated envelope" / "matches the envelope's `argmin(v)`" phrasing implies method fidelity that does not hold at the segmentation layer (see M1). Tighten to "apex *within a window* matches argmin(v); corner segmentation differs (regime-run vs prominence peaks)".

---

## What is genuinely good
- **Pooled regression is correct.** `capability.py:150-157` builds a single design matrix: column 0 = `log R` (one shared β), columns 1..N = per-car intercept dummies, no global intercept, one `lstsq`. This is exactly a shared-slope / per-car-intercept fit, not independent per-car fits. On-limit filtering (`o.on_limit`) is applied *before* the fit (`131-135`). Residual is against the shared β line (`163`). Field-centring is mean-of-per-car-q90 (`165`), subtracted at `169`. Sign convention (higher = faster) is correct and directly tested (FAST>MID>SLOW, and the symmetric ±0.10 spacing). β≈0.5 recovery tested.
- **Degenerate handling** in `apex_pace` is thorough: empty weekend → `{}`; single car → centred 0; sub-`min_apexes` cars dropped; cars with zero on-limit apexes excluded; non-finite/≤0 v,R filtered.
- **Honest limitation correctly stated.** The single-driver fixtures cannot reproduce the season −0.89; the docs and tests say so and do not attempt a real cross-car fit on the fixtures. No overclaim on the *result* (only on the cross-check's framing — N2).
- **D4 facade is genuinely a facade, not a thin wrapper.** `capability.py`'s module docstring lays out the three product types (absolute force params, ideal-lap distribution, relative pace), documents the extension pattern (sibling functions: `corner_traversal_pace`, `drag_capability`, `ideal_lap_capability`), and explicitly keeps RELATIVE pace vs ABSOLUTE force/ceiling as distinct return types. The relative-vs-absolute distinction is documented in three places (module docstring, `ApexPace.pace` docstring, function `Note`). Extensible and clean.
- **Ideal lap untouched** — confirmed by import analysis + green MC suite.

## Blocker
**None.** Additive, relative, not-yet-pipeline-wired feature. M1 (merged-corner segmentation) and M2 (cross-check rigor) should be filed as follow-ups and resolved before the feature is trusted on real multi-car fields, but neither blocks merging this phase.
