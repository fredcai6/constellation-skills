# Implementer Handoff

## Gate
g5 (Tier-2 fracture quantification — close-with-number OR bounded-defer-with-number)

## Task
Quantify EACH of the four x7 basis fractures with a NUMBER. Produce a reproducible analysis
(`scripts/tier2_fracture_analysis.py`, ASCII) + a durable writeup `docs/physics/627-tier2-fractures.md`. Every
fracture ends CLOSED (before/after σ number) or DEFERRED (quantified downstream-σ-impact bound). An undecided
fracture, or a deferral with only a label and no number, is a PHASE FAILURE.

## Protected Intent
Defensible numbers, not labels. A bounded-and-quantified deferral is a legitimate research outcome; an unbounded
"we couldn't" is not. Do NOT re-introduce the decoupled-1D a_long failure (documented HONEST-NULL).

## Test Mode
test-after allowed; the analysis script is the evidence, guard any DB-dependent path.

## Close Criteria — one numbered subsection per fracture in the doc
1. **DUAL-CdA (PowerDrag vs Coast) — CLOSED (cite G3).** G3's `cross_view.fuse_dual_cda` already closes this:
   report the real numbers — RBR Monza 2023 Q z=6.80 (REFUSED, genuine disagreement), Mercedes z=2.03 (fused σ
   0.046 m² vs component 0.049/0.056 → ~18% tighter than PowerDrag-only, correlation-honest). State that the
   Coast-vs-PowerDrag CdA correlation is within-session shared mass/ρ (recoverable via the shared systematic),
   and the fusion is cov-aware. CLOSED with a before/after σ number.
