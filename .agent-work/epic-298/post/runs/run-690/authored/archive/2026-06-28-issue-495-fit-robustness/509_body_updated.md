**Top-down driver for the connected physics â†’ prediction pipeline.**
Spec: `docs/superpowers/specs/2026-06-24-physics-predictive-pipeline-pathway.md` (read it first).

Originating bet: #445 (physics-primary). Builds out the #492 holding candidates and #450. This epic exists to push us to the **desired completion state**, not to schedule a sprint â€” pacing is deliberate (one output at a time), iteration/reachback is expected.

## The bet â†’ the payoff
Lap-time-aggregate features are saturating (~0.80 quali ceiling). The richer feature space is physics-measured car/driver capability. Epic 1 (#485) + Epic 2 (#508) built the measurement machinery; this epic connects it to the predictor.

## Completion state (this epic's done-bar)
Physics features (GO/CONTEXTUAL outputs from Phase C) enter the **weekend-local `race_weekend` evo path** and are A/B-scored against the standing KPIs and the ~0.80 ceiling â€” **either** they raise it (bet pays, pipeline connected) **or** a gate yields a documented negative result that bounds the bet. An unmeasured "built features and hoped" is not a terminal state.

## Per-output done-done bar
Full test coverage Â· honest covariance (first-class artifact) Â· single canonical execution path Â· traceable dataâ†’dashboard â†’ a **GO / CONTEXTUAL / NO-GO** readiness verdict. Set-aside-incomplete is allowed only with the remainder captured in issue space **and** a pick-up note giving a clear resume point. Nothing set aside silently.

---

## Phase F â€” Foundation hardening (prerequisite: trustworthy fit base)
- [ ] #494 â€” persist telemetry to SQLite (reproducible-from-DB fits)
- [ ] #503 â€” single FastF1 entry point (route `session_fit` through the boundary)
- [x] #495 - fit robustness (~4% single-session failures) - RESOLVED (PR #548 fixed 17/19; this run fixed the last: Saudi-DEV empty-speed-stream -> no_speed_stream typed skip; live fit-exceptions 1->0). Spawned follow-ons:
  - [ ] #559 - rebuild the per-session fit store on post-#548/#495 code (stale baseline)
  - [ ] #560 - investigate minimum-flying-laps/sample floor for fit acceptance (thin fits pass as ok)
- [ ] #496 â€” physics-aware trajectory filter rebuild
- [ ] #507 â€” blind smoother corrupts heavy/transient braking
- [ ] #505 â€” cross-circuit validation + per-session calibration of the #498 refinement
- [ ] #504 â€” split `smoother.py` (simplification limits)
- [ ] #475 â€” Phase 1 estimator validation breadth (wets/circuits/pit filtering/thin-n)
- [ ] #476 â€” re-home orphaned physics-characterization scripts
- [ ] #461 â€” trajectory-grading follow-ups

## Phase C â€” Capability-output characterization (the heart; one output at a time, measured not wired)
Active first; the rest are queued and cut/detailed when reached.
- [ ] #510 â€” **Driver utilization on quali (ACTIVE, first)**
- [ ] #511 â€” Race-state ideal lap: fuel-mass anchor + grip-evolution state (queued)
- [ ] #512 â€” Regime-capability vector readiness (slow/fast grip + powerâˆ’drag) (queued)
- [ ] #513 â€” FP-session fits enabler (run physics on FP, feeds the weekend-local path) (queued)

Adjacent characterization-flavoured open work (folded as it bears on "what can the physics produce"):
- [ ] #443 â€” compound-degradation sensors
- [ ] #502 â€” per-PU temperature derating of P_max
- [ ] #499 â€” generic multi-state CdA interface
- [ ] #501 â€” force-residual diagnostics
- [ ] #506 â€” data-driven systematic-uncertainty floors
- [ ] #483 â€” RegulationEra 2026/2027

## Phase P â€” Composition + integration (last; shaped by C's verdicts)
- [ ] #450 â€” physics-derived features into the weekend-local `race_weekend` evo path (direct regime descriptors first; lap-sim demoted to validation)
- Adjacent evo-side: #482 (allfp into quali head), #424 (feature-engineering epic)

---

## Parked (MODEL_SCOPE ratifications)
Standalone downforce identity (â†’ k_df) Â· ICE-vs-deploy split (â†’ deployed-power index) Â· ride-height/rake Â· dirty-air explicit model (quali = clean-aero anchor). Triggers: 2026 active-aero / ERS telemetry.