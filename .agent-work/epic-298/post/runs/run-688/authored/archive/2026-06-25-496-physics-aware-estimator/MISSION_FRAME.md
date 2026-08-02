# Mission Frame — #496 / #507 Physics-Aware Filter Rebuild

Map-first frame. Architecture artifacts are rich here (physics packet + 5 decision
anchors), so the full frame is required — this is not a trivial change.

## Intent
Land an **evolutionary** extension of the existing trajectory-estimation machinery
(`struct:preprocessing` Matérn smoother + `struct:physics.layer2` kind=3 / raw-speed)
that recovers the **real sharp braking knee / longitudinal transients** the blind
position-smoothness prior currently rounds away — so `braking_view` / `lateral_view`
parameters and the C1 `car_prior` ceiling stop under-calling. Outcome is a per-session
**measurement** improvement with a GO/CONTEXTUAL/NO-GO verdict on the chosen mechanism,
reached via an explore-then-decide worktree portfolio. NOT a full smoother replacement.

## Affected Capabilities
- **`purpose:physics_estimation`** (physics parameter measurement) — the downstream
  consumer of the trajectory; braking/lateral frontier fits are corrupted today.
- **Trajectory estimation** (`struct:preprocessing.trajectory` smoother/calibration) —
  the locus of the defect; spikes extend it (kind=3 channel, process noise, mean fn) or
  add a parallel longitudinal estimator beside it.
- **`struct:physics.utilization` car ceiling** (C1 #510) — the flagged downstream
  victim (braking + fast-corner `U` clips at 2.0); re-eval gated as #518.

## Examples / Events
- **Bahrain T1 heavy stop** — raw ≈ −52 m/s² (~5.3 g) vs smoothed ~−39 (4 g); the
  under-read case. The smoother↔layer2 seam (`accel_obs` → `kind=3` → re-smooth) is the
  boundary the spikes act on.
- **Monaco short-straight** — +13 m/s² spurious non-throttle `a_long` vs ~5.6 raw ceiling
  (corner-entry bleed → braking-transition ringing). The generalization failure case.
- **Spa control** — #498 plateau anchor already works; must not regress.

## Structural Anchors
- `struct:preprocessing.trajectory` — `smoother.py` (`StintSmoother`, `AccelObs`, kind=3),
  `calibration.py`, `dynamics.py`, `physics_adapter.py`, `loaders.py` (container).
- `struct:physics.layer2` — `accel_obs.py` (`emit_accel_obs`, `FrontierSamples`),
  `trajectory_refine.py` (`refine_trajectory`, `RefineInputs`), `braking_view.py`
  (`clean_longitudinal_from_raw`, `project_longitudinal`), `session_braking.py`.
- `struct:physics` — `sim_evaluator.py` (the under-call consumer), `physics_simulator.py`,
  `braking_fit.py` / `traction_fit.py` (frontier fits).
- Eval harness: `scripts/validate_refine_505.py` (the #505 scoreboard precursor).

## Governing Constraints / Assumptions
- `decision:two_cycle_external_anchor_design` — **the binding one.** Four #498 invariants:
  anchor is external & un-biased (raw `a_long`, never re-read from a smoothed trajectory);
  plateau-only obs placement; two cycles only; Student-t jerk foundation. Any spike that
  changes the anchor source/placement (M1 onset-shape anchor, M7 raw-denoise anchor)
  **extends/edits these invariants → decision pressure** (see below).
- `decision:smoother_rounds_braking_knee` — the root-cause finding the work attacks;
  also documents that the raw-speed read is *necessary* today (P1b kernel-on-speed failed).
- `decision:ideal_lap_sim_two_sided_evaluator` — the downstream ceiling consumer; a small
  sim-vs-human gap = under-call; the metric the C1 re-eval (#518) reads.
- `constraint:physics_region_no_evo_import` — spikes/synthesis import no evo package.
- Physics evidence rule (ORCHESTRATOR_CONTEXT): new/modified physics model needs
  highest-applicable **L1–L4** truth evidence + units/bounds/invariants.
- `py` launcher; DB-only is N/A here (physics reads the offline FastF1 cache by design).

## Decision Anchors & Decision Pressure
- `decision:two_cycle_external_anchor_design`, `decision:smoother_rounds_braking_knee`,
  `decision:ideal_lap_sim_two_sided_evaluator` — already govern this structure.
- **Decision pressure (NEW, surface at reconcile):**
  1. **"Evolutionary-not-revolutionary"** — extend the existing machinery; reject full
     process-model replacement (M2/M6). Already a confirmed user constraint; record as the
     governing rationale for the rebuild's shape.
  2. **Anchor-invariant extension** — the winning mechanism likely edits
     `decision:two_cycle_external_anchor_design` (e.g., onset-region obs placement beyond
     plateau-only, or a model-denoised anchor source). That amendment is a decision the
     synthesis gate forces; it must stay inside "external & un-biased."
  3. **Retire `clean_longitudinal_from_raw`?** — #507 acceptance asks to re-evaluate the
     raw-speed interim once the knee tracks raw. GO here flips a standing decision.

## Claims / Evidence Surfaces
- **Scoreboard claim (G1):** the common harness reproduces #505's baseline numbers
  (Bahrain/Monaco/Spa knee + ringing) — the trust anchor every spike is measured against.
- **Per-spike claim (G2):** each mechanism's knee-vs-raw + ringing-vs-ceiling deltas vs the
  baseline are honest and reproducible (no overfit / cherry-pick).
- **Synthesis claim (G3):** landed code improves the scoreboard on BOTH a hard-braking and
  a short-straight circuit, carries honest covariance, single canonical path, L1–L4 evidence.
- **Verdict claim (G4):** GO/CONTEXTUAL/NO-GO with the dashboard as traceable evidence;
  retire-`clean_longitudinal_from_raw` re-evaluated.

## Map Confidence / Staleness / Disputes
- `struct:physics.layer2` / `struct:preprocessing.trajectory` packets are **high
  confidence, current** — recently reconciled (#508/#510). Low staleness risk.
- **Open Question (physics packet):** trajectory consumption bypasses the artifact
  boundary; `session_fit.py` is a 2nd FastF1 entry point. A spike touching loaders should
  not be silently trusted to follow the artifact boundary — note in handoff, route any
  boundary change to Triage, do not let a spike quietly re-plumb it.

## Out of Scope
- Predictive output (measurements only — `non-goal` in the #496 spec).
- Full process-model replacement (M6 collocation, M2 longitudinal swap).
- `#499` named-CdA interface and `#504` `smoother.py` split — **opportunistic-if-intentional
  only** (a deliberate sub-task if a spike lands on them; otherwise untouched).
- Wiring physics estimates into evo prediction (`constraint:physics_region_no_evo_import`).
