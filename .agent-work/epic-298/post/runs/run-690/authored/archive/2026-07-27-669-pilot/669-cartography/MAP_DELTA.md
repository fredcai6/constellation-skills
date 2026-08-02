# Map delta — #669 pilot (staged for the #671 closeout reconcile)

**FENCE:** this run is fenced OFF `docs/architecture/*` per LAUNCH_ORDER-669 (the map reconcile is #671). This
file records the structural impact as prose for the #671 cartographer to fold in — NO map edit was made here.

## New structural node
- **`struct:physics.pilot`** — `src/physics/pilot/` (`__init__.py`, `pipeline.py`) + `scripts/run_pilot_669.py`
  + `scripts/verify_pilot_results_669.py`. A THIN end-to-end **orchestrator** (leaf, ~44KB pipeline.py) that
  composes the six landed epic-659 stages into ONE offline per-circuit command, collects each C/D/E/H GATING
  verdict + six acceptance slots + `fresh|fell-back` provenance into a results JSON + a markdown report. Pure
  consumer — imports and calls the landed stages; owns no model, no frozen constant.

## New capability
- **`capability:pilot-orchestration`** — run the full C→D→E→G→H→PANEL chain per circuit, offline, isolated
  own-DB, resumable, with a per-stage wall-time-budget auto-park → archived-observables fallback (provenance
  stamped), a two-segment-map consistency tripwire, and non-empty/finite gating.

## Edges (consumes, read-only — no reverse coupling introduced)
- `struct:physics.pilot` → `struct:physics.segment_map.derivation` (C: derive_segment_map + split_half_boundary_drift)
- `struct:physics.pilot` → `struct:physics.layer2` grip_baseline/grip_batch/grip_store (D: run_grip_batch, held-out)
- `struct:physics.pilot` → `struct:physics.utilization` (E: build_class_utilization_observables CLI, subprocess)
- `struct:physics.pilot` → `struct:physics.fingerprint` fit + join (G: fit_driver_fingerprints; H: join_weekend_prior)
- `struct:physics.pilot` → `struct:physics.instrument_panel` (PANEL: run_panel dry-run, instrument 1)
- Import boundary respected: pilot is under `src/physics/`, imports only physics-region modules; no evo import.

## Decision anchors introduced (for #671 to record as durable if it agrees)
- `decision:pilot-fresh-vs-archived` @grade: settled/measured — FRESH C/E telemetry compute is the default
  (g1 probe: offline + ~65-90s/circuit, all 3 ran fresh); the archived `fp_slice_2023Q.db` observables are the
  per-stage-timeout/park-on-hang net only, provenance-stamped.
- `decision:two-segmap-paths` @grade: settled/inherited — C's persisted `segment_maps.db` and E's live
  in-process re-derivation both exist; the pilot tripwires their consistency (segment count) but does NOT unify
  them (unification is out of scope; a candidate for a future issue if #671 judges it worth one).
- `decision:pass-vs-limitation-boundary` @grade: settled/measured — a C/D/E/H GATING FAIL = machine broken
  (report/float); the only sanctioned complete-with-gap outcome is a data-coverage PARK (provenance-stamped).

## Claims / evidence
- `claim:pilot-runs-end-to-end-3-circuits` — VERIFIED: Monaco/Belgium/GB 2023-Q all provenance=fresh, all C/D/E/H
  gating PASS, all 6 slots ran, no tripwire (flags=[]); reproduced landed numbers (GB VER +5.625s, corner_share
  0.42174533307785167). Report: `docs/physics/pilot_669_report.md` (committed).

## Map-confidence note
The durable arch map (`docs/architecture/index.md`) is reconciled only through #601; ALL epic-659 stages
(#661/#662/#663/#664/#666/#667/#668 + now this #669 pilot node) are deferred new-leaf nodes awaiting the #671
closeout reconcile. #671 should fold in this `struct:physics.pilot` node alongside the six stage nodes.

## Triage candidates raised this run (routed at spine triage step)
- tc1: `run_pilot_669.py` default `--report-path` writes into tracked `docs/physics/` on a bare run (no `--out-dir`).
- tc2: critic-#3 pure-decider negative tests sit under a `test_downstream.py` fixture-level `skipif` (latent vacuity
  if fixtures absent; executed here with 0 skipped).
