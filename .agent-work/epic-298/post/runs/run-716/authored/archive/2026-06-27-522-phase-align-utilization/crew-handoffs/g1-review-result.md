# Review Result

## Assigned Gate
`g1-review — verify the #522 DIAGNOSIS (no production code): is it SOUND and well-evidenced, plus the scope-determining units-vs-dilution probe.`

## Result
`APPROVE` (diagnosis sound) — **with a material correction to the implementer's root-cause attribution** (resolved by the probe below; this does not invalidate the verdict).

---

## Handoff compliance
The diagnosis answered exactly the assigned question — discriminate **(a) corner misregistration** vs **(b) under-called ideal-speed caps** on RBR 2023-Q, using a true-distance re-registration as the decisive test. It used the **canonical ideal-lap path** (`PhysicsSimulator.simulate_lap` from the `_build_ceiling`/`car_prior` causal ceiling — confirmed in `diag_alignment.py` imports, lines 67–82), not a reinvented sim. Scope respected: only `.agent-work/` artifacts, no `src/`/`scripts/` edits, no store writes.

## Scope drift
None. Artifacts confined to `.agent-work/522-phase-align-utilization/`. I opened the store read-only (`file:...?mode=ro`) for the probe; no writes by anyone.

## Evidence verdict
**Regenerates and matches `DIAGNOSIS.md` to the digit** (`py .agent-work/522-phase-align-utilization/diag_alignment.py`).

- **(a) genuinely rejected.** Lap-length delta 15.1 m on 3241.6 m = 0.47%. True-distance re-registration (`np.interp(grid_dist, driver_distance, driver_speed)`) does NOT lower the ratios: braking regime mean 1.884 → 1.870 (−0.7%, noise), fast_corner 1.994 both ways. At the C2 braking knee the true-dist ratio goes **up** (1.22 → 2.0) — the opposite of what misregistration would produce. Real, not an artifact of the recomputation.
- **(b) genuinely confirmed.** Tunnel cap ≈ 15.9 m/s (57 km/h) vs VER's actual 63.3 m/s; required lateral `κ·v² = 44 m/s²` (4.5g) vs the model-supplied ~5 m/s² (0.5g). No registration correction can reconcile a 16 m/s cap with a 63 m/s pass.
- Figure `fig_alignment_monaco_ver.png` regenerated this run.

One immaterial arithmetic slip in the writeup: `DIAGNOSIS.md` states the cap as `v_cap = sqrt(A0/(κ − A2))`, dropping the air-density `ρ` that the real code carries (`denom = curvature − A2·air_density`). Effect is ~19% on the tiny A2 term and does not move the A0-dominated cap or the verdict.

## Code/doc quality
Diagnosis is units-explicit in its own arithmetic and physically reasoned. The single real defect is the **root-cause attribution**: the implementer asserted A0≈2.64 is "cross-session pooling dilution / Monaco diluted by high-speed tracks" **without verifying it**. The probe shows that attribution is wrong (below). The verdict (b) stands; only the *why* changes.

## Map impact verdict
- **Evidence supports claimed change:** Yes for the (a)-rejected / (b)-confirmed claims. **No** for the "pool dilutes A0" sub-claim — unbacked and refuted.
- **Constraints not violated:** Canonical ideal-lap path honored; read-only store/cache; no evo import.
- **Notes match the diff:** Yes — artifacts match the Map Impact notes.
- **Decision candidates surfaced:** The implementer routed the A0 question to the decide-fix checkpoint (good), but mislabeled the cause. The correct decision candidate is a **lateral units/assembly bug on `decision:ideal_lap_sim_two_sided_evaluator`, parallel to the #518 G5 watts→W/kg fix.**
- **Durable context routed:** Now routed via triage candidate `tc1` (below).

## Reconciliation check
The finding re-scopes #522 from "capability/pooling rebuild" to a **small, surgical units fix**. This should reach the decide-fix checkpoint and Cartographer as a units bug, not a pooling problem.

---

## SCOPE-DETERMINING PROBE — Units vs Measurement vs Pooling

### Conclusion: **UNITS / ASSEMBLY BUG.** Not pooling dilution. Not a measurement under-call. → #522 is a **small fix**, not a capability rebuild.

The lateral grip parameters are fitted as a **dimensionless grip coefficient (μ, "g-units")** but consumed as if they were already **m/s²** — the consumer drops the `×g (9.81)` factor. That single missing factor fully explains the ~3–4× speed / ~9–10× force under-call.

**Evidence:**

