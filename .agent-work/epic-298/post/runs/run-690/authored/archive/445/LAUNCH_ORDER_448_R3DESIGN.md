# Launch Order: `cmdr-448-r3d — issue #448 round-3 architecture design (design-only wave)`

Commanders start cold. Everything you need is pasted here.

## Mission

Produce the **round-3 estimator architecture design** for the Phase 1 competition — a design document plus cheap empirical pre-tests, NO full build. The design returns to the human for review before any build wave. Run the `constellation-commander` skill end to end on this bounded scope in the existing cmdr-448 worktree, new work area `.agent-work/issue-448-round3/`, branch `issue-448-estimator-competition` (PR #468 deliberately unmerged — the prior code is your substrate and baseline, NOT sacred).

## Why round 3 exists (pasted history)

Round 1+2 (waves 3-4): two strategies — A batch LS/RTS whole-session, B sequential EKF/UKF+FB-RTS — both fail gate (a) (sector-crossing ≤50ms) at 1.5-6.8× tolerance per-lap RMS on held-out sessions, after full decontamination (A's covariance bug fixed: truth-anchored chi² 1141→1.50; B's long-race bug fixed; frozen knobs byte-identical; no gate softened). CLEAN NULL. Residual chi² still 400-1100 → unmodeled error remains. F3 decomposition: a calibration common-mode term carries 43-68% of the strategies' anchor residual — a SYSTEMATIC NEGATIVE SPEED-SCALE BIAS (estimators think the car covers less distance than it does). Verdict-neutral (scatter alone busts the gate) but architecturally diagnostic.

## The design brief (the human's direction — binding as the design's skeleton)

Read `C:/Programs/f1Brainz/.agent-work/445/DESIGN_NOTES_ROUND3.md` (the user's round-3 design seed, captured verbatim-in-substance). Core elements:

1. **Multi-frame**: ribbon frame for geometric constraints (containment, closure, anchors); pseudo-inertial local-velocity frame for dynamic constraints (acceleration/friction-ellipse, jerk plausibility). No single frame "tells you everything."
2. **Windowed local solves**: window sized to the information/reliability horizon (dynamics correlation ~seconds). Three relationships per window: residuals within; consistency with the window before; consistency with the window after. Overlap disagreement is itself a data-quality signal. NO whole-session trajectory coupling; NO driver-consistency priors (they launder driver variation into suspect data).
3. **Two-level solve**: local = windowed smoothed trajectories per driver (use future data — smoothing, not filtering). Global = ONLY genuinely-constant parameters: sector-loop positions AND time biases, clock structure, **and the ribbon geometry itself** — estimated cross-driver (speed diversity at a loop separates position-bias from time-bias) and possibly cross-session.
4. **Sector times are measurements, not truth**: per-loop estimable bias; the 50ms gate becomes consistency with *calibrated* loops. (Gate changes still require Admiral float + human ratification — design for it, don't apply it.)
5. **The ribbon recursion (user-flagged)**: the current ribbon is a consensus racing line built from RAW positions only (pooled cloud → 5m median-grid → closed periodic cubic spline; never uses speed data; Spa arc 6941.6m vs official 6949.5m ≈ 0.1% short ≈ 100ms/lap). Cleaned trajectories imply a better ribbon → the ribbon's spline coefficients are circuit constants and belong IN the global calibration solve (iterate or co-estimate to convergence). Design this loop explicitly: update schedule, convergence criterion, divergence guard.

## Mandatory cheap pre-tests (empirical, before the design freezes — hours, not days)

- **H1 — curvature-offset factor**: does the existing measurement model map integrated speed directly onto ribbon arc, omitting the (1 − κℓ) path-element correction for lateral offset ℓ on curvature κ? Inspect the round-1/2 code; quantify the implied bias on one session (predicted sign: negative speed-scale — matches F3). If confirmed, this is a measurement-model fix that round 3 inherits for free.
- **H2 — ribbon arc bias**: reconcile ribbon arc length against per-lap integrated speed across drivers on 2-3 circuits; quantify the systematic shortfall and whether a single per-circuit scale parameter absorbs it.
- Pre-test results go IN the design doc as evidence anchoring the architecture choices.

## Deliverable / Done-when

`docs/physics/round3_estimator_design.md` (or equivalent under docs/physics/): the architecture spec — state vectors per level, frames and the constraint placement map, window mechanics (sizing rule, overlap relationships, the three residual relations), the global calibration solve (parameters, observability argument, ribbon-update loop), measurement models incl. the curvature-offset correction, how the EXISTING harness/gates consume round-3 output unchanged, build-wave decomposition (gates for a future build), and the H1/H2 pre-test results. Committed on the branch, pushed. NO production estimator code in this wave (pre-test scripts in scripts/ are fine).

## Pre-Rulings

1. Design must compete on the UNCHANGED #446 harness (any gate-calibration proposal is floated, designed-for, not applied).
2. Frozen session split stays for the eventual round-3 run (tuning={Belgian Q, Spanish R, British R}, held-out={Belgian R, British Q, São Paulo R}).
3. Reuse-don't-rebuild: round-1/2 ribbon builder, gates, competition machinery, loaders are the substrate; name what round 3 keeps, modifies, replaces.
4. No re-pull; raw streams; decimetres; offline cache (same data rules as all waves).
5. The design doc is for the HUMAN to review — plain-English architecture narrative first, math beneath, OD vocabulary welcome (the user thinks in orbit-determination terms).

## Inherited Latitude

Yours: design content, pre-test implementation, doc structure, branch commits/pushes. Float: gate changes, anything outside design+pre-tests, merging, issue filing. The design itself goes to the human — end your run with it as the centerpiece of your report.

## Workspace / File Ownership

- Worktree `C:/Programs/f1Brainz-worktrees/cmdr-448` (exists), branch `issue-448-estimator-competition`. New work area `.agent-work/issue-448-round3/`. Prior packages `.agent-work/archive/2026-06-12-issue-448*/` are read-only reference.

## Inherited Context (platform invariants — unchanged)

- `py` never `python`; tests `py -m pytest tests/...`; cd worktree root before git/gh; crews via Agent tool + registry shim; piped empty stdin for headless crews; utf-8 child env; engine attach-then-advance for artifact checks; lease re-claim `--force` if stale; heartbeat before >25min steps; simplification_limits before review; commit+PUSH after every gate; AGENT_FEEDBACK + lessons-delta at `review`; final turn only when DONE or BLOCKED; poll long compute foreground ≤10 min; never end a turn to float something inside your latitude.

## Data Locations

- FastF1 cache `C:/Programs/f1Brainz/outputs/cache`; season DBs `C:/Programs/f1Brainz/data/f1_data_<year>.db`; ribbons + competition checkpoints in-worktree under `.agent-work/archive/2026-06-12-issue-448*/`; measurement model `docs/physics/measurement_model.md`.

## Budget

Opus commander, Sonnet crews. Design + cheap pre-tests — this should be a SHORT wave. If a pre-test balloons, bound it and note the cut.

## Return Shape

1. **The design** (path to the committed doc) + a plain-English executive summary of the architecture for the human.
2. **H1/H2 pre-test verdicts** with numbers — especially whether the curvature-offset omission is confirmed and how much of the speed-scale bias it explains.
3. Proposed build-wave decomposition (gates, rough sizes).
4. Branch/PR state (push, do NOT merge); map impact; triage candidates; workflow feedback; floated user-decisions.
