# Mission Frame — issue #446 (Phase 0a trajectory grading harness)

## Intent

Add a permanent, read-only **trajectory grading harness** in the physics region that scores
any candidate per-lap trajectory product (`s(t)` + covariance) against official sector/lap
truth and raw telemetry, emitting a stable machine-readable JSON report. Prove it
discriminates by scoring a deliberate strawman (FastF1's merged/interpolated product). No
estimator work. The map is relevant here (new structural node in `struct:preprocessing`,
new committed report schema), so a full frame is warranted.

## Affected Capabilities

- **(new) trajectory grading** — scores a candidate `s(t)`+covariance via three primitives:
  sector-anchor gate (a), covariance-consistency gate (b), cross-residual diagnostic (c).
  This is the fixed competition field Phase 1 estimators will be graded on.
- **telemetry measurement characterization** (spec Phase 0) — relies on the two-stream raw
  telemetry (`car_data`, `pos_data`) already on disk; the harness consumes raw streams only.

## Examples / Events

- A candidate trajectory passes the sector-anchor gate when its predicted sector-crossing
  times reproduce the DB's per-sector splits within ~50ms (anchors co-fit per circuit).
- The **strawman** (merged `get_telemetry()`): differentiating interpolated jitter-timestamped
  ~4-5Hz position twice yields sawtooth accel + correlated errors; its covariance (if any) is
  not honest → expected to FAIL gate (b) and show structured sector-anchor residuals. This is
  the discrimination proof. An honest null (strawman indistinguishable at 50ms with unknown
  anchors) is an equally complete deliverable.

## Structural Anchors

- `struct:preprocessing` — `src/preprocessing/`, container. Harness lands here as a new
  submodule (e.g. `src/preprocessing/trajectory_grading/`).
- `struct:preprocessing.coordinate_transform` — existing `CircuitGeometry.from_fastf1`
  exposes `marshal_sectors` (coarse marshal loops, NOT the 3 timing-sector loops →
  reinforces anchors-are-unknown). Reusable for ribbon/coordinate handling.
- `struct:sqlite_db` — `data/f1_data_<year>.db` `lap_times` (sector1/2/3_time seconds,
  per-sector durations; sum ≈ lap_time) is the truth source via `src/data/database`.
- `struct:fastf1_api` (offline cache only) — raw `session.car_data`/`session.pos_data`.

## Governing Constraints / Assumptions

- **constraint: physics region isolation** — no imports from evo (`src/evo_predictor`,
  `src/latent_power`, `src/compound_prior`). Harness depends only on physics/preprocessing +
  data/utils + offline FastF1.
- **constraint: DB-only data access** — narrowed exception for Phase 0: reading the FastF1
  cache offline is in-bounds for instrument characterization ONLY; sector/lap truth still
  comes from the DB. The harness never re-pulls (offline cache only).
- **constraint: report schema atomicity** — committed JSON report needs producer +
  `docs/report_schemas/` doc together.
- **assumption: anchors are calibration parameters** — sector-loop arc positions unpublished;
  the scoring API treats them as estimated/supplied inputs with uncertainty, never hard-coded.
- **assumption: streams' clock pathologies not independent** — cross-residual is a diagnostic,
  never a gate.
- **physics evidence bar** — truth-anchored L1-L4 unit tests on scoring primitives; units,
  bounds, invariants explicit.

## Decision Anchors & Decision Pressure

- **decision (spec 2026-06-10):** physics-primary direction; Phase 0a grading field BEFORE any
  filtering — every estimator competes on identical terms. Governs why this is harness-only.
- **decision pressure → durable candidate:** the committed report schema for graded
  trajectories becomes the contract Phase 0b/1 consume. Surface the schema shape as a
  decision candidate at reconcile (Cartographer decides if it is a durable anchor). Within
  Commander latitude to author; flagged for the map.
- **decision pressure:** anchor-acquisition mechanism for the strawman run (co-estimate
  anchors from truth vs supply). Commander latitude (implementation structure). Chosen:
  **co-estimate** per circuit from the candidate + official splits, with reported uncertainty
  — keeps anchors as parameters and avoids importing unpublished constants.

## Claims / Evidence Surfaces

- **claim:** scoring primitives are correct → L1 analytical/known-answer unit tests (synthetic
  trajectory with known anchors/offset recovers them; chi-square of white-noise residuals ≈ 1).
- **claim:** harness discriminates → ≥3-session strawman run produces a report whose numbers
  separate "honest" from "pathological" OR a documented honest null at 50ms.
- **claim:** read-only / no re-pull → offline cache load logs "Using cached data"; no DB writes.

## Map Confidence / Staleness / Disputes

- `struct:preprocessing` status `current`, confidence `high` — but its existing windowed
  estimator is the FAILED first attempt (spec diagnosis). No staleness blocks this run; the
  harness is additive and does not touch `windowed_estimator.py`. No scout step needed.

## Out of Scope

- Any estimator/filter work (Phase 1+). Track-ribbon construction as a shipping product.
- Instrument characterization numbers (Phase 0b). Modifying `windowed_estimator.py` or
  `src/physics/`. Any evo/data-region behavior change. Re-pulling telemetry. Tightening the
  50ms tolerance (revisit after 0b).
