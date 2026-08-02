# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g5 (Tier-2 fracture quantification)`

## Result
`APPROVE`

## Handoff compliance
All four x7-basis fractures carry a NUMBER, satisfying the close criteria (close-with-number OR
bounded-defer-with-quantified-bound):

1. **DUAL-CdA — CLOSED.** Mercedes fused CdA sigma = 0.0460 m² vs PowerDrag's own 0.0562 m² —
   18.1% tighter. RBR z=6.80 correctly REFUSED (genuine disagreement, not silently blended).
   Independently re-ran the script: the real `src.physics.layer2.cross_view.fuse_dual_cda` is
   called live over G3's captured Monza inputs and reproduces G3's cited z=6.80/2.03 and fused
   sigma ≈0.046 exactly (the script's own inline `assert`s also confirm this, and they pass
   silently). `cross_view.py` is read-only-imported, not modified.
2. **GRIP-TRIPLET — BOUNDED-DEFER ≤0.6%.** The method genuinely controls for circuit: each grip
   axis is demeaned within its `gp_name` group (a circuit-fixed-effect residualization) BEFORE
   computing the Pearson correlation — this is a real partial/circuit-controlled correlation, not
   a raw Pearson dressed up as one. Both raw (up to |r|=0.238) and circuit-controlled (max
   |r|=0.107) values are shown side by side so the distinction is auditable. The 0.6% bound
   follows correctly from `Var(A|B) = Var(A)(1-r²)` applied to the strongest controlled pair
   (verified the arithmetic: 1 − sqrt(1 − 0.107²) ≈ 0.57% ≈ 0.6%).
3. **a_long — BOUNDED-DEFER ≤13.4σ, structural, NOT re-merged.** All 18 transcribed per-view
   |shift| numbers were checked one-by-one against
   `docs/architecture/decisions/decoupled-1d-longitudinal.md`'s Config-C tables (#523/#546
   sections) and match exactly, including the max (PowerDragView P_max, Monaco, 13.4σ) and min
   (TractionView b_t, Belgium, 0.15σ). `decision:decoupled_1d_longitudinal` is a real, existing
   map anchor. `git status --porcelain src/` is empty — the decoupled/estimator path was not
   touched, confirming "do NOT re-merge" was honored in fact, not just in prose.
