# Wave 7 · #628 Phase 3b — Driver utility on the physics basis — VERDICT

**Commander:** Ship H (delegated). **Branch:** `feat/628-driver-utility` (base main `61b1c76e`), PR opened, NOT merged.
**Verdict:** **PASS** — the driver-utility latent's corner-axis structure **replicates out-of-sample**, built on
a genuinely anti-circular construction. Honest-null was a first-class available outcome; the data cleared the
frozen rubric.

---

## 1. What was built (produced, not consumed)
A **driver-utility latent** on the same physics basis as the car-capability envelope: per-driver, per-axis
**access** of the pooled car ceiling, as a race-history prior. Three shipped modules + a resumable batch CLI +
a reproducible gate runner:
- `src/physics/utilization/driver_utility_observable.py` — pure per-regime **absolute speed-deficit** observable
  `g = mean(v_ideal_causal − v_real)` (NO ratio).
- `scripts/build_driver_utility_observables.py` — resumable, idempotent batch CLI (lean `fit_best_lap_trace`;
  one `strictly_pre` ceiling + one sim per constructor-round; untracked scratch DB).
- `src/physics/utilization/driver_utility.py` — partial-pooling latent (`pool_random_effects`) + explicit
  resolved/unresolved status (reused `UNRESOLVED_AXIS_SIGMA_FRAC` + `effective_axis_sigma`) + banked artifact.
- `src/physics/utilization/driver_utility_gate.py` — the falsifiable held-out gate harness.
- `scripts/run_628_driver_utility_gate.py` — reproducible end-to-end gate runner.
- `scripts/diag_628_leakage_materiality.py` — the non-gating real-data leakage-materiality diagnostic.

**Banked artifact:** `data/driver_utility.db` (untracked) — 84 (driver,axis) rows = 21 drivers × 4 axes,
80 resolved + 4 reserved (RIC, 2 sessions). Ready for round-2 driver-affinity consumption (out of scope here).

## 2. Anti-circularity construction PROOF (critic F4)
The gate is falsifiable because utility is **never** `observed ÷ capability`:
1. **Capability is a pooled latent, causal to the held-out session.** `car_prior.build_car_ceiling(strictly_pre=True)`
   uses only rounds `< W`, so the held-out session's own laps never enter the ceiling that scores it. This closes
   the within-session leak (the `loo-residual-diagnostic` truth-leak class). Verified in source by the cold critic
   and the G1 reviewer (behavioral call-count check).
