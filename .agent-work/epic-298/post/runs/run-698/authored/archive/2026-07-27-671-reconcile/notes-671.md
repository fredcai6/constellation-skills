# notes-671 — architecture reconcile + lineage dispositions (epic #659 Wave 5b)

Working notes. Fence: worktree-only; no main-checkout writes; sole writer to docs/architecture/*.

## Consolidated understanding (understand step) — verified against code, not just the order

### A. The landed pipeline C→D→E→G→H→PANEL (orchestrated by pilot #669) — ALL 6 stages MISSING from map
Verified: live predictor (`sampled_runtime.py`) imports no `src/physics/*` directly; physics pipeline is its own region.

| Letter | Stage | Wave | Module(s) | Map status |
|---|---|---|---|---|
| C | segment map | #661 runtime + #662 derivation | `src/physics/segment_map/` (+`derivation/`) | MISSING — new component node |
| D | grip-G baseline | #663 | `src/physics/layer2/grip_baseline.py, grip_store.py, grip_batch.py` | MISSING — module-leaf under `struct:physics.layer2`; REGENERATE (order) |
| E | reference laps + observables | #664 | `src/physics/utilization/reference_lap_product.py, reference_utilization_store.py, class_utilization_observable.py, class_ledger.py` | MISSING — module-leaves under `struct:physics.utilization` |
| G | driver fingerprint | #666 | `src/physics/fingerprint/` | MISSING — new component node |
| H | join (weekend utilization prior) | #667 | `src/physics/fingerprint/join.py` | MISSING — leaf under fingerprint |
| PANEL | instrument panel | #668 | `src/physics/instrument_panel/` | MISSING — new component node |
| — | pilot orchestrator | #669 | `src/physics/pilot/` | MISSING — new component node (thin consumer) |

Real edge chain (from pilot/pipeline.py + module-level imports):
`[#625 layer2 substrate: property_mixture]` → C(segment_map.derivation) --map_version--> E(reference_utilization_store); D(grip_batch→grip_store) --grip--> E; E(driver_class_observables) → G(fingerprint.fit→store); E(field-reference composition) + G(cells) → H(join.join_weekend_prior→WeekendUtilizationPrior); E-slice + fingerprint cells → PANEL(instrument_panel). pilot(#669) consumes all six read-only.

**#665 pooling: ALREADY on map (`struct:physics.layer2.pooling`), DO NOT duplicate.** No cartography delta staged for it; appears only as consumed dependency of G(#666 fit) and PANEL(#668).

**Naming-collision guard:** #663 grip files call THEMSELVES "module G" (G=grip), but in the pipeline chain grip = **D** and letter **G** = driver **fingerprint** (#666). pilot keys the grip slot `grip_g` distinct from `fingerprint`. Do not conflate.

### B. Staged cartography deltas to fold (8 waves; on MAIN checkout, reference-only)
Decision anchors staged across waves:
- #661: segment_map `constrained-by constraint:physics_region_no_evo_import` edge.
- #662: `purpose:segment_map_derivation` (NEW); `decision:reference-lap-pooled-not-per-lap`, `decision:corner-gate-is-curvature`.
- #663: `decision:grip_estimate_record_session_level_pk` (decisions/grip-estimate-record-session-level-pk.md); `explained-by` edge on layer2. Built but GATING-measured NULL (g4 +155.5% RMS, g5 31.9% FAIL) — honest measured-null.
- #664: `decision:class-attribution-membership-faithful`, `decision:field-reference-fingerprint`, `decision:g-one-sided-directed-uncertainty`; claims attribution-robust / deficits-sum-to-lap. RETIRES #625 regime_rollup DISTANCE-share caveat.
- #666: candidate `decision:fingerprint-era-key`; reuses #627/#628 anchors.
- #667: `decision:join-consumer-boundary`, `decision:join-is-normalized-weighted-average`; capability `weekend-utilization-prior`.
- #668: `decision:golf-correction-is-double-centering`, `decision:split-half-unit-cross-circuit-2v2`, `decision:replication-frozen-set-signed`; `claim:instrument_panel_reads_cells_directly`; `decision:replication-deferred` RESOLVED.
- #669: `capability:pilot-orchestration`; `decision:pilot-fresh-vs-archived`, `decision:two-segmap-paths`, `decision:pass-vs-limitation-boundary`; `claim:pilot-runs-end-to-end-3-circuits` (Monaco/Belgium/GB 2023-Q).

Note: overlays currently use the DEPRECATED `purpose:`/`serves` ontology (per Open-Q line 974). I will follow the EXISTING convention in-file (match what's there), not migrate — migration is its own tracked triage item. Keep lowest-dimensionality.

### C. Five lineage dispositions (verified importer topology)
1. **circuit rollup #625** (regime_rollup.py / property_mixture.py): `regime_rollup` = **validated but UNWIRED** (zero production importers; only scripts/build_regime_rollup.py + scripts/validate_segment_map_662.py + test). `property_mixture` = **LIVE** via segment_map derivation chain (from_mixture, corner_attributes) + segment_classifier — STAYS. #664's TIME-share composition supersedes regime_rollup's DISTANCE-share. → Disposition: property_mixture WIRED (live); regime_rollup SUPERSEDED-and-removal-PROPOSED (→ FOR-OWNER list).
2. **#628 utilization** (driver_utility_observable.py / car_prior.py): driver_utility_observable = **code-complete, never run at season scale** (only batch script). car_prior = wired within utilization/ideal_lap cluster but cluster is script-driven only. → Disposition: KEPT-WITH-REASON (validated, awaiting season-scale consumer per #642/#696 Build 2). Not removable (car_prior has live-region importers).
3. **ephemeris per-corner pilot** (src/physics/ideal_lap/): ephemeris core (residuals.build_ephemeris / ephemeris_store.py / generator / wear_derate) NOT wired live (tests only). ONE live tendril: `pvat_writer` consumed by layer2/session_race.py (unrelated to ephemeris). generator imports car_prior (ties clusters). → Disposition: KEPT-WITH-REASON — pvat_writer LIVE (must stay); ephemeris core unwired-but-entangled (validated exploration; not a clean removal — needs per-consumer care). NB distinct from #669 `src/physics/pilot/`.
4. **apex_obs full-coverage raw material** (apex_extract.py::extract_apex_observations + apex_obs col of session_fits): extractor IS LIVE (session_fit + fp_gate_real_extractor). Persisted `apex_obs` column WRITTEN on every prod fit but its sole reader `fit_store.load_apex_weekend` has **zero production callers** (test only). → Disposition: KEPT-WITH-REASON — deliberate full-coverage raw material preserved for a future consumer; extractor live, column intentionally-written-unread.
5. **segment_classifier.py**: `classify_samples` (tiling) = **LIVE PRODUCTION** — CONFIRMED imported/called by apex_extract.py:55/333, parameter_estimator.py:33/57, layer2/session_braking.py:178/192, physics/__init__.py:88. MUST NOT touch. `soft_class_membership` bridge = **ZERO non-test callers** (only its own def + docstring-mentions in corner_attributes.py + 3 assertions in test_segment_classifier.py; self-docstring: "NOT wired into classify_samples's main loop"). → Disposition: classify_samples WIRED (protected, explicitly untouched); soft_class_membership bridge SUPERSEDED/unwired-removal-PROPOSED (→ FOR-OWNER list; method only).

### D. Adjacent dispositions #587/#559/#577/#642/#654 (consistent convention = existing Open Structural Questions table; #577 already lives there)
- **#587** — retire/demote old `fit_store` per-driver engine (two coexisting physics-fit engines). Adjacent machinery. → record: dual-engine coexistence, tracked by #587, per-consumer migration needed (generator power-curve has no EstimateStore replacement). Route: Triage (#587).
- **#559** — rebuild per-session fit store on post-#495 code (data/physics_fits.db is pre-fix baseline). → record: store artifact stale vs current code, regenerable/untracked, tracked by #559. Route: Triage (#559).
- **#577** — re-batch physics estimates against wired burn rate. ALREADY at Open-Q line 981; refine to name #577. Route: Triage (#577).
- **#642** — reserved/deferred structure: corner-class count domain-capped at 4; revisit once driver-utility/affinity consumer can define the selection criterion. → record: corner-class cap = deliberate deferred judgment, tracked by #642. Route: Triage (#642).
- **#654** — reserved/deferred structure: `CarBasisPosteriorRecord.process_noise_link`/`parc_ferme_step` reserved slots (already noted in #629 reconcile prose). → record: reserved slots + honest-sigma-widening is the architecture, real fit tracked by #654. Route: Triage (#654).

### E. #696 graduation
#696 = "Roadmap: Builds 2-3 + carried threads (post-#659 forward map — anti-orphan)". OPEN, stays open as tracker. Graduate into a **docs/architecture/decisions/ anchor** (its structural home) — the anti-orphan point. Build 2 = race reference (soft push/managed, traffic/tyre controls, P6 variant queue). Build 3 = live loop (two-speed practice update, seed-then-supersede live maps [#661/#662 interface], physics feature-family→fusion choir [#629/#630 seam]). Allocation-not-gating rule: each Build cut only after Build 1 instrument-panel §7 reports signal sizes.

### F. Triage candidates found
- #664 stale forward-reference: `segment_map/store.py`, `identity.py`, `derivation/derive.py` still label the seeded/supersede path "#664 = Build 3" (wrong issue number; that path stays NotImplementedError, correctly out of #664 scope). Route: Triage (comment repoint).
- N4 (from cold critic): `docs/architecture/overlays/purposes.yml` uses the DEPRECATED `purpose:`/`serves` ontology (already Open-Q line 974); each new epic-659 `purpose:`/`capability:` entry this reconcile adds grows the eventual migration. Route: Triage (overlay ontology migration — folds into the existing line-974 item).
- #577 correction (cold critic S6): index.md line 981 is the **#575** burn-rate row; #577 is the tracking issue for that re-batch. Add the #577 pointer to that row, do NOT relabel #575.

## G. FOR-OWNER — proposed-removals LIST (PROPOSE ONLY — do NOT execute; Admiral parks)
1. **`src/physics/layer2/regime_rollup.py`** (+ `scripts/build_regime_rollup.py`, `tests/unit/physics/layer2/test_regime_rollup.py`; repoint the `circuit_distance_share`/`load_circuit_frame` import in `scripts/validate_segment_map_662.py`). WHY: validated but UNWIRED (zero production importers); #664's field-reference TIME-share composition supersedes its DISTANCE-share rollup and #664 explicitly retired its caveat. CONFIRMS-SAFE: reverse-import scan (only 2 scripts + 1 test import it); property_mixture — its one live dependency — is NOT removed (stays live via segment_map). NB: validate_segment_map_662.py would need its import repointed or that validation retired.
2. **`SegmentClassifier.soft_class_membership`** method only (`src/physics/segment_classifier.py:93`) + its 3 assertions in `tests/unit/physics/test_segment_classifier.py`. WHY: bridge with ZERO non-test callers; its own docstring says "NOT wired into classify_samples's main loop." CONFIRMS-SAFE: reverse-import scan — only def + prose mentions in corner_attributes.py (comments, not calls) + 3 test assertions. **`classify_samples` (the live tiling) is a DIFFERENT method and MUST STAY** — protected, explicitly untouched.
3. (LOWER-CONFIDENCE, entangled — recommend investigate-not-delete) unwired ephemeris core in `src/physics/ideal_lap/` (`ephemeris_store.py`, `residuals.build_ephemeris`). WHY: no production consumer (tests only). NOT-CLEAN: `pvat_writer` in the same package IS live (session_race.py), and `generator.py` imports `car_prior` — the cluster is tangled, so this needs per-consumer care, not a blanket delete. Dispositioned kept-with-reason above; listed here only so it is not forgotten.

## H. Triage recommendations (recommend-and-defer — NOT filed; no filing authority granted, owner AFK)
1. **#664 stale forward-reference comment** (cleanup). `src/physics/segment_map/store.py`, `identity.py`, `derivation/derive.py` label the seeded/supersede (`NotImplementedError`) path "#664 = Build 3" — wrong issue number (that path is correctly out of #664 scope; it belongs to Build 3 / #696). Acceptance: repoint the three comments to the Build-3 lifecycle (#696) issue number. Out of scope: any behavior change (the path stays `NotImplementedError`). Disposition: **recommend-and-defer** — fix-now DISQUALIFIED (touches `src/`, which the #671 launch order fences to doc-only; deletion guard). Already recorded in the `segment_map` packet section ("Known stale-comment → Triage"). Deferral reason: filing authority not granted by the launch order; owner AFK; float to Admiral if a real issue is wanted.
2. **N4 purposes.yml deprecated-ontology migration** — ALREADY-CAPTURED, no new recommendation. The 3 new epic-659 `purpose:` entries were added under the deprecated `purpose:`/`serves` ontology (in-file convention, lowest-dimensionality); this grows the existing migration surface already tracked by the Open-Structural-Questions "`purposes.yml` old ontology" row, which I extended to name the 3 new entries. Disposition: folded into the existing item (no separate issue).

## Plan shape (reasoning gates — doc/map only; one cartographer for reconcile-verify)
- G1: Fold the 8-wave pipeline into index.md + packets/physics.md + overlays + decisions anchors (real edges C→D→E→G→H→PANEL; regenerate #663; don't duplicate #665).
- G2: Five lineage dispositions + adjacent #587/#559/#577/#642/#654 into the Open Structural Questions table (single consistent convention).
- G3: Graduate #696 into a docs/architecture/decisions anchor.
- G4: check_arch_map.py green + cartographer independent verify (content drift, not just green check).
- FOR-OWNER removal list + triage (#664 stale ref) carried to reconcile/triage/review; NO code deleted.
</content>
