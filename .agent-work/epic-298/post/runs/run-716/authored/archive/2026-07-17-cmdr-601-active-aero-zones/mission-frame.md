# Mission Frame

## Intent
Create a source-backed active-aero allowance reference layer for 2026 Driver Adjustable Bodywork opportunity windows and lines, explicitly separate from observed per-car aero state.

## Affected Capabilities
- Physics track/regulation context: existing track profiles can carry DRS opportunity masks; this run adds an active-aero eligibility contract that downstream CdA work can project onto track distance without treating it as telemetry state.
- Data/reference loading: source-backed JSON fixtures/artifacts can be loaded with strict validation and provenance.

## Examples / Events
- FIA 2026 Sporting Regulations B7.1.1: defines full and partial Driver Adjustable Bodywork activation and requires FIA-provided Activation Zone / Low Grip Activation Zone information.
- FIA 2026 Sporting Regulations B7.2.1: requires competition-specific Detection Gap, Detection Line, Activation Line, and related limits.

## Structural Anchors
- `struct:physics` (`src/physics/`): natural home for a read-only regulation/track-opportunity helper consumed by future physics/CdA identification.
- `struct:data` (`src/data/schema.sql`, `src/data/database/`): DB-backed persistence remains possible later, but this gate avoids schema changes because public event-specific rows are unavailable.
- `docs/physics/measurement_model.md`: already records that 2026 observed aero state is missing, preventing conflation with this reference layer.

## Governing Constraints / Assumptions
- `constraint:DB-only data access`: analysis must use canonical DB or committed source-backed artifacts, not live API fallback.
- Launch-order pre-ruling: allowed zones are published track/session/event reference data, not per-car state.
- Generated DB/parquet artifacts are not committed.
- Distances are metres along the official lap/ribbon frame where known; unknown official distances remain null and fail closed for mask projection.

## Decision Anchors & Decision Pressure
- Existing `decision:ideal_lap_sim_two_sided_evaluator` explains telemetry-pooled DRS masks. This run does not reuse `drs_open`; it creates an explicit adapter boundary.
- Decision pressure deferred: whether to promote event-specific active-aero zones into the canonical season DB after FIA event documents become public.

## Claims / Evidence Surfaces
- FIA Sporting Regulations source lines establish the required fields and publication schedule.
- Unit tests must prove strict validation, source provenance, nullable source-gap distances, and distance-mask projection behavior.
- Source findings must distinguish accepted regulatory sources from unavailable event-specific zone documents.

## Map Confidence / Staleness / Disputes
- Public event-specific activation-zone documents are not yet accessible in searched official FIA/F1 public surfaces. Plan therefore builds the interface and source-gap contract rather than inventing distance rows.

## Out of Scope
- No per-car active-aero state inference.
- No generated DB/parquet commits.
- No physics fit/model promotion or production default flips.
