# 668-cartography — MAP_DELTA (staged for the epic-659 closeout cartographer)

Map fence honored: #668 did NOT edit `docs/architecture/*`. Fold this delta at epic closeout.

## New node
- `struct:physics.instrument_panel` — `src/physics/instrument_panel/` (package, file-level).
  Read-only diagnostic panel (four instruments). Consumes: `struct:physics.fingerprint` (cells,
  read directly), `struct:physics.utilization` (reference laps + driver_class_observables),
  `struct:physics.layer2.pooling` (TwoWayPool), `src/common/student_t` (predictive_t),
  `struct:physics.layer2.frozen_constants` (SECTOR_CALIB_* + the new REPLICATION_* set).
  Emits: `docs/physics/instrument_panel_668_gb2023q_report.md` via
  `scripts/instrument_panel_668_report.py`.

## Edges
- `instrument_panel --reads--> fingerprint.store.get_fingerprint` (UN-AGGREGATED cells; NOT via #667 join).
- `instrument_panel --reads--> utilization.reference_utilization_store (driver_class_observables + reference_laps)`.
- `instrument_panel --consumes--> layer2.frozen_constants (SECTOR_CALIB_* + REPLICATION_*)`.
- `instrument_panel --validates-against--> data.f1_data_2023 lap_times.sector{1,2,3}_time` (official, post-hoc target only).

## Constraint edge
- `claim:instrument_panel_reads_cells_directly` — the panel reads cells/observables directly, never
  through the `#667` join (consumer boundary ruled at #667). Verified-by: the panel modules import
  no `join` symbol; the g3/g7 reviews confirmed no #667 join usage.

## Frozen-constant delta
- `layer2/frozen_constants.py`: `decision:replication-deferred` RESOLVED → the owner-signed
  `REPLICATION_*` set added (values in notes-668.md).

## Decision anchors (record with @grade — see notes-668.md for the grades)
- decision:golf-correction-is-double-centering @grade: settled/measured
- decision:split-half-unit-cross-circuit-2v2 @grade: settled/human
- decision:replication-frozen-set-signed @grade: settled/human

## Follow-ons routed
- #670: per-FIA-sector segment tiling (telemetry-derived) for a genuine composed-sector prediction;
  broader-circuit / full-season breadth. (HITL.)