2. **GRIP-TRIPLET cross-coupling — CLOSE or bounded-defer WITH A NUMBER.** lateral_mech_grip_g, brake_decel_ms2,
   traction_accel_ms2 are 3 uncoupled fits. The plain cross-session Pearson correlation of the point estimates
   CONFLATES real physical co-variation ("grippy circuits are grippy on all axes") with shared measurement-error
   covariance. SEPARATE them: compute the PARTIAL correlation CONTROLLING for circuit (e.g. within-circuit
   residual correlation, or a circuit-fixed-effect residualization) over a 2023 Q season load from
   `EstimateStore.load`. Report BOTH the raw and the circuit-controlled correlation, and bound how much leaving
   the triplet uncoupled inflates (or fails to tighten) the pooled grip σ — a number (e.g. "the residual
   measurement-error correlation is |r|<=X, so a joint grip solve would tighten the pooled mechanical-grip σ by
   at most ~Y%"). If the data can't identify it, bounded-defer WITH that upper-bound number.
3. **a_long reconciliation — BOUNDED-DEFER WITH A NUMBER (do NOT re-merge).** READ
   `docs/architecture/decisions/decoupled-1d-longitudinal.md` (#523/#546 sections) FIRST. Braking uses the
   decoupled Kalman-RTS filter; Traction/PowerDrag/Coast use `clean_longitudinal_from_raw` — two numbers for one
   a_long, a documented STRUCTURAL HONEST-NULL (re-merge fails circuit-topology-dependently; cite issue #644 for
   the 0%-CPU headless-fit stall if a live re-run is infeasible). Quantify the basis-inconsistency BOUND: e.g.
   the a_b discrepancy between the decoupled vs clean a_long in σ units on real sessions (the #523 table already
   gives per-view shifts — Belgium/Monaco/Bahrain in σ), and translate that into a bound on the cross-view a_long
   inconsistency the split leaves in the basis. DEFER with that σ-impact number + the explicit reason (structural,
   per the decision record). Do NOT re-wire the decoupled path.
4. **SHARED-TRAJECTORY-NOISE — CLOSE or bounded-defer WITH A NUMBER.** Braking/Traction/Lateral share the same
   per-driver smoothed trajectory (`sample_cache`) but bootstrap their covariances as if independent, so their
   cross-view fit errors are correlated by the shared upstream trajectory-estimation error, which no cross-view
   term captures. Bound the covariance-underestimate: estimate an UPPER bound on the correlation-inflation of the
   pooled grip σ from the shared trajectory noise (e.g. via the fraction of each view's fit variance attributable
   to the shared σ_kin, or a perturbation of the shared trajectory). Report the bound (e.g. "ignoring shared
   trajectory noise underestimates the joint braking+traction grip σ by <= Z%"). If not closeable, bounded-defer
   with that number.

## Allowed Scope
- CREATE `scripts/tier2_fracture_analysis.py` (ASCII, guarded for absent DB), `docs/physics/627-tier2-fractures.md`.
- May add a small unit test under `tests/` for any pure helper in the script (optional).
- READ-ONLY: `estimate_store.py` (load the store), `cross_view.py` (G3 fusion numbers),
  `docs/architecture/decisions/decoupled-1d-longitudinal.md` (#523/#546), `pooling.py`, the x7 map at
  `.agent-work/archive/2026-07-17-explore-physics-evo-hookup/excursions/x7-basis-map-RESULT.md`.

## Specific Exclusions
- Do NOT re-wire/modify the decoupled a_long path or any view/estimator (analysis only).
- Do NOT change production defaults, circuits.yaml, gold, or the store schema. No data/*.db writes.

## Constraints
- Every fracture carries a NUMBER (closed or bounded-defer). Undecided/unbounded = failure.
- a_long: do NOT re-introduce the documented HONEST-NULL. `constraint:physics_region_no_evo_import`. ASCII; `py`.

## Map Anchors (inbound)
- Structural: `struct:physics.layer2` — new `scripts/tier2_fracture_analysis.py`, `docs/physics/627-tier2-fractures.md`.
- Decision anchor: `decision:decoupled_1d_longitudinal` (governs a_long — defer, not re-merge).
- Evidence: each of 4 fractures carries a number.
- Map confidence flag: worktree editable-.pth trap; 0%-CPU headless-fit stall = #644 (cite if deferring a live run).

## Deliverable Path Check
- Committed — `scripts/tier2_fracture_analysis.py`, `docs/physics/627-tier2-fractures.md` (new, tracked).

## Required Evidence
- `py scripts/tier2_fracture_analysis.py` runs and prints all four fracture numbers (paste output; use a stored
  `C:/Programs/f1Brainz/data/physics_estimates.db` 2023 Q load; if a live fit is needed and stalls, cite #644 and
  use stored rows). The doc must contain each fracture NAME + its numeric bound.

## Verification Commands
```bash
cd /c/Programs/f1-627
py -c "import src.physics.layer2.estimate_store as m; print(m.__file__)"   # assert under C:\Programs\f1-627
py scripts/tier2_fracture_analysis.py
```

## Suggested Model Tier
stronger — the partial-correlation (physical vs measurement-error) separation and the shared-trajectory-noise
bound require careful statistical reasoning; the numbers must be defensible.

## Authority
Tier/scope frozen by the launch order. You decide the exact estimators for the bounds (document them). You must
NOT re-wire the a_long path or change any production default. dual-CdA is CLOSED by G3 — cite, don't rebuild.

## Worktree Isolation (CRITICAL)
cwd MUST be `C:/Programs/f1-627`. Assert `py -c "import src.physics.layer2.estimate_store as m; print(m.__file__)"`
prints under `C:\Programs\f1-627` before any real-data run. `physics_estimates.db` is at
`C:/Programs/f1Brainz/data/physics_estimates.db` (absolute path into main; your worktree lacks it). Do NOT commit data/*.db.

## Stop Conditions
Stop and return if: a fracture cannot be given a number by any bounded method (return it as a blocker with what
you tried — an unbounded fracture is a phase failure the Commander must know about); the a_long path would need
re-wiring; or a production default must change.

## Return Format
Write `IMPLEMENTER_RESULT` to `.agent-work/627-unified-basis/g5-implement/IMPLEMENTER_RESULT.md` AND deliver a
summary to ShipF-627 (route to team-lead if unaddressable) via SendMessage before ending your turn: the four
fracture numbers (closed/deferred each), files changed, the estimators used, evidence (script output), assumptions,
stop conditions, out-of-scope observations, workflow feedback.
