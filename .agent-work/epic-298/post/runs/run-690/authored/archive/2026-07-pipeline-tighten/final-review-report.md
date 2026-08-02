# Final whole-branch review — pipeline tightening (telemetry → ephemeris)

Reviewer: Senior Code Reviewer (final gate). Range: `3741f756..HEAD(feat/pipeline-tighten)`.
Materials: full `final-review-src.diff` read end-to-end (8,660 lines); plan v2.1; original
2026-07-06 data-pathway review; epic ledger; D9 spur verdicts + 17 follow-on drafts;
targeted read-only spot-checks in the main checkout (physics_data_models, frontier_fit tail,
race_stint_store, dynamics.py, packets/preprocessing.md, _telemetry_store.py, schema.sql,
populate CLI args).

---

## Strengths

- **Byte-identity discipline held everywhere it was promised.** Every opt-in seam
  (`return_sigma`, `sigma=None`, `pvat_db=None`, `hp_store=None`, `terrain=None`,
  `return_cov=False`, `view_pins=None`) defaults to the exact legacy path, including the
  subtle traps the plan called out (the `rng.integers` vs `rng.choice` bootstrap branch;
  the +0.0 WLS weight identity in tyre_separation; y-sort permutation of kernel weights).
  The only default flips are the two ratified ones (D1 ceiling source, D7 pins/k-prior).
