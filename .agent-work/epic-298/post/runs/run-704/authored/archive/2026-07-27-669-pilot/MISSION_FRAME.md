# Mission Frame — #669 3-circuit end-to-end pilot (tracer bullet)

**Map note (shrunk frame, justified):** the durable arch map (`docs/architecture/index.md`) is reconciled only
through #601 (`299313cf`); ALL six epic-659 stages (C/D/E/#664/#666 fingerprint/#667 join/#668 panel) are
deferred new-leaf nodes for the #671 closeout reconcile, so the map carries NONE of them. This is stale-BY-DESIGN
(the epic fenced every stage's map edit to closeout) and my launch order fences me OFF `docs/architecture/*`.
Therefore I plan from **code (source-verified) + the epic-659 ADMIRAL_LOG + the Explore stage-map**, not the
durable map. Frame is shrunk accordingly; no map-trust gate needed because I do not plan against the stale map.

## Intent
Wire the six landed stages into ONE invocable pipeline and run it on Monaco/Belgium/Great Britain (2023-Q,
on-disk) to prove the MACHINE runs end-to-end. Tracer bullet gating the season run (#670). NOT signal-sizing.

## Affected capabilities
- `struct:physics.segment_map.derivation` (C/#662) — per-weekend tiling.
- `struct:physics.layer2` grip baseline (D/#663) — grip G, mu=0 sigma+ directed uncertainty.
- `struct:physics.utilization` (E/#664) — reference laps + class-grain observables (chains C live + optional D).
- `struct:physics.fingerprint` (G/#666, H/#667) — hierarchical fit + the join.
- `struct:physics.instrument_panel` (#668) — variance/replication/scorecard dry-run.
- NEW (this issue): a thin **pilot orchestrator** capability that composes the above per-circuit + collects the
  C/D/E/H GATING verdicts + emits a report. Lowest-dimensionality: wiring only, no new model.

## Structural anchors (source-verified entry points — see notes-669.md table)
- C: `derive_segment_map()` / `scripts/derive_segment_maps.py`; gating `scripts/validate_segment_map_662.py`.
- D: `run_grip_batch()` (module driver, no CLI); gating harnesses `test_grip_heldout.py` / `test_grip_synthetic_recovery.py`.
- E: `scripts/build_class_utilization_observables.py` (`--validate` runs jackknife+positive-control).
- G: `fit_driver_fingerprints()` / `scripts/fingerprint_bounded_validation.py`.
- H: `join_weekend_prior()` (pure) / `scripts/join_bounded_validation_667.py`; gating `test_join.py` t7_1..t7_4.
- PANEL: `scripts/instrument_panel_668_report.py`.
- Telemetry seam confirmed offline: `session_fit.load_quali_session(..., offline=True)` reads durable telemetry
  store first, FastF1-cache fallback is `offline=True` (no network), src/physics never imports fastf1 (#503).

## Governing constraints / assumptions (from launch order — binding)
- OFFLINE ONLY (no FastF1 online); artifacts to ISOLATED own-DB/scratch, NEVER tracked `data/f1_data_*.db`,
  NEVER the 38GB FastF1 cache; `git checkout -- data/f1_data_*.db` on any Modified.
- Reversibility: code git-revertible, run artifacts regenerable. detached + STATE-NOTE-FIRST before long stages;
  park-on-hang (precise diagnosis, no thrash).
- Consume LANDED frozen sets (#660 layer2 + #666 fingerprint + #668 REPLICATION_*); mint NOTHING (a needed
  threshold is a FLOAT to the Admiral).
- Strictly-pre causal cutoffs preserved (no race-outcome leakage). No baked normality (Student-t σ preserved).
- Interpreter PIN `.../pythoncore-3.14-64/python.exe`; `.pth` guard on bare scripts; pyright-0 on new modules.
- Map fence: notes-669.md + 669-cartography/ only; feedback trio under staged-feedback/669-pilot/ + FENCE.md.

## Decision anchors / decision pressure
- **decision:pilot-fresh-vs-archived** — the pipeline attempts the fresh C/E telemetry compute; on
  FastF1-fallthrough OR wall-time hang it PARKS that stage and falls back to the archived `fp_slice_2023Q.db`
  observables for downstream G/H/PANEL, recording the gap. @grade: guess · settle: g1 probe on GB.
  Within latitude (park-on-hang + report-the-gap doctrine); Admiral float ONLY if fresh cannot run offline at all.
- **decision:two-segmap-paths** — C's persisted `segment_maps.db` vs E's live in-process re-derivation both exist;
  pilot runs C+gating as the "valid maps" deliverable AND lets E re-derive live (what feeds G/H); do NOT unify
  (out of scope). @grade: settled/inherited (the stages shipped this way). TRIPWIRE (critic #4): the pipeline
  asserts per-circuit consistency (segment count / boundary signature) between the two maps and flags any
  divergence — not unifying is fine; running one while validating the other silently is not.
- **decision:pass-vs-limitation-boundary** — a C/D/E/H GATING check that FAILS = the MACHINE IS BROKEN (float/reopen,
  NOT a complete "honest finding"); the ONLY sanctioned complete-with-gap outcome is a DATA-COVERAGE PARK
  (fresh C/E unavailable offline → provenance-stamped archived fallback). @grade: settled/measured (critic #2 fix).

## Claims / evidence surfaces
- Acceptance = one command → 3 circuits produce {valid maps, fitted G + held-out score, populated observables,
  smoke-fit fingerprint, panel dry-run} + every C/D/E/H GATING passes; report names breakage + #670 implications.
- Evidence: per-circuit gating JSON/artifacts in isolated scratch; the report; pyright-0; green tests on 3.14.

## Out of scope
Interpreting signal sizes (that's #670); the season run (#670, HITL); any new method/model; backfill; touching
the live stages' internals; unifying the two segment-map paths; docs/architecture edits (#671).
