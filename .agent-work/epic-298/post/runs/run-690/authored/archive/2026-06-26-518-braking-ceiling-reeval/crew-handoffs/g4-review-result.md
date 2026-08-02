# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g4 — C1 driver-utilization re-eval on the recalibrated (wired) ceiling + lap-sampling σ + headline GO/CONTEXTUAL/NO-GO verdict (review)`

## Result
`verdict: APPROVE`

APPROVE = the re-evaluation, the **NO-GO** verdict on braking + fast-corner, the CONTEXTUAL straight call, and the project-redirecting diagnosis are all sound and independently reproduced. It does **NOT** mean the regimes are GO — braking and fast-corner remain NO-GO.

---

## THE CRUX — aphysical-ideal-lap diagnosis: **CONFIRMED**

I independently probed the canonical sim for Italy/VER on the WIRED store using the *same* canonical helpers the dashboard uses (`EstimateStore → car_prior.build_car_ceiling → PhysicsSimulator.simulate_lap → _build_regime_masks`; probe at `.agent-work/518-braking-ceiling-reeval/crew-handoffs/g4_probe.py`). My own measured numbers:

| Quantity | My probe | Implementer claim | Match |
|---|---|---|---|
| **Ideal-lap top speed** | **206.9 m/s = 745 km/h** | 206.9 m/s | exact |
| Ideal-lap min speed | 7.5 m/s | 7.5 m/s | exact |
| **Real-lap top speed** | **95.3 m/s = 343 km/h** | 95.3 m/s | exact |
| Real-lap min speed | 20.8 m/s | 20.8 m/s | exact |
| Braking mask: mean v_ideal | 25.1 m/s | 25.1 m/s | exact |
| Braking mask: mean v_real | 65.6 m/s | 65.6 m/s | exact |
| Braking mask: ratio min/mean/max | 1.29 / 3.32 / 5.20 | — | — |
| Braking mask: frac(ratio≥2.0) | 0.76 | 0.73–1.0 range | in range |
| Braking U = clip(mean) | **2.000** | 2.000 | exact |
| Fast-corner: v_ideal / v_real | 16.7 / 62.9 (ratio 3.79, frac≥2=1.0) | 16.7 / 62.9 | exact |
| Fast-corner U | **2.000** | 2.000 | exact |
| Straight: v_ideal / v_real | 135.6 / 89.1 (ratio 0.71) | — | — |
| Straight U | **0.712** | 0.712 | exact |

**Verdict on the diagnosis:** the ideal lap is genuinely **aphysical** (745 km/h top speed — no F1 car approaches that; real lap tops out at a physical 343 km/h) and **phase/apex-misaligned**: in the real-braking mask the ideal lap is already deep in the apex (25 m/s) while the real lap is still fast (66 m/s) at the *same* progress-grid index, giving a 2.5–3.7× structural ratio offset. The U clip is therefore a **comparison artifact**, NOT a braking-frontier-depth problem. A deeper braking ceiling cannot close a 2.5–3.7× offset — which is exactly why the recalibration leaves `u_braking`/`u_fast_corner` bit-for-bit unchanged. The straight regime is correctly aligned (both laps near flat-out there), which is why it is the only regime that responds and lands physical. **The NO-GO diagnosis is sound; I confirm it.**

---

## Handoff compliance
Satisfied. The change does exactly what the handoff asked: `--db`/`--cases` seam on the dashboard (back-compat default = OLD store); first-class lap-sampling σ in the pure core threaded through `RegimeUtilization` → `UtilizationRow` → CSV; an apples-to-apples OLD-vs-WIRED run on the 4 RBR/VER cases at mc=50/seed=42; and an honest per-regime verdict. Stop conditions: none hit.

## Scope drift
None. Changed set is exactly the 5 allowed files (`regime_utilization.py`, `characterize.py`, `driver_utilization_dashboard.py`, 2 test files). **Excluded files verified UNTOUCHED** (zero diff): `car_prior.py`, `estimate_store.py`, layer2 views, `docs/architecture/**`. The braking wiring (G3) is untouched. `scripts/g3_store_manifest.py` is a pre-existing untracked G3 artifact correctly flagged by the implementer as not theirs — I did not touch it; review introduced no tracked-source changes.

## Evidence verdict
Required evidence present, reproducible, and re-run by me inline:
- **Headline reproduced on my own re-runs of BOTH stores** (4/4 ok, 0 errors each, ~256 s): `u_braking`=2.000 and `u_fast_corner`=2.000 on OLD **and** WIRED in all 4 cases → **Δ=0.000** (no un-clip). `u_straight`: **Italy 0.578 → 0.712 (+0.134, exact)**, GB 0.775→0.825, Singapore 0.831→0.888 (all physical <1), Monaco 1.196→1.183 (known DRS artifact). `split_is_impure=True` on every row. Bit-for-bit match to the implementer's table.
- **Tests:** `py -m pytest tests/unit/physics/test_regime_utilization.py tests/unit/physics/test_driver_utilization_dashboard.py tests/unit/test_utilization.py -q` → **60 passed in 5.85 s**.
- **Simplification:** `py -m src.utils.simplification_limits --paths …` → **PASS (5 files checked)**.

