# Problem Statement — issue #446 (Phase 0a trajectory grading harness)

## Confirmed capability (present tense)

The system gains a **permanent, read-only trajectory grading harness** that scores any
candidate per-lap trajectory product — `s(t)` (arc-length along the track) or equivalent,
**plus covariance** — against the session's official lap/sector truth and the raw telemetry
streams. It is the fixed competition field every future estimation strategy is graded on.

## Scores the harness computes

- **(a) Sector-anchor gate** — predicted sector-crossing times vs official sector times;
  initial tolerance ~50ms (revisit after 0b). Sector-loop arc-length positions along the
  ribbon are **NOT published** and are treated as per-circuit calibration parameters
  (estimated/supplied with uncertainty), never hard-coded.
- **(b) Covariance-consistency gate** — reduced chi-square ≈ 1 on residuals; the reported
  covariance must honestly describe the error.
- **(c) Cross-residual DIAGNOSTIC (never a gate)** — fit a per-lap inter-stream time offset
  as a free parameter; compare integrated-speed arc length vs position-derived arc length
  with lap closure. Report fitted offsets per lap/session. The two streams' clock
  pathologies are NOT assumed independent.

## Bounds

- Read-only over already-collected telemetry (offline FastF1 cache; **no re-pull**) + DB
  sector/lap truth.
- **No estimator work** in this issue. The harness must run against a trivial **strawman**
  (FastF1's own merged/interpolated `get_telemetry()` product wrapped as a 'trajectory')
  to prove it discriminates.
- Harness shipping code lives in the **physics region** (`src/preprocessing/`, new
  submodule); exploration in `scripts/`. **No imports from evo.**
- Raw per-stream input only: `session.car_data[driver]` / `session.pos_data[driver]`. The
  merged product is allowed ONLY inside the strawman candidate (the artifact under study).

## Done-when

Harness runs on **≥3 sessions** (prefer 2022-2025; ≥1 race + ≥1 quali), scores the strawman,
emits a **machine-readable JSON report** with a stable documented schema (producer +
`docs/report_schemas/` doc together); scoring primitives are **unit-tested** with
truth-anchored L1-L4 evidence.

## Protected intent

- **Honest null is a complete deliverable.** A measured negative (e.g. sector-anchor scoring
  cannot discriminate at ~50ms with unpublished loop positions) is reported with the same
  rigor as a win and feeds 0b's gate.
- Covariance honesty matters more than point accuracy (orbit-determination framing: sector
  times are range gates, clock biases are nuisance states).
- The harness must **discriminate**: a good trajectory passes, the strawman's known
  pathologies (sawtooth accel from differentiated interpolated position, time-base error)
  must show up in the scores.

## Residual ambiguity

None requiring the Admiral before planning. All open sub-questions (anchor co-estimate vs
supply mechanism, exact JSON schema fields, which 3+ sessions) fall within Commander
latitude per the launch order's Inherited Latitude section.

## Authority

Resolved by the Admiral's LAUNCH_ORDER_446.md (8 pre-rulings + honest-null clause +
inherited latitude). The Admiral is the human-reachable authority in this constellation and
has front-loaded every interrogation answer; no further human confirmation is required to
proceed to planning.
