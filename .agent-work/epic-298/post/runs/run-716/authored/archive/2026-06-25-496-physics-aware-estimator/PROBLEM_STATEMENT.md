# Problem Statement — #496 / #507 Physics-Aware Filter Rebuild

**Work id:** 496-physics-aware-estimator · **Resolved:** 2026-06-24 (interrogation)

## Capability (present-tense)
A physics-aware trajectory estimation step that recovers **real sharp longitudinal
transients** (heavy brake-onset, ~5 g) and transient-region behavior that the current
**blind Matérn position-smoothness prior corrupts** — so downstream physics parameters
(`a_b`, `b_b`, grip ceiling) and the C1 car-capability ceiling reflect reality, not
over-smoothed kinematics. A sharp ~5 g decel becomes a *predicted feature* of the
dynamics, not noise the prior rounds away.

## Why now (super-epic #509 context)
This is the **F-layer (foundation) bottleneck**. C1 #510 (CONTEXTUAL) found
braking + fast-corner driver-utilization **NO-GO** because the ceiling under-calls
(`U` clips at 2.0) — re-eval gated on #496 → #518. The blind smoother is "making other
steps harder." Chosen over a new C-output because it unblocks the C-phase. This run
**reverses the 2026-06-23 "post-epic" deferral of #507** — now pulled in because C1
concretely demonstrated it as the blocker.

## Scope = #507 core (evolutionary, not revolutionary)
Recover the sharp braking knee / transient so it tracks the raw sensor, going **beyond**
#498's plateau anchor (which #505 proved Spa-specific: fails on Bahrain heavy-onset and
Monaco short-straight ringing).

**CONSTRAINT (user decision, 2026-06-23/24): evolutionary step(s) that EXTEND the
existing Matérn + kind=3 + raw-speed machinery — NOT a full reorg.** Full process-model
replacements rejected: **M6** (collocation / forward-sim joint trajectory+param fit) is
OUT; **M2** (longitudinal process-model swap) demoted — its physics-residual spirit lives
inside the anchor / 1D approaches.

## Deliverable shape (explore-then-decide portfolio)
1. **Parallel spikes**, each in its own **worktree**, each prototyping ONE evolutionary
   mechanism, measured on a **common scoreboard**.
2. **Synthesis gate**: pull the promising pieces together, measure combinations, pick best.
3. **Build the chosen approach** toward #507 acceptance; **set-aside-incomplete allowed**
   (remainder → issue + pickup note) per the #509 mandate.

**Done-done bar (#509):** full test coverage · honest covariance (first-class) · single
canonical execution path · traceable data→scoreboard → **GO / CONTEXTUAL / NO-GO** verdict.

## Candidate slate (wave 1 — commander's call, all evolutionary)
- **M4** regime-gated process noise — let the prior breathe at brake-onset (heteroscedastic
  jerk variance gated by brake telemetry + speed-derivative).
- **M1** model-shape transient anchor inside kind=3 — anchor the `a_b + b_b·v²` onset shape,
  not just the sustained plateau (direct evolution of #498).
- **M7** model-aware raw-speed denoise → kind=3 anchor — promote raw speed (shows 5.3 g) to
  primary longitudinal truth, 1D physics-residual/TV denoise that permits the model onset
  step, feed as high-confidence anchor; targets retiring `clean_longitudinal_from_raw`.
- **M3** decoupled 1D physics-constrained longitudinal filter on the speed channel —
  root-cause (speed is the only good longitudinal observable; position is jitter-dominated).
  A parallel estimator, not a position-smoother replacement.
- **M8** semi-parametric onset mean function — change-point/ramp mean keyed to brake-apply
  time; the GP only smooths the residual around a physically-shaped step.

**Synthesis-stage ride-alongs** (not standalone spikes): robust/Huber speed likelihood;
curvilinear arc-length frame with decoupled long/lat length-scales; **M5** IMM
(interacting-multiple-models) if switching proves necessary but M4 isn't enough.

## Eval contract (the scoreboard)
Reuse / extend `scripts/validate_refine_505.py`. Cases:
- **Bahrain T1** — heavy stop from ~330 km/h, raw ≈ −52 m/s² (~5.3 g) vs smoothed ~−39 (4 g).
- **Monaco** — short-straight ringing, +13 m/s² in non-throttle vs ~5.6 raw ceiling.
- **Spa** — control: the plateau anchor already works here; must not regress.

Metrics: **braking-knee vs raw sensor** (track within an agreed tolerance);
**non-throttle ringing vs raw ceiling** (bring under). Acceptance (from #507): knee tracks
raw on BOTH a hard-braking AND a short-straight circuit; Monaco ringing under raw ceiling;
THEN re-evaluate retiring `clean_longitudinal_from_raw`.

## Constraints / decisions to honor
- `decision:smoother_rounds_braking_knee` — the root cause being attacked.
- `decision:two_cycle_external_anchor_design` — the #498 invariants (external un-biased
  anchor = raw `a_long`, never re-read from a smoothed trajectory; plateau-only obs
  placement; two cycles only; Student-t jerk). Any new anchor must respect these or
  consciously, documented-ly extend them (a decision candidate if it changes them).
- `decision:ideal_lap_sim_two_sided_evaluator` — the downstream consumer (a small
  sim-vs-human gap is the under-call signal).
- `constraint:physics_region_no_evo_import`.
- z-map / terrain (#497) + real `rho` (#500) are now first-class inputs available to use.

## Decision candidate (NEW — surface at reconcile)
**"Evolutionary-not-revolutionary"** governs the filter rebuild's structure: extend the
existing Matérn + kind=3 + raw-speed machinery; reject full process-model replacement
(M2/M6). Records *why* the rebuild took the shape it did.

## Out of scope
- Predictive output (per-session measurements only).
- Full collocation / process-model replacement (M6 / M2).

## Opportunistic-if-intentional (user, 2026-06-24)
- **#499** named-CdA interface and **#504** `smoother.py` split MAY be captured if a spike
  naturally lands on them — but only **intentionally and tracked** (a deliberate gate/sub-task,
  not incidental drift). Default remains out of scope; pulling either in is a recorded choice.

## Open map flag (note, not in scope)
Physics packet Open Question: trajectory consumption bypasses the artifact boundary
(`session_fit.py` is a 2nd FastF1 entry point). Note for any spike touching the loaders.