Test mode = test-after (appropriate; this is a measurement/characterization gate, not new feature behavior). New tests are behavior-focused: closed-form SEM, 3-4-5 quadrature, envelope-σ separateness, zero-spread→0, strict 1/√n shrinkage.

## Code/doc quality
Minimal, well-factored, project-rule-compliant. The lap-sampling σ is `std(ratio[mask])/sqrt(n)` computed in `_u_and_consistency`, reusing the `std_r` already computed for the CV (no redundant recompute). Quadrature in `_combine_sigma_quadrature` is correct (`None+None→None`; else `sqrt(env²+lap²)` treating `None` as 0). The **envelope σ math is genuinely unchanged** and kept as its own separately-reportable field — the lap-sampling term is additive, not a replacement (constraint honored). The result-assembly refactor (`_per_regime_metrics` + `_assemble_result`) is behavior-preserving and keeps the function under the simplification limit. Docstrings updated to retire the deferred TODO honestly.

## Map impact verdict
- **Evidence supports claimed change:** Yes — the σ columns flow through to the CSV (verified in my re-run output: `sigma_u_straight` / `sigma_u_lapsampling_straight` / `sigma_u_total_straight` all populated and behaving sensibly — lap-sampling dominates Monaco's short straight, envelope dominates Italy).
- **Constraints not violated:** Yes — single canonical ideal-lap path preserved (zero direct `simulate_lap`/`PhysicsSimulator()` calls in dashboard/characterize; sim runs only inside `estimate_driver_utilization`); `split_is_impure=True` hardcoded at every construction site; no evo import; honest-covariance additive.
- **Notes match the diff:** Yes — `struct:physics.utilization` touched as described; `car_prior` read-only; no overstated impact.
- **Decision candidates surfaced:** Yes — the aphysical-ideal-lap finding is correctly surfaced as bearing on `decision:ideal_lap_sim_two_sided_evaluator` and as superseding #510's "ceiling under-call" framing.
- **Durable context routed:** Yes — two triage candidates routed (physics-aware/phase-aligned ideal-lap comparison; wire the remaining 4 C1 constructors). No `docs/architecture/**` edits (reconcile owns the map) — correct.

## Reconciliation check
The diagnosis is a **significant decision candidate**: it redirects the C1 branch — the binding constraint on braking/fast-corner utilization is the ideal-lap shape/alignment, NOT braking-frontier depth (the premise #518 G1–G3 was built to test). This supersedes #510's framing and should go to Commander for reconcile/triage. Flagged as `tc1` in the survey. No structural-baseline conflict in the diff itself (the map is not edited here).

## Blockers
- none — confirmed after full review: headline reproduced on both stores; crux diagnosis independently reproduced bit-for-bit; σ math + tests + simplification green; invariants and exclusions intact.

## Out-of-scope observations
- **`tc1` (decision/triage):** aphysical ideal lap (745 km/h) + longitudinal phase/apex misalignment is the real blocker for braking/fast-corner U → needs a physics-aware / phase-aligned ideal-lap comparison (or a per-regime capability frontier), not a deeper braking frontier. Supersedes #510's "ceiling under-call" framing.
- **`tc2` (continuation):** only RBR is fully wired in `physics_estimates_g3wired.db`; wire the remaining 4 C1 constructors (Ferrari/McLaren/Williams/Mercedes r1–15) before any cross-constructor C1 verdict.
- **Cosmetic (non-blocking):** the dashboard's printed header and `--cases` help text still say "bounded subset (10 cases…)" even when running the 4-case subset. Harmless; not worth a change unless the Commander wants it tidied.

## Workflow Feedback
- **Handoff gaps:** The handoff's own Close Criteria and the implementer's result both note a "10-case" vs "4 RBR-only" scope contradiction between the handoff body and the Commander's live dispatch. It is reconcilable via the store-scope note, but it cost the implementer (and me) a reconciliation step. Naming the 4 RBR/VER cases in the Task section, not only in a scope caveat, would remove it.
- **Context rediscovered:** The handoff named `car_prior.build_car_ceiling` and `PhysicsSimulator.simulate_lap` but not the exact module locations (`EstimateStore` is under `src/physics/layer2/`, `resample_by_progress` under `src/physics/sim_evaluator`, not `regime_utilization`). I had to grep to wire the probe. A one-line "canonical path import map" in the handoff would have saved two grep round-trips.
- **Instructions improvised around:** None material. The reviewer skill + engine covered the survey cleanly; I appended 5 context-warranted checks (headline / crux / σ / invariants / verdict-honesty / tests) beyond the template's generic 6, which is exactly the "append per inherited rule" instruction.
- **What would have made this easier:** Pre-stating the apples-to-apples MC setting in the handoff ("re-run OLD at mc=50/seed=42, not the stored mc=20 CSV") — the implementer flagged this too; I independently re-ran both at mc=50/seed=42 and confirmed it is the right call, but the handoff could have said so.

## Return status
`complete`
