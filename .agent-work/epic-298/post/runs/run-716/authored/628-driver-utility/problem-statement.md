# #628 Phase 3b — Driver utility on the physics basis: consolidated problem statement

**Mode:** delegated (Admiral launch order `wave7-628-launch-order.md` is the frozen principal; no reachable human).
**Reconciled against launch order Mission + F4 discipline + explicit-unknown contract.**

## The ask (reconciled)
Produce (round 1, not consumed) a **driver-utility latent on the same physics basis** as the car-capability
envelope: per-driver, per-axis **access** of the pooled car capability — a race-history prior with a weekend
update. Corners expected to dominate; power-to-weight expected ≈0 driver utility. Bank the produced artifact
for round-2 driver-affinity consumption (out of scope here).

## Baseline reconciled against the actual code (map-first)
- **Pooled car latent EXISTS and has no driver dimension** — `car_prior.build_car_ceiling` (per year,
  constructor, round; one-sided causal kernel; `strictly_pre` mode excludes round W). This is the denominator,
  fit independently of any single driver-weekend. Do NOT add a driver dim.
- **`session_estimates` pools BOTH cars** per constructor-session (220 rows/season = 10 constructors × 22
  rounds; `drivers=["VER","PER"]`). There is **no per-driver physics estimate** in the store. Driver utility
  therefore needs a per-driver realized observable, extracted fresh.
- **#510 already ships a DESCRIPTIVE per-(driver,session,regime) utilization** (`regime_utilization.py`,
  `characterize.py`): `U_r = mean(v_real / v_ideal)` over 4 tiling regimes {braking, slow_corner, fast_corner,
  straight}. This is **literally the `observed ÷ capability` ratio F4 forbids as a gate basis** — and its
  per-lap "recomposition" (U_r × v_ideal = v_real) is true-by-algebra. #628 is DIFFERENT: a driver-level
  latent validated **out-of-sample**, not that per-lap ratio.
- Decision anchor `decision:c1_driver_utilization_design` (2026-06-24) deliberately (pt 2) lets the measured
  driver contaminate the through-W frontier and (pt 3) marks `split_is_impure=True`. **For a falsifiable
  held-out gate that contamination must be broken:** the ceiling used to predict a held-out driver-session
  must be built `strictly_pre=True` (round < W) so it cannot use the held-out laps. Already supported.

## The load-bearing anti-circularity construction (F4)
Any decomposition of a realized lap into (capability, utility) is algebraically invertible on the SAME
session — ratio OR difference. What makes it falsifiable is NOT the arithmetic form but the **held-out latent
structure**:
1. **Capability from the pool, causal to the held-out session** — `build_car_ceiling(strictly_pre=True)` uses
   only rounds < W, so the held-out session's own laps never enter its own denominator (kills the
   `loo-residual-diagnostic` truth-leak: truth channel must not be derived from the same session it scores).
2. **Utility is a driver-level random effect** (a race-history prior, shrunk) fit on **TRAIN sessions only** —
   never the per-session ratio.
3. **Gate is out-of-sample**: on held-out sessions, recompose (causal capability ⊗ driver utility) → predict
   realized behavior; utility_train ≠ observed_heldout/capability_heldout, so replication is genuinely
   falsifiable.
To structurally avoid even the *appearance* of the forbidden division, the observable is expressed as an
absolute per-regime **speed deficit** `g = mean(v_ideal_causal − v_real)` (a subtraction against the causal
ceiling), NOT a ratio; the utility latent is the driver's shrunk mean deficit per axis. **No `observed ÷
capability` is computed anywhere in the utility definition or the gate.**

## Gate (freeze split + rubric BEFORE seeing held-out numbers)
Fit δ_{driver,axis} on TRAIN rounds; on HELD-OUT rounds confirm BOTH:
1. **Recomposition replicates out-of-sample** — `v_ideal_causal − δ_driver` predicts held-out `v_real` per
   axis with lower error than the δ=0 (car-only) baseline, out-of-sample.
2. **Per-axis structure replicates out-of-sample** — cross-driver variance of δ is meaningful on corner axes
   (braking/slow/fast) and ≈0 on the straight/power axis — measured on held-out, not just fit rounds.
Reputational sanity (does a known quali specialist score high) = **smell test only, never pass/fail**.
Named limit: **no external driver-utility ground truth exists** — held-out replication is the substitute.

## Explicit-unknown contract (OWNER HARD REQUIREMENT)
Every axis carries a resolved/unresolved status; any axis where driver utility is unmeasurable/unidentified
becomes a **reserved high-uncertainty slot** (reuse `estimate_store` status field + `UNRESOLVED_AXIS_SIGMA_FRAC`
sentinel — do not invent a parallel mechanism). Nothing dropped silently.

## Honest-null is a complete deliverable
If held-out replication fails broadly, that is a legitimate PASS-with-honest-null — recorded with the
reserved-slot contract. No automated kill switch.

## Compute envelope (feasibility, measured)
- Full MAP `characterize_case`: ~74–108 s/case → prohibitive.
- Lean path: realized trace via `session_fit.fit_best_lap_trace` (~28–30 s/case; skips
  `ParameterEstimator.estimate_parameters`) + one `strictly_pre` ceiling sim per (constructor, round, shared
  across both cars) + reuse `regime_utilization._build_regime_masks`. Downstream δ fit + gate = seconds.
- Only heavy part = per-(driver,session) trace batch. Plan: a **resumable** CLI persisting per-regime
  observable rows to a scratch table, launched **OS-detached** (`Start-Process -WindowStyle Hidden`),
  **polled in-turn**, on a **bounded 2023-Q slice** sized to ~1–2 h. Float to Admiral if the gate needs a
  larger owned batch.

## Scope guardrails (from launch order)
OUT: driver-affinity consumption, evo-feature consumption, delta-basis evolution, round-2 anything. Do not
re-fit the merged Phase-3 car basis. Corners-dominate / power≈0 is a PREDICTION the gate tests, not an input.

## DB hygiene / isolation
Work only in `C:/Programs/f1-628`. NEVER commit `data/*.db`; `git checkout -- data/` any dirtied DB; explicit
`git add` paths only; check `git status data/` at every gate. Headless launch via `Start-Process -WindowStyle
Hidden`. Poll artifacts, never idle on a watcher.