2. **Utility is a driver-level random effect** (`pool_random_effects` over the driver's TRAIN sessions) — a
   race-history prior, **not** a per-session ratio. Fit on TRAIN rounds only; the harness asserts TRAIN/HELD-OUT
   round disjointness (a driver's held-out sessions never enter their own δ).
3. **The observable is an absolute SUBTRACTION**, not a division — grep-verified NO `v_real/v_ideal` in any module.
   (Note, per critic MINOR-1: additive-vs-ratio is *not itself* the anti-circularity guarantee — subtraction is
   equally per-session-invertible; the guarantee is **held-out + causal ceiling**. Additive was chosen for
   numerical stability in low-speed corners + lean compute.)

## 3. Held-out gate result (FROZEN methodology: train R1-8 / held-out R9-12, 2023-Q, 21 drivers)
Frozen BEFORE any deficit number was seen (coverage/outcome firewall honored — only fit_status/roster inspected).

**LIMB 1 — recomposition, out-of-sample (held-out R9-12, n=80 per axis):**
| axis | RMSE baseline (δ=0) | RMSE model | improvement (m/s) | role |
|---|---|---|---|---|
| braking | 7.26 | 5.73 | **+1.53** | corner |
| slow_corner | 4.70 | 2.51 | **+2.19** | corner |
| fast_corner | 4.71 | 3.16 | **+1.56** | corner |
| straight | 2.03 | 1.94 | +0.10 | **confounded neg-control (excluded)** |

3/3 corner axes improve OOS; pooled-corner improvement **1.64 m/s** ≥ frozen 0.05. **LIMB-1 PASS.**

**LIMB 2 — per-axis structure, centered cross-driver variance (TRAIN), straight=0.870:**
| axis | centered var | cross-team var | > straight? |
|---|---|---|---|
| braking | 3.137 | 1.343 | ✓ |
| fast_corner | 1.428 | 1.190 | ✓ |
| slow_corner | 0.546 | 0.402 | ✗ |

2/3 corner axes exceed the straight negative-control ≥ frozen 2/3. **LIMB-2 PASS.**
Nuance: slow_corner carries strong limb-1 recomposition (+2.19) but LOW cross-driver spread — drivers replicate a
common slow-corner access pattern rather than differentiating. Passes the frozen 2/3 rule.

**OVERALL: PASS** (both limbs on corner axes; straight structurally excluded).

## 4. Leakage self-test / materiality
- **Synthetic (G3 unit self-test, frozen pre-committed 0.15 m/s):** a non-causal (through-W) ceiling inflates OOS
  replication by **0.36–0.73 m/s** across 6 seeds on a 16-driver high-leverage roster (2.4× worst-case margin);
  null-construction companion = structural 0.0. Proves the metric DETECTS leakage; null ⇒ immaterial-OR-underpowered,
  never a silent pass.
- **Real-data (round 9 Austria, non-causal vs causal ceiling on 1249/1500 corner points, pre-committed 0.15 m/s):**
  FIELD mean |corner Δv_ideal| = **2.185 m/s** → **MATERIAL** (14.6× the pre-committed magnitude). All 10
  constructors show a POSITIVE shift (+0.48 to +4.00 m/s): a non-causal through-W ceiling that includes round 9's
  own laps runs faster on corners, which would shrink the deficit basis by ~2.2 m/s. So the strictly_pre causal
  apparatus suppresses a large, real ceiling contamination at this leverage — the out-of-sample protection is
  doing genuine work, not over-engineering. (Round 9 is high-leverage: only 8 prior sessions in the causal pool.)

## 5. Explicit-unknown contract (OWNER HARD requirement)
Every (driver, axis) carries a status; nothing dropped. 84/84 present. 4 reserved slots (RIC, 2 sessions):
all 4 axes `unresolved` with widened `effective_sigma` via the reused sentinel (e.g. straight δ=0.879 →
effective_sigma 2.196). The 20 regular drivers × 4 axes = 80 resolved.

## 6. Reputational smell-test (NON-GATING — never pass/fail)
Sorted by mean resolved corner δ (smaller = closer to own-car ceiling): TSU, HUL, DEV, **VER (4th, elite ✓)**,
GAS, PIA, OCO, NOR, RUS, SAI, HAM, ALO, … SAR. **Not cleanly reputation-aligned** — expected and honest, because
δ is **teammate-relative access to the car's own ceiling, not absolute pace** (a driver near a weaker car's
ceiling scores "good access"). VER placing high is a mild positive; the rest is consistent with the named
teammate-relative limit. Non-gating.

## 7. Named limits
1. **No external driver-utility ground truth** — held-out replication is the substitute (per launch order).
2. **Cross-round contamination attenuated, NOT eliminated** (critic SERIOUS-2): the `strictly_pre` ceiling for
   round W still pools driver d's own rounds `< W`, which also feed δ_d, and the store has no per-driver physics
   estimate — so this cannot be removed. The within-session leak IS closed.
3. **Straight/power axis is calibration-confounded** (critic SERIOUS-1) — a negative control, not a validated ≈0.
   Its near-zero centered variance is *consistent with* but not a *validation of* "power≈0 driver utility".
4. **δ is teammate-relative** (critic MINOR-2) — within-constructor δ mutually anchored; cross-constructor cleaner.
5. **Bounded slice** — 2023-Q rounds 1–12 only. A null here would kill only this test under these conditions
   (scoped-null), not the idea class. The PASS likewise generalizes only as far as this slice.

## 8. Tests / DB / compute
- **Unit tests (new):** G1 = 8, G2 = 8, G3 = 13 → **29 new**, all green; each independently re-run by an
  independent reviewer crew; `simplification_limits` PASS on all modules; grep NO-RATIO across all.
- **DB-clean:** `data/driver_utility_observables.db` + `data/driver_utility.db` are UNTRACKED scratch, never
  staged; `git status data/` verified clean at every gate; #632 DB dirtying avoided (batch reads main-checkout
  stores read-only).
- **Compute tax (#644 / relevant to #648):** the #644 single-thread BLAS/OMP cap in base `61b1c76e`
  systematically ~2×'d per-case fit time vs the frozen-methodology 28s/case estimate (which predated the cap) →
  ~30s/valid driver-session, ~2h for the full 2023-Q R1-12 batch. Honest bookkeeping: a real cost of a fix whose
  hang was never reproduced. Batch was OS-detached (`Start-Process -WindowStyle Hidden`), resumable, watcher-armed.

## 9. Cartographer map impact
New `struct:physics.utilization` members (driver_utility_observable, driver_utility, driver_utility_gate) — a
falsifiable driver-utility LATENT sibling to the DESCRIPTIVE #510 regime-utilization ratio. New decision to anchor:
the **strictly_pre causal ceiling for the held-out gate** (extends, does not overturn,
`decision:c1_driver_utilization_design` — the descriptive layer keeps its through-W frontier). Reconciled at G-reconcile.

## 10. Triage / floats
Triage candidates filed (in execute.json `triage_candidates`): (tc1) `.gitignore` lacks a glob for the new
scratch DBs; (tc2) G1 Fowler non-blocking (dup `_validate_inputs`, data-clump, long param lists); (tc3)
`effective_axis_sigma` value-beats-reference_value caller-trap docstring; (tc4) `run_gate` refits G2 twice on
TRAIN. Compute-ownership float to the Admiral RESOLVED (owner-detached, approved). No open blockers.
