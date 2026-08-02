# #670 Season-scale run — consolidated problem statement (delegated, reconciled vs LAUNCH_ORDER-670)

## The ask (from the launch order, frozen principal)
Run the **full 2023 season** through the landed #669 pilot machine at season scale:
vocabulary tilings -> G(grip) -> C(segment map) -> E(class-grain utilization + scalar
reference-lap recovery) -> G(fingerprint) -> H(fingerprint x composition join) -> instrument panel.
2023 because every durable store is deepest there.

**Deliverable = TWO artifacts:**
1. **Season panel report** — all 4 instruments over the full corpus (cross-circuit replication
   now meaningful across ~22 rounds); the 4 gating verdicts (C/D/E/H) per round + provenance + flags.
2. **Held-out-weekend DIAGNOSTIC** — fingerprint×composition prior vs a driver-overall-only prior,
   per held-out weekend, **strictly-pre (zero leakage)**. ONE documented driver-overall baseline
   (join's T7-1 unweighted-cell-mean OR fit-hierarchy support-weighted — pick + justify). Golf null
   is the benchmark to beat. This SIZES value; it does NOT re-establish join correctness (#667 already did).

Plus a **"FOR OWNER — allocation decisions"** block: evidence for the 3 owner decisions
(variance→Build-2 effort; per-class/per-channel replication→which axes+channel earn join weight;
sector calibration→whether reference-lap work precedes fingerprint work). Present evidence, DO NOT decide.

## Five binding owner rulings
1. **No frame-kill** — a small/fat-σ driver signal is a COMPLETE successful deliverable; route to structural
   work, never editorialize as failure.
2. **Frozen constants (F12)** — consume LANDED frozen sets; mint NOTHING. Raising the E timeout is a
   run-parameter (invocation), not a frozen-constant edit.
3. **Pre-quali** — strictly-pre throughout; the held-out diagnostic has zero leakage.
4. **Lowest dimensionality** — run the LANDED pipeline; build NO new model. Season run = execution + diagnostic.
5. **No baked normality** — Student-t σ preserved end-to-end.

## Reversibility contract (owner AFK)
- OFFLINE ONLY — no FastF1 online calls (pilot proved all 6 stages offline).
- NEVER write tracked `data/f1_data_*.db`; E reads a SCRATCH COPY. Season `processed_telemetry` writes → isolated/scratch DBs only.
- NEVER touch the 38GB FastF1 cache. All run artifacts to isolated paths; committed deliverable = report (+ minimal code), regenerable.
- DETACHED + STATE-NOTE-FIRST; auto-park on hang with diagnosis (no thrash). Killable throughout.

## Coverage verification (launch-order-mandated FIRST action — DONE, all confirmed)
- **f1_data_2023.db** (worktree): all 22 rounds of 2023-Q, 20 drivers each. FP2/FP3 present on 16 rounds;
  6 sprint weekends have only FP1 (rounds 4,9,12,17,18,20 = Azerbaijan/Austria/Belgium/Qatar/USA/Brazil)
  → grip held-out sub-score PARKS on those 6 (honest, D-gate still passes on fit-completes, as Belgium in pilot).
- **physics_estimates.db** (MAIN): all 22 rounds 2023-Q, 10 constructor rows each (fit ok; Netherlands 9/10,
  Japan 7/10 — per-constructor, still substantial).
- **telemetry_store.db** (MAIN): all 22 rounds 2023-Q, 20 drivers each.
- **VERDICT: full per-round coverage confirmed — NO rounds to park for missing data.** No FastF1 pull needed.

## Machine facts that shape the plan (source-verified in src/physics/pilot/pipeline.py + #669 report)
- Pilot HARDCODES `PILOT_DRIVERS`=(VER,PER,LEC,SAI) and `PILOT_CIRCUITS`=3 circuits. Season needs the full
  per-round 20-driver grid × 22 rounds.
- `run_circuit` does NOT forward `budget_s` to `run_stage_e` (stays 180s default). The full 20-driver E loop
  (~14s/driver ≈ ~4.7 min/circuit) WILL exceed 180s → must thread the E budget through as a run-param and
  raise to ~6–8 min/circuit. This is plumbing, not a frozen-constant edit (ruling 2 permits).
- Pilot PANEL runs instrument{1} only; instruments 2/3/4 need cross-circuit official-lap reads + the multi-circuit
  slate → the season run must exercise the full panel over the corpus (a #668/#670 concern to confirm at plan).
- Held-out diagnostic does NOT exist in the pilot — it is the "+ diagnostic" the launch order names (composes
  landed join pieces; NO new model).
- Sizing: single-threaded OFFLINE ≈ ~1.5–2h E-dominated; apply #650 ~2× margin → plan ~2–4h. Per-circuit is
  independent → parallelizable if infra is safe.

## Reconciliation verdict
Ask reconciles cleanly with the frozen launch order. Coverage (the one thing that could have forced an Admiral
float) is fully confirmed. No genuine gap requiring an up-float at understand. Proceeding to map-first plan.
