# Mission Frame — #670 season-scale run (epic #659 Wave 6, Build-1 culmination)

## Intent
Run the landed #669 pilot machine (C→D→E→G→H→PANEL) over the FULL 2023 season (22 rounds ×
per-round 20-driver grid), OFFLINE, killable, producing (1) the season instrument-panel report
over the full corpus and (2) a strictly-pre held-out-weekend diagnostic that SIZES the join's value.
This is EXECUTION + the DIAGNOSTIC — no new model (ruling 4). The map for this area is un-reconciled
(deferred to #671); I framed against the SOURCE (pipeline.py, join.py, instrument_panel_668_report.py,
fingerprint/fit.py) directly, verified read, not against a stale packet.

## Affected capabilities (read-only consumers; this run adds run-adapters, not model behavior)
- The 6 landed epic-659 stages (segment map C, grip-G D, class-grain utilization + reference-lap E,
  driver fingerprint G, fingerprint×composition join H, instrument panel) — all consumed as-is.
- The join product `join_weekend_prior` (src/physics/fingerprint/join.py) — the Build-1 core the
  fantasy-points metric rides on; the diagnostic sizes its value vs a driver-overall-only baseline.

## Structural anchors (source-verified)
- `src/physics/pilot/pipeline.py::run_circuit` — the per-circuit C→…→PANEL orchestrator. Accepts
  per-call `drivers`, `year`, `session_type`; does NOT forward `budget_s` to `run_stage_e` (stays 180s).
- `src/physics/pilot/pipeline.py::run_stage_e` — subprocess E with `budget_s` kwarg (default 180s),
  auto-park + archived-fallback + provenance stamping. Reads a SCRATCH copy of f1_data (reversibility).
- `scripts/build_class_utilization_observables.py` — E's CLI; writes `driver_class_observables` +
  `reference_laps` via INSERT OR REPLACE on PK (a shared/merged DB accumulates cleanly across rounds).
- `scripts/instrument_panel_668_report.py::run_panel` — the 4-instrument read-adapter, HARD-WIRED to
  CIRCUITS=4 / DRIVERS=4; `enumerate_2v2_partitions` raises unless exactly 4 circuits. The underlying
  module `compare_channels_by_class` works on any two halves → generalizing the split scheme is a
  read-adapter choice, NOT new method.
- `src/physics/fingerprint/fit.py::fit_driver_fingerprints` — strictly-pre via `round_idx <= as_of_round`
  (INCLUSIVE). Leakage-critical: the held-out diagnostic MUST use `as_of_round = R-1` to exclude W itself.

## Governing constraints / assumptions (binding)
- OFFLINE only (no FastF1 online); DB-canonical (no live calls from analysis). Reversibility: never write
  tracked `data/f1_data_*.db` (E reads a scratch copy); scratch/isolated DBs only; never touch the 38GB cache.
- Frozen constants CONSUMED not minted (ruling 2); raising the E timeout is a RUN-PARAM (invocation), not a
  frozen-set edit. Student-t σ preserved end-to-end (ruling 5). Strictly-pre throughout (ruling 3).
- Lowest dimensionality (ruling 4): run the landed pipeline; the season runner + panel-corpus adapter +
  diagnostic harness are read/run-adapters composing landed pieces, building NO new model.
- No frame-kill (ruling 1): a small/fat-σ driver signal is a COMPLETE deliverable.
- Map fence: no docs/architecture/* edits (that's #671). Feedback trio staged under .agent-work/staged-feedback/.

## Decision anchors / decision pressure (surfaced as candidates, not decided alone)
- decision:panel-corpus-split-scheme — the cross-circuit replication split over 22 circuits (the pilot's
  4-circuit 2v2-averaged-over-3-partitions does not scale). Candidate: repeated balanced random split-half
  over the available circuits, fixed seed + fixed count, re-applying the frozen decision rule unchanged.
  @grade: guess · leans g3-implement · settle: implement + document as a read-adapter choice; surface in the
  FOR-OWNER block; float to Admiral if judged beyond read-adapter latitude.
- decision:diagnostic-baseline — the ONE documented driver-overall baseline. Candidate: the join's T7-1
  uniform-composition form (equal shares → unweighted resolved-cell mean), because it is the SAME join code
  path with composition flattened (cleanest apples-to-apples vs the full fingerprint×composition prior) and
  is exactly the "T7-1 unweighted-cell-mean" the launch order names as one of the two allowed forms.
  @grade: guess · leans g4-implement · settle: state + justify in the diagnostic report per #667 TC-1.
- decision pressure: golf-null definition — composition/field-only prediction with NO driver term (the floor
  both priors must beat). Carried as the benchmark; defined precisely in g4.

## Claims / evidence surfaces the run re-confirms
- claim: full per-round 2023-Q coverage across the 3 durable stores (VERIFIED at understand — all 22 rounds).
- claim: the machine runs end-to-end offline at season scale with provenance=fresh where stores cover the round
  (the pilot proved 3 circuits; this sizes over 22).
- claim (leakage guard): the diagnostic's fingerprint fit sees ZERO round-R rows (as_of_round = R-1).

## Map confidence / staleness / disputes
- docs/architecture/* for epic-659 is UN-RECONCILED (deferred to #671) → I did NOT trust it; I read source.
  No gate silently trusts a packet. confidence_flag on every gate: "epic-659 map deferred to #671; framed vs source."

## Out of scope
- 2019–2026 backfill; any Build-2/3 work; MAKING the 3 owner allocation decisions; the #671 map reconcile;
  deleting anything; new models/methods; editing frozen constant sets.
