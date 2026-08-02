# Plan decisions — #666 (plan step)

## Design-it-twice / plan-alternatives — NAMED UNTAKEN ROAD (sanctioned skip)
Per LAUNCH_ORDER-666 §"What to build": the CALLER/FLEX/MINIMAL address-space design-it-twice is ALREADY
SETTLED in the spec ("do NOT re-open"). Plan-alternatives at the gate-decomposition level was therefore
run as a single candidate with the alternative named, not a parallel subagent panel (bias-to-yes skip
surfaced here):
- **Taken:** 4-gate decomposition — G1 (#675 diagnosis + frozen-constant pre-registration) / G2 (address +
  vocabulary + store) / G3 (hierarchical fit) / G4 (bounded real-slice validation).
- **Untaken road: 3-gate merge (fuse G1 into G3).** Rejected — loses the diagnosis-first ordering the
  launch order mandates (#675 "resolve as the FIRST task of your plan phase; it gates the class-axis
  intervals") and loses F12 pre-registration-before-first-run ordering. Cold critic independently affirmed
  4 gates as correct (SIMPLICITY lens: "Collapsing to 3 would fuse the #675 diagnosis into the fit and lose
  the pre-registration ordering").
Panel-vs-single choice: single-candidate + named untaken road, justified by the spec-frozen design (a
keystone build, but the load-bearing interface — the address space — was pre-decided by the epic).

## Cold plan critic — dispositions (all findings disposed within delegated latitude; none floated)
- HIGH #675 coverage circular/underpowered on real data → FIXED: G1 pins the #665 synthetic-recovery form
  (known injected truth) driven by the REAL slice's per-cell support counts, N_REPS>=200, coverage reported
  with a binomial CI; held-out real-data coverage is a flagged secondary (different quantity).
- MED-HIGH parent-side leakage false-green → FIXED: G3 cutoff filters the ENTIRE input set (target+parent+
  field); keystone test poisons a NON-target driver round>R row too.
- MED energy-channel coverage unmeasured → FIXED: G1 measures class-axis coverage for BOTH channels; G3
  applies a per-channel shared_floor.
- MED F12 pre-registration timing (post-hoc tuning risk) → FIXED: the 4 constant VALUES are pre-registered
  in the plan now (nominal 0.80; under-coverage bound 0.60 = #665 CALIBRATION_COVERAGE_THRESHOLD; recency
  half-life 5.0 rounds; unresolved-support floor 1.0), frozen before any real run; G1 encodes them verbatim.
- MED ClassVocabulary real F12 verdict sourcing → FIXED: G2/G4 source the verdict from existing f12
  machinery with explicit provenance; never a silent hardcoded PASS.
- LOW-MED sigma_lapsampling dropped → FIXED: G3 carries it as a present-but-zero σ component (mirrors G).
- LOW-MED σ-idempotence scope → FIXED: single structural pricing site + idempotence both asserted.
- LOW .agent-work commit hazard → FIXED: no-.agent-work-commit constraint added to every gate.
- Slice-gen unaudited input (MED) → FIXED: commander generates + verifies the bounded slice (offline;
  row-count, distinct circuits/drivers/classes, no round>cutoff contamination) and records the audit.
- SIMPLICITY/out-of-scope → no findings; 4-gate decomposition affirmed.

## Pre-registered frozen constants (FINGERPRINT_FROZEN — set BEFORE first real-data run, Ruling F12)
- FINGERPRINT_NOMINAL_COVERAGE_LEVEL = 0.80
- FINGERPRINT_UNDER_COVERAGE_BOUND = 0.60  (class-axis empirical coverage below this = materially under-covered)
- FINGERPRINT_RECENCY_HALFLIFE_ROUNDS = 5.0
- FINGERPRINT_UNRESOLVED_SUPPORT_FLOOR = 1.0  (summed n_points below this -> unresolved cell)

## Bounded slice plan (commander-owned, offline)
Generate a 3–4 circuit 2023-Q slice (VER/PER/LEC/SAI) via scripts/build_class_utilization_observables.py
where physics_estimates.db has full 2023-Q coverage. Mix permanents + a street. Write to a scratch DB path
OUTSIDE the committed tree. Verify offline + audit before handing to G1.