**(1) Raw per-session A0 — pooling dilution REFUTED.** All 22 RBR 2023-Q rows have A0 in **1.87–4.91** (Monaco's OWN session = **2.626**; the causal pool = 2.642). There is no session with a high A0 that the pool could be averaging down. Pooling is not the cause.

| round | gp | A0 | A2 |
|---|---|---|---|
| 1 | Bahrain | 2.759 | 5.2e-4 |
| 3 | Australia | 2.559 | 8.2e-4 |
| 6 | **Monaco** | **2.626** | 5.2e-4 |
| 13 | Netherlands | 4.911 | 1.7e-4 |
| 14 | Italy | 1.869 | 7.6e-4 |
| 22 | Abu Dhabi | 2.765 | 8.4e-4 |

(full 22-row sweep pulled read-only; range 1.87–4.91, all same scale)

**(2) Source-vs-consumer units mismatch — the bug.**
- **Producer** `src/physics/layer2/lateral_view.py` (docstring L1–6, `grip_coef`/`a_lat_max` L66–72): `mu_max(v) = A0 + A2·v²` is a **grip coefficient in g-units**; the actual acceleration is `a_lat_max(v) = mu_max(v) · g`. The de-conflation `mu_obs = |a_lat|/(g·cosθ)` (L141) divides g out, so the fitted A0/A2 are μ. `session_lateral.py` confirms (`_GRIP_CEILING_G = 7.0 # g`, `keep = (a_lat/_G) < _GRIP_CEILING_G`).
- **Consumer** `src/physics/physics_data_models.py::LateralParameters.lateral_capability` (L237–249): `mechanical = A0·g_track`, `aero = A2·ρ·v²`, `result = mechanical + aero` (m/s²). **No `×9.81`.** It reads the g-coefficient as m/s². `physics_simulator._compute_speed_caps` (L497–518) and `_gsat_ceiling` (L482) inherit the same un-scaled reading.
- Two discrepancies: **(dominant)** missing `×9.81` on BOTH the A0 and the A2 terms — a clean ~constant multiplicative gap, exactly the #518 G5 "units" tell; **(secondary)** the consumer multiplies the aero term by `ρ` (~1.19) that the producer never had (the fit absorbed any density into A2).

**(3) Direct measured frontier on VER Monaco (probe #3, `probe_lateral_units.py`).** `LateralView.fit` on VER's Monaco 2023-Q corner cloud: **A0 = 3.20**, raw p99 grip = **4.62 g**.
- As a g-coefficient → a_lat = 32–41 m/s² (3.3–4.2 g) across 20–63 m/s — **physical for a 2023 F1 car.**
- As m/s² (the consumer's reading) → 0.34–0.42 g — **absurd.**
- Applying the missing `×g`: tunnel corner-speed cap = **65.9 m/s (237 km/h)** vs VER's actual **63.3 m/s (228 km/h)** — agreement within **4%**. The `×9.81` closes the entire gap.

**(4) Channel isolation.** Braking (`a_b ≈ 27 m/s² ≈ 2.7 g`, `BrakingView` docstring "m/s²") and traction (`a_t`) are natively m/s² and are read correctly. **Lateral is the lone mis-scaled channel.** This also explains why the braking-*regime* utilization is contaminated even though braking caps are fine: corner-entry speed denominators are set by the broken lateral cap upstream.

**Fix shape (for the decide-fix checkpoint, NOT implemented here):** scale the lateral g-coefficient to m/s² by `×9.81` (and drop the spurious `ρ` on the aero term — or rescale once at the store boundary), then re-baseline the ideal lap. Verify blast radius: the `braking_grip_ratio × lateral_capability` and `traction_grip_ratio × lateral_capability` fallback paths also consume `lateral_capability`, so a fix shifts them too (mostly inert when measured frontiers are present, which they are for RBR 2023-Q).

---

## Blockers
- None. The diagnosis is sound and the probe resolved the scope question conclusively.

## Out-of-scope observations
- The implementer's "pool dilution" narrative (DIAGNOSIS.md §"Physical Root Cause" and Out-of-scope obs #1; g1-implement-result Map Impact + obs #1) is **incorrect** and should be struck/annotated before this feeds planning — it would otherwise send the fix down a "per-circuit A0 re-calibration / capability rebuild" path that is unnecessary.
- Secondary geometry overlap at the Massenet braking zone (~640–710 m) noted by the implementer is real and independent of the units bug, but is dominated by it; defer until after the units fix re-baselines utilization (may shrink to nothing).
- DIAGNOSIS.md cap formula should add the `·ρ` on the A2 term to match the code (cosmetic).

## Workflow Feedback
- **Handoff gaps:** Strong handoff. The probe section pre-named the #518 G5 "watts-in-W/kg" parallel and the "clean multiplicative gap on both terms = units bug" tell — that framing pointed straight at the answer and is exactly the context that should be carried. One missing field: the handoff said "g_track=1.0, k_tire=0.0 so consumed lateral grip is exactly the stored A0" but did not state the **units** of that stored A0 (g-coefficient vs m/s²); naming that the producer (`LateralView`) emits a g-coefficient would have let the probe start from the answer rather than rediscover it from the source docstrings.
- **Context rediscovered:** Had to read `lateral_view.py`/`session_lateral.py`/`physics_data_models.py` to establish that A0 is a g-coefficient and that the consumer drops `×9.81`. The map anchors named `struct:physics.layer2` (the measured frontier) but did not carry the units contract across the producer→store→consumer seam — that contract is the whole bug.
- **Instructions improvised around:** The reviewer survey template has no dedicated "scope-determining probe" item; I `append`ed `r6-probe` (engine-sanctioned for surveys) and flagged the fix as triage candidate `tc1`. No skill instruction failed to cover the situation.
- **What would have made this easier:** A one-line units annotation on the store schema / `LateralParameters` ("A0/A2 are g-coefficients per LateralView; multiply by g for m/s²") — its absence IS the defect. Adding it to the handoff's probe section would have made this a 10-minute confirmation.

## Return status
`complete`