4. **SHARED-TRAJECTORY-NOISE — BOUNDED-DEFER ≤0.0%, honest method-scoped null.** States plainly
   what was tested (a between-session own-fit-sigma correlation proxy, circuit-controlled,
   floored at 0 because a negative empirical correlation isn't evidence of shared noise) and what
   was NOT tested (a direct live-perturbation re-fit of the shared smoother — structurally
   incapable of detecting within-session, non-overlapping-sample-set correlation). Cites #644 for
   the live-refit follow-on, matching the handoff's own citation guidance.

`py scripts/tier2_fracture_analysis.py` independently re-run twice: default DB path (exit 0, all
4 numbers print, output byte-for-byte matches the doc's pasted evidence) and a nonexistent
`--db-path` (exit 0, fractures 2/4 print an explicit DB-not-found BOUNDED-DEFER skip line instead
of crashing — the DB-guard claim is independently confirmed, not merely asserted).

## Scope drift
None. `git status --porcelain` shows only `scripts/tier2_fracture_analysis.py`,
`docs/physics/627-tier2-fractures.md`, and `.agent-work/627-unified-basis/` (engine-owned plan
state) — matches the Allowed Scope exactly. `git status --porcelain src/` and
`git status --porcelain data/` are both empty: no view/estimator/a_long re-wiring, no
production-default/store-schema change, no `data/*.db` writes. `cross_view.py` and
`estimate_store.py` are imported (deferred, inside functions) but not edited.

## Evidence verdict
Required evidence is present and reproducible, not merely reported. The implementer's pasted
"Full script output" section in the doc matches my own independent re-run character-for-character.
`verify_simplification_limits --paths scripts/tier2_fracture_analysis.py` → PASS. Script is
ASCII-only (independently verified via `.decode('ascii')`, not just trusting the file's own
header comment).

## Code/doc quality
Constraint checks: every fracture carries a number (yes); a_long not re-merged (yes, `src/`
untouched); `constraint:physics_region_no_evo_import` (yes — module-level imports are stdlib only;
the two physics-layer2 imports are function-local and are physics-region, not evo-region). Doc
citations (G3's `monza_final_table.json`, `decoupled-1d-longitudinal.md` #523/#546,
`x7-basis-map-RESULT.md`, #644) all resolve to real files/anchors.

**Fowler refactoring pass** (`.agent-work/627-unified-basis/g5-review/fowler_pass.json`,
`scripts/verify_fowler_pass.py` exit 0): all 12 baseline smells visited.
- `duplicated-code` **flagged** (non-blocking observation): `fracture_2_grip_triplet` and
  `fracture_4_shared_trajectory_noise` each repeat a near-verbatim
  `if not os.path.exists(db_path): print(...); return None` DB-guard block. A shared
  `_guard_db()` helper would remove it; minor given only 2 call sites in a one-shot analysis
  script.
- `comments-as-deodorant` **overridden**: the script/doc's dense provenance comments trace every
  number back to its source run — CREW_CONTEXT's data-semantics traceability requirement, not
  compensation for unclear naming (function/variable names are already self-explanatory).
- Remaining 10 smells: absent.

## Map impact verdict
- **Evidence supports claimed change:** yes — independently reproduced above.
- **Constraints not violated:** yes — `constraint:physics_region_no_evo_import` honored;
  `decision:decoupled_1d_longitudinal` not re-opened.
- **Notes match the diff:** yes — `struct:physics.layer2` gains one read-only-consumer script +
  one doc, correctly characterized as a minor addition, not a structural change.
- **Decision candidates surfaced:** n/a — no new decision authority was required; the implementer
  correctly did NOT propose re-opening the a_long decision.
- **Durable context routed:** yes — the pre-flagged tc8 (main store's `cross_view_covariance`
  unpopulated) is routed to Triage as engine candidate `tc1` in this survey, not silently dropped.

## Reconciliation check
No unreconciled architecture divergence. Confirmed `decision:decoupled_1d_longitudinal` and
`struct:physics.layer2` are real, existing map anchors (not invented). No new anchors were needed
for this analysis-only gate.

## Blockers
- none

## Out-of-scope observations
- (engine candidate tc1) Main repo's `data/physics_estimates.db` has `cross_view_covariance` ==
  `None` on every row (store snapshot predates a run that persisted G3's fused values; CoastView's
  CdA is production-pinned so `fused_cda` stays inert on the live pathway). A future gate querying
  fused-CdA directly from the store needs a fresh `record_from_estimate` run with an
  independently-fit Coast. Pre-flagged in the handoff as a known non-blocker (tc8); confirmed here,
  not fixed (out of g5's scope).
- Fowler `duplicated-code` (see above): minor, non-blocking — a candidate for whoever next touches
  this script, not worth a follow-up issue on its own.

## Workflow Feedback
- **Handoff gaps:** none material. The four close-criteria subsections mapped cleanly onto
  independently-verifiable checks (re-run the script, diff the transcribed a_long table against
  its source doc, check the partial-correlation method).
- **Context rediscovered:** none beyond what the implementer's own IMPLEMENTER_RESULT.md already
  flagged (the main store's unpopulated `cross_view_covariance` column) — that write-up was
  accurate and saved me a dead-end query.
- **Instructions improvised around:** none — the skill's survey template, engine verbs, and the
  Fowler-pass rail all applied directly to an analysis-script gate with no friction.
- **What would have made this easier:** none — this gate was unusually well-suited to independent
  verification (a pure, deterministic, DB-guarded script with byte-reproducible output plus a
  citable decision doc to cross-check transcribed numbers against).

## Return status
`complete`
