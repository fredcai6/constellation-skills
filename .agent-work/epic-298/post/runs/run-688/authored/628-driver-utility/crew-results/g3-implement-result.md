# Implementation Result — G3 (held-out driver-utility gate harness)

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`g3-implement` (#628 Phase 3b — the LOAD-BEARING falsifiable gate). Worktree `C:/Programs/f1-628`, branch `feat/628-driver-utility`.

## Completed slice
Built the full held-out gate harness `src/physics/utilization/driver_utility_gate.py` and its synthetic-only test suite `tests/unit/physics/test_driver_utility_gate.py`, driven vertical-slice by vertical-slice (limb 1 → limb 2 → composition/verdict → powered leakage self-test → evidence) through the engine plan `.agent-work/628-driver-utility/g3-implement-plan.json`. All engine gates closed; plan reports DONE.

The harness, given G1-schema deficit rows + a train/held-out ROUND split:
- **Limb 1 (recomposition, OOS):** `recomposition_limb` splits by round (asserts disjoint), fits `delta` on TRAIN only via G2 `estimate_driver_utility`, then scores each held-out row `err_model = g_obs - delta_TRAIN` vs `err_baseline = g_obs - 0`; reports per-axis held-out RMSE_model / RMSE_baseline / improvement and `is_corner_axis`.
- **Limb 2 (per-axis structure, OOS):** `per_axis_structure_limb` computes cross-driver variance of the per-axis-CENTERED delta (`delta - mean_over_drivers(delta,axis)`), plus a cross-constructor variance (teammate-relative, MINOR-2). Documented honestly: variance is translation-invariant, so the centered value equals the raw cross-driver variance — the centering is what *licenses* reading that spread as the driver signal (mean = car/calibration offset).
- **Straight = calibration-confounded negative control (SERIOUS-1):** every straight-axis output row carries `confounded_negative_control=True`; `run_gate`'s verdict is computed over CORNER axes ONLY (`_corner_verdict`), so a straight-axis limb-1 "pass" can never reach the verdict. `negative_control_axes` is surfaced on `GateResult`.
- **Verdict:** `replicated` / `honest_null` / `mixed` / `insufficient_data` — `honest_null` is first-class and reportable; no kill switch, nothing tuned toward a pass.
- **Powered leakage self-test:** `oos_replication_strength` accessor + two tests contrasting a CAUSAL (strictly_pre, `alpha=1`) vs NON-CAUSAL (through-W, `alpha=0.05`) held-out ceiling on a high-leverage (few-prior-session) wide roster; asserts non-causal inflates OOS replication by a PRE-COMMITTED 0.15 m/s, with an explicit assert message: null inflation ⇒ causal apparatus immaterial-OR-underpowered, NEVER a silent pass. A companion null-construction test proves specificity (no leak ⇒ 0 inflation).
- **Reputational smell-test (NON-GATING):** `rank_drivers_by_corner_delta` returns a ranked frame tagged `NON-GATING / smell-test only` in `attrs['label']`; never feeds the verdict.

## Scope
**Files changed:**
- `src/physics/utilization/driver_utility_gate.py` (NEW)
- `tests/unit/physics/test_driver_utility_gate.py` (NEW)

Both are within Allowed Scope. G1/G2 untouched; G2 `estimate_driver_utility` reused read-only (signature confirmed at source, `driver_utility.py:130` — single DataFrame arg, matches the handoff, so no STOP triggered).

**Specific exclusions touched:** no. No real batch / FastF1 / telemetry (synthetic rows only). No `observed/capability` ratio (grep clean). No kill switch (honest_null is a returnable verdict). Nothing staged or committed.

## Behavior changed
Yes — new capability: a falsifiable held-out gate that fits driver-utility on TRAIN rounds and evaluates two limbs strictly out-of-sample on disjoint HELD-OUT rounds, with a powered leakage self-test and a non-gating reputational read.

## Map Impact
- **Structural anchors touched:** `struct:physics.utilization` — new `driver_utility_gate.py`; reuses the G2 `estimate_driver_utility` estimator by import, no modification.
- **Capabilities added:** falsifiable held-out driver-utility gate (limb-1 OOS recomposition + limb-2 centered per-axis structure), composed by `run_gate` into a corner-only verdict.
- **Constraints/assumptions touched:** out-of-sample discipline enforced structurally (disjoint-round assert; delta fit on TRAIN only; `loo-residual-diagnostic` lesson honored — no self-inclusive metric); straight axis carried as calibration-confounded negative control and excluded from the verdict; centered variance is the limb-2 driver signal.
- **Decision:** `decision:c1_driver_utilization_design` — strictly_pre causal ceiling breaks the within-session leak; cross-round leak only attenuated (named limit; the leakage self-test demonstrates the metric's sensitivity to a non-causal ceiling).
- **Claims/evidence produced:** on synthetic data, known delta is recovered OOS (corner improvement when signal exists; honest-null reachable when signal is zero); centering removes a shared car offset (~0 centered variance under a pure car-offset); the leakage self-test is genuinely powered (leak inflation 0.55–0.70 m/s per corner axis vs 0.15 threshold; null construction 0.0).
- **Triage candidates:** none.

## Test mode
**Required:** test-first (TDD red→green→refactor), synthetic only.
**Satisfied:** yes. Each of m1/m2/m3/m4 wrote its test, observed RED, then went GREEN through the engine. m4's RED was a *genuine, meaningful* red: the powered self-test failed on a 4-driver roster (min corner inflation 0.045 < 0.15) because `rms(eps)` over few held points is too noisy; I fixed the TEST POWER (widened to a 16-driver / 8-constructor roster), not the pre-committed threshold and not production code.

## Evidence

```bash
cd /c/Programs/f1-628 && PYTHONPATH=/c/Programs/f1-628 py -m pytest tests/unit/physics/test_driver_utility_gate.py -q
# => 13 passed in 1.73s

cd /c/Programs/f1-628 && PYTHONPATH=/c/Programs/f1-628 py -m src.utils.simplification_limits --paths src/physics/utilization/driver_utility_gate.py tests/unit/physics/test_driver_utility_gate.py
# => PASS (2 files checked)

cd /c/Programs/f1-628 && grep -nE "/ ?v_ideal|observed ?/ ?cap" src/physics/utilization/driver_utility_gate.py || echo NO-RATIO-OK
# => NO-RATIO-OK

cd /c/Programs/f1-628 && git check-ignore src/physics/utilization/driver_utility_gate.py tests/unit/physics/test_driver_utility_gate.py; echo $?
# => (no output) exit 1  — both deliverables are tracked-eligible (not gitignored)
```

Powered-leakage magnitudes (printed via the test's own helpers, seed 11):
```
LEAK inflation per corner axis: {'braking': 0.7, 'slow_corner': 0.683, 'fast_corner': 0.554}   min = 0.554  (>= pre-committed 0.15)
NULL construction inflation:    {'braking': 0.0, 'slow_corner': 0.0, 'fast_corner': 0.0}        max|null| = 0.0
```

**Result:** pass — full suite green, simplification PASS, no ratio, deliverables tracked, leakage self-test genuinely powered and specific.

## TDD evidence, if required
- Failing test observed:
  - m1 red: `ImportError: cannot import name 'driver_utility_gate'` (module absent).
  - m2 red: 4 structure tests failed (no `per_axis_structure_limb`).
  - m3 red: 4 gate tests failed (no `run_gate`/`rank_drivers_by_corner_delta`).
  - m4 red (meaningful): `min corner inflation 0.045 < 0.15` on the 4-driver roster (underpowered).
- Passing test observed: 13 passed after each slice's green; final full-file run 13 passed.
- Refactor while green: honest-null assertion relaxed from exact-0 to `< MIN_CORNER_IMPROVEMENT_MS` after observing a spurious-fit slight-negative improvement (the real no-signal signature); leakage roster widened to stabilize the metric.

## Docs/contracts touched
- None. Module is self-documenting (module docstring states the falsifiability contract, the negative-control framing, and the cross-round-leak limit).

## Assumptions
- `round_idx` is the G1 round identifier used for the train/held-out split (from G1's persisted schema in the G2 docstring). The split is by round; disjointness is asserted.
- A held-out `(driver, axis)` with no RESOLVED TRAIN delta falls back to `delta=0` (car-only) — identical to baseline for that row, so an unresolved driver earns no artificial limb-1 credit (honest, no hidden fallback beyond car-only).
- Deficit-sign convention for the smell-test: smaller resolved corner delta = closer to the car ceiling = "better utilization" (ranked ascending). Non-gating, so direction is presentational only.
- Synthetic leak model: the non-causal ceiling suppresses the held lap's idiosyncratic residual (`alpha*eps`, `alpha<1`) while preserving the driver's systematic delta — a deliberate idealization of the through-W leak sufficient to prove the metric's SENSITIVITY (documented in the test helper docstring). A real through-W ceiling also partially absorbs the systematic component; that only attenuates the naive deficit and does not change what the self-test demonstrates.

## Stop conditions hit
- None. G2 signature matched source (no STOP); scope not exceeded; OOS discipline honored; honest-null representable.

## Out-of-scope observations
- `data/driver_utility_observables.db` is present untracked in the worktree (a G1/G2 artifact, not produced by this gate — this gate is synthetic-only and writes no DB). Left as-is.

## Workflow Feedback
- **Handoff gaps:** The handoff specifies limb 2 as "cross-driver variance of the per-axis-CENTERED delta" but centering is mathematically a no-op on variance (translation-invariant). The handoff's own test spec (b) is what makes it operational (pure car-offset → ~0 variance). Not a blocker, but a naive reader could waste time looking for a numeric difference between centered and raw variance — worth a one-line note that centering is *interpretive* (licenses reading the spread as driver signal), not a numeric transform.
- **Context rediscovered:** The G1 round-split column name (`round_idx`) is not in the handoff; I confirmed it from the G2 module docstring's schema list. A one-line "split on `round_idx`" in the handoff would have saved a lookup.
- **Instructions improvised around:** The plan template's TDD-red postcondition assumes red = "code missing." For m4 the accessor already existed (needed by m3 composition), so the meaningful red was a *miscalibration* red (underpowered roster) rather than an import error. I attested it honestly as a genuine red and fixed test power, not the threshold — but the template wording ("new test written and observed failing") could acknowledge the powered-self-test case where the red is a calibration failure, not an absent symbol.
- **What would have made this easier:** Naming `round_idx` and the deficit-sign convention (is a larger `g_deficit` better or worse for the driver?) in the handoff. I inferred deficit = ceiling − observed (smaller = better) from the G2 docstring; an explicit statement would remove all doubt for the smell-test direction.

## Return status
`complete`
