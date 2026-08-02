# Round-3 Design Seed — user direction received 2026-06-12 (mid wave-4)

Captured verbatim-in-substance from the user at the Phase-1 iteration checkpoint. This is
the design basis for the next strategy round if wave 4 (fix-and-rerun) returns "null stands
clean." Not binding on wave 4, which is deliberately bounded to decontamination.

## 1. Multi-frame estimation — frames are views, not homes

- Ribbon frame: useful, keep — geometric constraints natural there (containment, lap
  closure, anchor crossings).
- **Pseudo-inertial local-velocity frame**: acceleration constraints are better considered
  there (tire friction ellipse, longitudinal/lateral accel bounds, jerk plausibility).
- Anti-pattern named by the user: "this frame tells me everything." Apply each constraint
  in the frame where it is natural; the estimator carries state wherever convenient.

## 2. Windowed estimation — the information horizon

- Whole-session solves are unjustified for trajectory states: "there is nothing the last
  lap tells you about the first one" unless you adopt driver-consistency priors
  ("this driver always drives like his mean attack on this corner") — and residuals to
  such priors launder driver variation into suspect data. Reject those priors.
- Required design step: determine the **window of useful information** and the **window of
  reliable information within it** (dynamics correlation time ~ seconds; events: braking,
  corners).
- Three relationships per window: (a) residuals WITHIN the window; (b) consistency with the
  window BEFORE; (c) consistency with the window AFTER. → fixed-lag smoother with
  overlap-consistency diagnostics; overlap disagreement is itself a data-quality signal.

## 3. Two-level solve — local trajectories, global calibration

- Local: windowed trajectory estimation per driver (smoothed — use future data; the user
  prefers the Kalman/sequential family but notes forward-only throws away the backward
  half; B's FB-RTS pass is necessary but not sufficient).
- Global: ONLY genuinely-constant parameters — anchor/loop positions, per-loop biases,
  clock structure — estimated across windows and **across all drivers** (and plausibly
  sessions).

## 4. Sector times are measurements, not truth

- User concern: "we don't know what sensor error is on any of these measurements." Stop
  treating range gates as exact.
- Observability note (admiral): per-loop TIME bias is degenerate with anchor POSITION
  error for one car at one speed (Δt ≈ Δs / v), but speed diversity across
  drivers/laps at the same loop separates them → loop calibration is observable from the
  all-driver ensemble, which is where the user suspects the global solve belongs.
- Gate epistemics change: the 50 ms bar becomes consistency with *calibrated* loops.
- Wave-4's F3 residual decomposition is the first empirical test of how large this
  calibration term is — feed its result here.

## 5. Ribbon curvature shrinkage (user, 2026-06-12, post-launch addendum)

- User-identified mechanism for the ribbon arc shortfall: **median-of-cloud on a curved
  band biases to the inside of every corner** ("you'd always shallow out the turn").
  Two stacked pulls: (a) geometric — the centroid/median of a curve segment's
  neighborhood sits inside by ≈ κh²/6 (local-averaging curvature shrinkage); (b)
  sampling — racing lines cluster at the inside kerb at apex, so the cloud median
  starts inside before geometry applies. Order-of-magnitude check: h≈10 m, R≈50 m →
  ~0.3 m/corner → metres per lap → consistent with Spa ribbon 6941.6 m vs official
  6949.5 m. Tight corners worst-hit.
- Design implications: (1) replace median consensus with curvature-aware local fits
  (local arc/quadratic regression cancels the leading-order bias); (2) preferably move
  ribbon estimation INTO the global calibration solve constrained by integrated speed —
  the speed channel measures true path length and is blind to inward shallowing, so a
  jointly-estimated ribbon cannot silently shrink corners.
- H2 pre-test should test this mechanism explicitly: shortfall should correlate with
  corner curvature inventory per circuit, not distribute uniformly.

## 6. Categorical acceleration terms (user, 2026-06-12, post-E4)

- Longer-term: model acceleration roughness with categorical/state-dependent terms rather than
  bucketing windows into turns/straights/braking regimes — i.e., σ_a as model structure
  (continuous function of state or labeled actuation category) instead of discrete window
  classes. Explicitly delayable: E4 achieved chi² 1.00/1.00 with stationary-per-window
  roughness at 10-30 s; revisit when per-regime held-out chi² shows miscalibration.

## 7. Non-orthogonal inertial uncertainty frames (user, 2026-06-13, parked)

- User's gut on the corner shrinkage: the deeper fix may not be "Cartesian with a bias term"
  but uncertainty captured in a non-orthogonal inertial frame chosen so the dynamics are
  near-zero-mean and well-conditioned — analogous to equinoctial elements in orbit
  determination (coordinates that absorb the dominant secular behavior so the residual
  process is honestly zero-mean). Deliberately parked as excessive for now; mean-compensation
  in Cartesian (E8) is the first-order test. Revisit if E8 leaves structure on the table.

## Disposition

- Wave 4 (cmdr-448-fix1): NOT steered; bounded scope stands.
- If wave 4 → "null stands clean": this note + wave-4 F3 evidence = the agenda for the
  user's strategy-brainstorm checkpoint (contract amendment 2026-06-12: persistent null
  returns to user, never closes the epic unilaterally).
- If wave 4 → a strategy passes: this note still seeds Phase-1 hardening / Phase-2 design
  review (multi-frame constraints matter for force attribution).