- **The T5→T6 seam is internally consistent** (the brief's #1 concern): BrakingView passes
  its per-sample `sigma` into BOTH the main `fit_frontier` call and the ±h
  `cda_frontier_jacobian` refits; TractionView is unweighted in both. The `drag_sign`
  convention was verified against each view's observable definition (braking `y = −a_long
  − drag − …` → −1; traction drag added → +1) and is correct. The `n_boot=0` Jacobian
  refit path is safe (`_bootstrap_cov` returns zeros below 5 draws, frontier_fit.py:277-279).
- **T9's covariance blob is PSD by construction, not by repair**: the joint-correlation
  clamp (review fix d24b9a43) makes `_psd_repair` a genuine last-resort guard, and the
  code says so explicitly — the stored diagonal can never silently drift off `mass_se²`.
- **session_race composed cleanly across parallel tracks** (brief #5): T10's
  `pvat_db`/key threading and T14's `hp_store`/`session_key` seam touch different
  functions, no shadowed or duplicated params, both default-off. T4's `burn_rate_source`
  is exactly the promised one-field-one-line change.
- **The create-on-connect footgun got real, repeated attention** — compare-script guards
  (T2 CRITICAL fix), generator's estimate-path existence check, `build_ephemeris`'s
  latest_run bypass (fixwave), export_wear_run's ro-URI raw reads. (Two new unguarded
  sites did slip in — see Important #3.)
- **backfill_estimate_store.py fixes the retired script's destroy-good-rows bug
  structurally** (ok-path upsert+log outside any error-record try), not just cosmetically.
- **Honest-absence discipline throughout**: NULL-not-clamp below the PVAT speed floor,
  None-not-fabricated sigmas, `sigma_source="unavailable"` labeling in the compare script.

## Cross-task seam checks (the brief's list)

1. **T5×T6 signature drift** — consistent per view (see Strengths). No issue.
2. **T1 ceiling × T9 grid × T11 terrain** — `ideal_lap` and `ideal_lap_sigma_grid` share
   `_resolve_ceiling` verbatim, and `residuals` threads identical
   `cached_fit_row/ribbon/terrain/ceiling_source/estimate_db_path/config/wear_model` into
   both, with the grid's `session_type="Q"` matching the per-lap ideal. Grid and nominal
   cannot structurally diverge; the only theoretical divergence is an intermittent store
   read failure between two independent loads (negligible; see Minor #5 for the
   efficiency side of those repeated loads).
3. **T7 (κ,σ) contract** — every call site is on the right side of the union:
   generator's `_apply_state_derates` and residuals' capability call opt in
   (tuple-of-tuples, `cast`-narrowed); residuals' realized call and all legacy callers
   stay on the float-pair default. The fixwave snapshot fallthrough pins
   `latest_snapshot_run_id()` from the same `DEFAULT_SNAPSHOT_DIR` that `load_model`'s
   fallback resolves — consistent.
4. **T3/T4 provenance round-trip** — all four new StintEstimate fields
   (`k_prior_source`, `quali_pin_used`, `mass_kg_mean`, `mass_kg_start`) are set by BOTH
   factories and mapped by `record_from_stint_estimate`; `burn_rate_source` flows
   RaceStintData → batch → record; `error_record` nulls all five; migration script adds
   exactly the five columns. Complete. (One semantic nit → Minor #6.)
5. **T10×T14 in session_race** — compose cleanly (see Strengths). Note T14's seam is
   deliberately unreachable from the public API (`load_race_stints` has no `hp_store`
   param) — that is the scoped "seams-only" outcome, production wiring is follow-on 06.
6. **Global constraints** — no evo-region imports added anywhere in
   src/physics|preprocessing (all new imports checked); unit conversions only at the
   sanctioned seams (compare script uses ×g mech / ×g÷ρ aero exactly per car_prior's
   Jacobian); every store change is additive (self-heal ALTERs or PRAGMA-guarded
   migration scripts); `hp_store.py` writing its own new DB is plan-sanctioned and
   packets/preprocessing.md:155-205 documents it. No task writes `data/*` (the two new
   unguarded EstimateStore constructions CAN — Important #3).
7. **Minor-list triage** — see section below.

---

## Issues

#### Critical (Must Fix)

None found. No data-corrupting, default-path-breaking, or contract-violating defect
survives in the merged branch.

#### Important (Should Fix)

1. **`SMOOTHER_VERSION` mislabels the production smoother as Matérn-5/2 — contradicting
   this same branch's Task 13.**
   `src/preprocessing/trajectory/__init__.py:37` — `"matern52+chi2target_hp_v1"`, with a
   docstring claiming "the SDE prior order (Matern-5/2)". Production is order=4 =
   Matérn-7/2 at every live call site (`session_fit.py` order=4, `session_race.py`
   order=4; `dynamics.py:96` confirms order=4 → Matérn-7/2), which is precisely the
   stale-doc error Task 13 fixed in `physics_adapter.py:7` and the arch index *in this
   very branch*. This constant exists solely for honest provenance and is pinned into
   `eph_runs.source_versions_json` on every build — the mandatory Wave-6 ephemeris
   rebuild will bake the wrong label in. Fix (one line + docstring): e.g.
   `"matern72_o4+chi2target_hp_v1"`. Fix BEFORE the Wave-6 ephemeris rebuild; it is free
   now and costs a rebuild (or a permanently wrong pin) later.

2. **PVAT persistence is not idempotent — re-running the export duplicates every row.**
   `processed_telemetry` has no natural-key uniqueness (schema.sql:132-133, autoincrement
   id; indexes only), `write_lap_pvat` (pvat_writer.py:213) does plain
   `insert_processed_telemetry`, and `scripts/export_pvat.py` never calls the
   already-existing `delete_processed_telemetry(session_id, driver_id)`
   (_telemetry_store.py:151). A re-run or resumed run of the Wave-6 PVAT export (at
   minimum 2022-2026 race sessions) silently doubles the trajectory channel with no
   error and no way to distinguish vintages. Fix: in export_pvat, delete per
   (session_id, driver) before `load_race_stints(..., pvat_db=db)`; or delete-before-
   insert per (session, driver, lap) inside `write_lap_pvat`. Land before the Wave-6
   PVAT export.

3. **The create-on-connect footgun was re-introduced at two NEW call sites in this epic**
   — after T2's review classified the identical pattern CRITICAL and T1 guarded against
   it. `race_priors.py:148` (`quali_pins`) and `race_stint_batch.py:364` (per-gp quali
   load) construct `EstimateStore(estimates_db_path)` with no existence check:
   `EstimateStore.__init__` runs schema writes, so a mistyped `--estimates-db` (a) creates
   a stub DB at the typo path and (b) silently disables quali pins for the entire run
   (empty frame → `RaceViewPins(None, None)`; only forensically visible via
   `quali_pin_used=0`). Contrast `generator._ceiling_from_estimate` (generator.py:~408),
   which guards with `Path.exists()` before touching the store. Fix: same two-line guard
   + a loud warning at both sites. The systemic fix stays follow-on 07, but these two
   instances were ADDED by this epic and are two lines each.

4. **The mandated Wave-6 "populate_race_stint_estimates full rerun" cannot actually
   repopulate an existing store.** The batch resume-skips every existing
   (year,gp,driver,stint,compound) row via `store.has(...)`
   (race_stint_batch.py:~273) and the CLI has no `--refit`/`--force`
   (verified: scripts/populate_race_stint_estimates.py arg list). Pointed at the current
   `race_stint_estimates.db`, the "full rerun" will report n_skip for everything — pins
   never applied, the five provenance columns stay NULL — and look successful.
   Additionally `RaceStintStore._init_schema` is CREATE-only (race_stint_store.py:340, no
   column self-heal), so any in-place write against an unmigrated old DB fails per-stint
   unless `scripts/migrate_race_stint_store_seam.py` runs first. Fix: either add
   `--refit` to the CLI, or amend the Wave-6 checklist to a fresh `--out` store rebuilt
   year-ascending (which also makes the year−1 k-prior pooling work) — and note the
   migration-first requirement for any in-place path.

#### Minor (Nice to Have)

5. **Per-lap ceiling re-resolution in the ephemeris batch (T1×T9 composition).** Every
   `ideal_lap` call in `residuals._build_gp_rows`' per-lap loop re-opens the estimate
   store and re-runs `build_car_ceiling` pooling (generator.py:404-430), even though the
   module's own docstring exists to cache exactly this class of per-driver-constant work
   (ribbon/power-curve). Post-backfill this is O(laps) store loads + poolings per gp —
   real but small next to the MC grid cost. Cheap fix: load `estimate_df` once per gp
   and thread it through the existing injection seam.
6. **`quali_pin_used` records "pins were offered," not "a pinned fit succeeded"** —
   it is True even when both pinned views subsequently returned None
   (stint_estimator.py:~1035). Docstring reads slightly stronger than what's stored.
7. **`scripts/migrate_estimate_store_metadata.py` default DB list still targets the
   retired `physics_estimates_g3wired.db`** — harmless ("NOT FOUND — skipped") but the
   name was D9-retired; fold into follow-on 04's g3wired cleanup.
8. **`generator._ceiling_from_estimate` reads `row["constructor"]` outside its try**
   (generator.py:404) — a hand-built fit_row without the field raises KeyError past the
   fallback (ledger T1 m1). Real FitStore rows always carry it; residuals' per-lap try
   contains the blast radius.
9. **Compare-script sigma aggregation under mixed missingness**
   (compare_capability_stores.py:~505): `fit_sigma = sqrt(Σσ²_available)/n_values`
   understates σ when some driver rows lack covariance blobs. Edge case, diagnostic-only
   script.

---

## Minor-list triage (accumulated ledger minors)

| # | Minor (ledger) | Triage |
|---|---|---|
| T1 m1 | constructor KeyError outside try (generator.py:404) | FILE (or fold into the two-line fix batch; see Minor #8) |
| T1 m2 | last-write-wins `ceiling_sources` across gps | FILE — now explicitly documented at the aggregation site; a per-gp map is a schema question, not a bug fix |
| T5 m1 | exact `ptp>0` uniform-σ detection, no tolerance | FILE — near-constant σ yields near-uniform weights; behavior continuous |
| T5 m2 | weighted bootstrap double-applies precision (p~w AND w in ridge) | FILE — plan-mandated per brief; T6 was informed; document in frontier_fit if revisited |
| T5 m3 | tight per-seed test tolerances (1e-6/1e-9) could tip on BLAS change | FILE — env-sensitivity, same class as the pre-existing evo decomp pin (follow-on 15) |
| T3 | per-call constructor-map rebuild; duplicated fixtures; inequality-only pin assertions | FILE — per-driver map rebuild is O(rows·drivers) per gp, small |
| T6 | unguarded NaN in ±h refit Jacobian | FILE — NaN coefs would need a degenerate refit the healthy-fit path doesn't produce; would surface loudly as NaN cov |
| T6 | migration ALTER untyped vs script typed | FILE — cosmetic, SQLite types advisory |
| T8 | spread test std>0.1 only; nominal-unchanged trivially true | FILE — test-strength only |
| T10 | export_pvat imports private `_get_session_id` | FILE |
| T10 | no unmocked full-4-hop integration test | Already filed (follow-on 14) |
| T9 | age grid clamps at 25 (long stints understate σ) | FILE — conservative direction is understatement; revisit when σ consumers appear |
| T9 | standalone grid resolves wear at age 0; 294-vs-288 naming | FILE — irrelevant on the residuals path (explicit wear_model passed); cosmetic |
| T14 | code_version doesn't invalidate; NaN restore hardcoded chi2_pos; git shell-out per put | Already filed (follow-on 06 owns invalidation semantics for production wiring) |
| T15 | hand-typed "2023-24 Q"; base blocks not degradation-wrapped; s4 phrasing | FILE — docs-only; next explainer regen (Wave-6 mandates one) is the natural vehicle |

**None of the accumulated minors escalates to must-fix in whole-branch context.** The
four Important findings above are new, whole-branch-scoped findings (three are
composition/operational gaps between tasks; #1 is a cross-task contradiction no
task-scoped review could see because T13 and T9 lived on different tracks).

## Recommendations

1. Fix Important #1 (one-line `SMOOTHER_VERSION` + docstring) on the branch now, before
   merge — it contradicts the branch's own T13 and the epic's provenance-honesty
   contract, and the Wave-6 rebuild freezes it.
2. Land #2 and #3 as a small pre-repopulation fix commit (≈10 lines total, all guarded
   paths, no default-path risk) — both gate the very Wave-6 checklist steps that are
   about to run. #4 can be a checklist amendment instead of code if preferred
   (fresh-store rebuild, year-ascending), but write it down.
3. When filing follow-on 04, add the `migrate_estimate_store_metadata.py` default-list
   straggler (Minor #7).
4. The Wave-6 runbook should state explicitly: race-stint in-place writes require
   `migrate_race_stint_store_seam.py` first (no self-heal on that store).

## Assessment

**Ready to merge?** With fixes

**Reasoning:** The branch delivers the stated contract — the seams carry σ, the
pass-1→pass-2 transition is baked and provenance-tracked, the ephemeris carries honest σ
+ a per-lap covariance, and D9's single-pathway sweep is real — with no Critical defects
and consistently strong byte-identity discipline. Four Important items (one provenance
mislabel contradicting the branch's own doc fix, two small operational gaps that would
silently corrupt or no-op the imminent Wave-6 repopulation steps, and one re-introduced
footgun) are each a few lines and should land before merge/repopulation; nothing
requires re-architecture or re-review.


---

# Round 2 — fix-round verification (4451c80d..367f4f26, branch track/finalfix)

Verified the consolidated fix commit `367f4f26` against the four Important findings.
Full delta read (1,054-line review package); consumer greps re-run against the checkout.

**Fix 1 (SMOOTHER_VERSION) — VERIFIED.** Constant is now `"matern72_o4+chi2target_hp_v1"`
with a truthful docstring (Matérn-7/2, order=4, matching every live call site). Consumer
sweep: the only literal occurrence of the old string in the entire repo is the definition
line itself; both consumers (`residuals._smoother_version`, `test_residuals_sigma.py:541`)
import the constant dynamically, `packets/physics.md:1452` references it by name not
value, and the committed `docs/pipeline/bundle.json` does not embed it. Rename is safe
with zero stale pins. Cosmetic nit (non-gating): the docstring says
"``matern52_sde``/``_m52`` … parameterized by ``order``" — those two symbols are the
fixed 5/2 closed forms; the order-parameterized builder is `matern_sde`. Loose wording
only; the load-bearing claims are correct.

**Fix 2 (PVAT idempotency) — VERIFIED.** `ensure_clean_pvat(db, year, gp, session_type,
driver)` resolves the session exactly as `write_lap_pvat` does and delegates to the
existing `delete_processed_telemetry(session_id, driver_id)` — scope is precisely
(year, gp, session_type, driver). The wiring point is `load_race_stints`, which IS the
single choke point: the `pvat_db` hook only exists on the
load_race_stints → _prepare_fitted_laps → _fit_driver_laps → _fit_clean_lap_row chain,
and `scripts/export_pvat.py` enters through `load_race_stints(..., pvat_db=db)` per
driver — both paths traced, both covered by one call. Cleanup fires once per driver
BEFORE any of that driver's lap writes in the same call (no self-clobbering), and only
when `pvat_db is not None`. Tests: the double-write test asserts count-equal (2, not 4)
after write→clean→rewrite; driver-scoping and missing-session no-op covered;
`TestPvatDbHook` proves the cleanup is called with the right args when the hook is on
and never called when it's None. Noted, non-gating: delete-before-rewrite means a re-run
whose fits then fail leaves that driver rowless (stale vintage removed) — standard and
arguably correct semantics.

**Fix 3 (create-on-connect guards) — VERIFIED.** Both new sites guard with
`Path.exists()` BEFORE constructing `EstimateStore` (no file can be created), warn in
each context's established convention (plain stderr WARNING in `quali_pins`;
verbose-gated `[HH:MM:SS] {gp}: WARNING:` in the batch, matching the adjacent
load-failure warning), and degrade to exactly the cold path
(`RaceViewPins(None, None)`, same as `--no-quali-pins`). Both tests assert cold pins +
warning content ("disabled") + `os.path.exists` false on the typo'd path.

**Fix 4 (--refit + schema guard) — VERIFIED.** The skip is now
`if not refit and store.has(...)` — bypassed only when `refit=True`; the default-skip
regression test (estimate_stint never called, n_skip=1) and the refit-overwrite test
(called once, n_ok=1, n_skip=0) cover both directions. `_check_seam_columns` runs at
`populate_race_stints` startup, PRAGMA-checks the existing table against ALL current
`RaceStintRecord` fields, and raises `RuntimeError` naming
`scripts/migrate_race_stint_store_seam.py` and the db path; test asserts the script name
appears, and the fresh-store test guards against false positives. The CLI catches the
RuntimeError into a clean `ERROR:` + exit 1. This hard guard supersedes round-1
recommendation 4 (the runbook note). Noted, non-gating: the message names the T4
migration script even for a hypothetical pre-T4-vintage store missing older columns that
script doesn't add — no such vintage is known to exist.

**Scope check:** production changes confined to the four fix areas; no `data/*` writes;
no default-path behavior changes outside the guards (all regression-tested). Fix report
claims 132 targeted + 829 package tests green; per the review mandate I did not run
tests — the separately-running full suite remains the parallel merge gate.

## Round-2 Assessment

**Ready to merge?** Yes

**Reasoning:** All four Important fixes are correctly implemented, minimally scoped, and
test-covered exactly as specified; the two residual nits are cosmetic wording only.
Merge `track/finalfix`, contingent only on the independently-running full suite staying
green. Round-1 filing items stand: the Minor list, and folding the
`migrate_estimate_store_metadata.py` g3wired-default straggler into follow-on 04.
