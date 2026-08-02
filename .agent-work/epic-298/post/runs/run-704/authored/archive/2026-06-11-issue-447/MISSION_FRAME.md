# Mission Frame — issue #447 (Phase 0b instrument characterization)

## Intent
Empirically characterize the raw FastF1 telemetry instruments (`car_data`, `pos_data`)
over the offline cache, and assemble the GO/NO-GO evidence for epic #445's estimator
decision point. Land a measured `docs/physics/measurement_model.md`; ship reusable
characterization analysis in `scripts/` and any durable noise-model reader in
`src/preprocessing/`. No estimator; recommendation only.

## Affected Capabilities
- Trajectory grading / measurement characterization (physics region) — the 0a harness
  graded a candidate trajectory against sector truth; 0b characterizes the *instruments*
  feeding any future candidate. Same capability family, upstream of grading.

## Examples / Events
- 0a strawman grading reports (`.agent-work/archive/2026-06-11-issue-446/evidence/`) —
  the cross-residual per-lap offset ranges there are the F2 signal I must quantify.

## Structural Anchors
- `struct:preprocessing` — `src/preprocessing/`, container (physics region). Work lands here
  (durable readers) and reuses `src/preprocessing/trajectory_grading/` (offline_loader,
  cross_residual, db_truth_loader).
- `scripts/` — non-map characterization analysis scripts (per pre-ruling 5).
- `docs/physics/` — deliverable `measurement_model.md` lands alongside overview.md.
- `docs/report_schemas/trajectory_grading_report.md` — durable contract from 0a; the
  measurement model's chi-square band recommendation informs the covariance gate it feeds.

## Governing Constraints / Assumptions
- `constraint:physics_region_no_evo_import` (overlays/constraints.yml) — no evo imports.
- DB-only data constraint — but telemetry is NOT in the DB (telemetry tables empty); the
  FastF1 offline cache is the only source for raw streams. This is the sanctioned
  exception established by 0a (offline cache + raw streams, never live, never
  get_telemetry). pos_data in DECIMETRES (lesson:fastf1-posdata-decimetres).
- DatabaseManager is NOT read-only — use `file:<path>?mode=ro` sqlite for sector truth
  (lesson:dbmanager-not-readonly; db_truth_loader already does this).
- Physics evidence bar: units/bounds/invariants explicit, truth-anchored, every number
  traceable to script + session.

## Decision Anchors & Decision Pressure
- 0a established: cross-residual is a DIAGNOSTIC, not a gate; sector-anchor + covariance
  are the gates. The measurement model must respect that split.
- **Decision pressure (delegated to my latitude, resolve from evidence, document):**
  (a) the recommended chi-square acceptance band for the covariance gate (F1);
  (b) whether `s_finish` should be a free anchor (F3);
  (c) the time-tag error model class (bias / random-walk / per-batch).
- **Decision candidate for reconcile**: the measurement-model document becomes a durable
  physics contract (like the 0a report schema). Cartographer should fold it in.
- **Floated to human (NOT mine to decide)**: the GO/NO-GO verdict itself — recommendation
  only.

## Claims / Evidence Surfaces
- Claim under test: "FastF1 telemetry is correlatable enough to support trajectory
  estimation." Evidence = measured sampling distributions, quantization, jitter model,
  inter-stream offset stability, per-channel covariances, operationalized against the
  GO/NO-GO criteria over ≥6 sessions / ≥2 seasons incl. a messy session.

## Map Confidence / Staleness / Disputes
- `struct:preprocessing` / `trajectory_grading/` — HIGH confidence, reconciled 2026-06-11
  for #446 (one day ago). No scout/verify gate needed; the map is trustworthy here.

## Out of Scope
- Any estimator/filter/smoother (Phase 1, gated behind this GO).
- Touching evo, data-collection, or the DB schema.
- Deciding GO/NO-GO; merging; closing the issue/epic.
