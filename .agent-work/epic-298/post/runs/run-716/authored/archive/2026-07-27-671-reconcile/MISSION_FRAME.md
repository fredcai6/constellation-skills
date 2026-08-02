# Mission Frame — #671 architecture reconcile + lineage dispositions

Map-first frame. Full evidence in `notes-671.md` (sections A–G); this is the planning distillation.

**Intent.** Fold the landed epic-#659 physics pipeline (waves #660–#669, the C→D→E→G→H→PANEL chain) into `docs/architecture/index.md` + `packets/physics.md` + overlays + decision anchors with REAL edges (not just nodes); give each of five prior lineages an explicit one-line disposition + pointer; graduate #696 into a docs/architecture anchor; disposition adjacent #587/#559/#577/#642/#654. Ends the "built-unjoined-forgotten-rediscovered" loop. **NO code deleted** — proposed removals return as a FOR-OWNER list only.

**Affected capabilities.** `purpose:physics_estimation` and its new children (`purpose:segment_map_derivation` #662, `capability:weekend-utilization-prior` #667, `capability:pilot-orchestration` #669). No evo/data-region capability touched.

**Structural anchors (current map).** Container `struct:physics`; components today = `struct:physics.layer2`, `.utilization`, `.wear`, `.ideal_lap`, `.weekend_state`, `.feature_view`. NEW to add: `struct:physics.segment_map` (+`.derivation`), `struct:physics.fingerprint` (+`join`), `struct:physics.instrument_panel`, `struct:physics.pilot`; grip-G module-leaves + reference-lap/observable leaves under existing components. `struct:physics.layer2.pooling` (#665) ALREADY present — must not duplicate.

**Governing constraints/assumptions.** `constraint:physics_region_no_evo_import` (every new node verified to honor it — no evo/latent_power/compound_prior import). DB-only analysis. `check_arch_map.py` must stay green but is BLIND to content drift → real code-vs-map read required (cartographer at reconcile). Overlays still use the deprecated `purpose:`/`serves` ontology (Open-Q line 974) — follow the in-file convention, do NOT migrate (lowest-dimensionality; migration is its own triage item).

**Decision anchors + pressure.** ~17 staged decision anchors across the 8 waves (notes §B). #696 graduation = new anchor. Disposition-recording convention: the EXISTING `## Open Structural Questions` table (Item | Current truth | Route) — #577 already lives there; use it as the single convention (no second convention invented). Naming-collision: #663 "module G"=grip=stage **D**; stage **G**=fingerprint #666 — keep distinct.

**Claims/evidence surfaces.** `claim:pilot-runs-end-to-end-3-circuits` (Monaco/Belgium/GB 2023-Q); grip node is an honest measured-NULL (g4 +155.5% RMS, g5 31.9% FAIL) — record as such, not as a gap. Live-path protection claim: `segment_classifier.classify_samples` imported at apex_extract.py:55/333, parameter_estimator.py:33/57, layer2/session_braking.py:178/192, physics/__init__.py:88 — re-confirm untouched (git diff shows zero src/ change).

**Map confidence/staleness.** Map reconciled only through #601; all 8 epic-659 stages are deferred-new-leaf awaiting THIS reconcile (per #669 delta). #664 flagged a stale "#664 = Build 3" comment in segment_map/{store,identity,derivation/derive}.py → triage (not a map edit).

**Out of scope.** Any code edit/deletion (propose-only); `src/physics/pilot/*` behavior + run artifacts (cmdr-670's territory — I document the pilot node from reads only, no code touch); overlay ontology migration; executing any removal; new F12.
