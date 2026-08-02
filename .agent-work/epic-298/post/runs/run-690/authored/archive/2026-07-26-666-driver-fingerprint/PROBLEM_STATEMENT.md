# #666 DriverFingerprint — consolidated problem statement (delegated understand)

Reconciled against frozen `LAUNCH_ORDER-666.md` (epic #659 Wave 3) + verified against actual code
(recon 2026-07-26). Delegated mode: no reachable human; the launch order is ratified intent.

## Mission (one bounded issue)
Build a **versioned DriverFingerprint cell store + a hierarchical Student-t shrinkage fit** over
#664's class-grain utilization observables, **both channels**, **strictly-pre**. Per (driver,
rules-era), k=4 corner-severity class cells (mean, σ, support n), fit by hierarchical shrinkage
`field mean → driver-overall → class cell + class-across-drivers parent`, recency-weighted.
**Slow-offline-loop mutation only; NO fit-on-read path** (structural, not convention).
Build season-CAPABLE, run BOUNDED.

## Verified baseline (where the order's framing is refined by the code)
1. **`ClassVocabulary` + its F12-stability-verdict field do NOT exist yet** — net-new for #666. Closest
   existing type is `VocabularyRef` (`segment_map/identity.py`), which carries NO verdict field. The
   F12 verdict currently lives only in `scripts/f12_held_out_stability.py` output. So #666 introduces
   `ClassVocabulary` as the seam that carries the F12 PASS/FAIL verdict and refuses fitting against a
   failed-gate vocabulary by default.
2. **physics_estimates.db has FULL 2023-Q coverage (all 22 rounds, `C:/Programs/f1Brainz/data/physics_estimates.db`)**
   → a 3–4 circuit bounded slice (permanents + a street, 4-driver core VER/PER/LEC/SAI) is well-supported
   and OFFLINE. This is NOT the 1-circuit-starved case; the class-across-drivers parent and the #675
   coverage check get real signal. (Full-season run stays OUT — that's #670/HITL.)
3. **#664 fit input** = `driver_class_observables` table in `src/physics/utilization/reference_utilization_store.py`
   (own DB, default `data/reference_utilization.db`). PK `(year, session_type, gp_name, round_idx,
   constructor, driver, class, map_version)`. TIME channel: `time_deficit_s` (populated), `sigma_lapsampling`
   (**DORMANT — NULL everywhere; #664 emits nothing**), `g_sigma_onesided` (**0.0 everywhere while grip
   store empty — expected soft-degrade**). ENERGY channel: `deployment_share`, `deployment_phase_fraction`.
   `n_points` = soft-membership FLOAT count. Classes per driver = 6 (`straight`, `braking_zone`, +
   `severity:2023:v1:c0..c3`). **k=4 corner-severity cells = the `severity:*:c0..c3`; `straight` EXCLUDED
   (confounded negative control); `braking_zone` is a seg-type label, not one of the k=4 severity classes.**
4. **frozen_constants.py has NO class-axis coverage / shrinkage-σ constants** → any threshold this run needs
   (nominal coverage level, under-coverage decision bound, recency half-life, thin-support n floor) is a
   **FLOAT** — a new named set pre-registered BEFORE the first real-data run (Ruling F12). The class
   `shared_floor` VALUE is data-derived (median pattern of `_shared_floor_for_param`), not a hand-picked
   threshold, so it is computed not pre-registered — but the derivation params are pre-registered.
5. **Rules-era key** — `RegulationEra.for_season(season)` keys off the `int` season (no string era id);
   era dimension value is derived from that seam (design choice settled at plan, within latitude).
6. **Store house pattern** — `__init__(db_path, *, must_exist)`, create-on-construct, `INSERT OR REPLACE`
   on PK, additive `_migrate_missing_columns`, `format_version` stamp. **NULL-PK gotcha**: SQLite PK cols
   allow NULL unless `NOT NULL`; a NULL PK component defeats `INSERT OR REPLACE` idempotency → the order's
   canonical non-NULL `cell_key` is the structural fix.

## The five epic-owner rulings (binding)
No frame-kill (measured-null = complete); frozen constants (F12, pre-register); pre-quali (no race-outcome
leakage); lowest dimensionality (dormant `channel`/what-measure slots present-unused); no baked-in normality
(Student-t via canonical `predictive_t`, ν default 4.0).

## #675 (I OWN it) — the FIRST plan-phase investigation, gates the class-axis intervals
#665's synthetic harness found CLASS-axis nominal-80% `predictive_t` coverage ~0.29–0.41 (badly under),
DRIVER axis ~0.90–0.96 (fine). Cause: the count-driven epistemic term `sqrt(1+1/n_eff)` in `predictive_t`
does NOT capture the independent class-effect variance. Investigate whether this generalizes to a REAL
driver×class fit (on the bounded slice); if yes, apply `pool_random_effects.shared_floor` (additive
quadrature σ floor, #627 G4/#506) at the fingerprint CLASS level (or wider ν); record recommendation.
Either way close #675 with this PR. #675 forbids editing pooling.py/student_t.py/driver_utility.py; #666
applying a documented `shared_floor` in its OWN store/fit is in-scope. Reproduce the #665 coverage method
(`scripts/pooling_imbalance_validation_665.py`: fit_two_way driver×class → predictive_t per axis at level
0.80 → empirical interval coverage) on the real slice's support structure.

## Acceptance invariants (all provable on the bounded slice)
1. **Cutoff-leakage** (keystone): `as_of_round=R` fit cannot see any row with `round_idx > R` (strictly-pre
   on the DRIVER side; cite #628's measured 14.6× materiality precedent). `as_of_round` REQUIRED, no default.
2. **Thin-cell σ-widening priced ONCE** (idempotence unit test; never re-filtered/re-widened downstream).
3. **Loud refusal on era/vocabulary mismatch** — no silent substitution; refuse a failed-gate ClassVocabulary
   by default.
4. **k-cells-always-populated** — every fingerprint returns exactly k cells; missing support → `unresolved`
   status row, never a missing row.
5. **#675 class-axis coverage recommendation recorded** (+ `shared_floor` applied at fingerprint layer if it
   generalizes).
Plus: **G σ⁺ carried** as a one-sided σ component on the time channel; soft-degrades to 0 while grip store
empty → **byte-identical point** invariant preserved.

## Scope boundaries / out of scope
Build season-capable, run bounded (offline 3–4 circuit 2023-Q slice only; NOT the full season = #670/HITL).
OUT: the join #668; race-side push/managed cells (Build 2); low-rank factorization (no read-boundary hook);
moving G's μ off 0 (#678); populating grip store (#692); changing k/class vocabulary (#642 downstream).
#560 (thin-fit acceptance floor) — prose reconciliation only, not solved.

## Hygiene (binding)
DB-BLOB GUARD: never commit `data/f1_data_*.db` (stage deliverables explicitly, `git checkout --` if
Modified); write the fingerprint store to its OWN db (#632); tests use temp/scratch DBs (#656). Map fence:
do NOT touch `docs/architecture/*` — map impact as prose + stage `notes-666.md`/`666-cartography/`. Stage the
feedback trio under `.agent-work/staged-feedback/666-driver-fingerprint/` with a `FENCE.md`. Interpreter PIN
`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`; NEVER bare `py`. Editable-.pth worktree
trap: bespoke scripts must force worktree-first sys.path (`PYTHONPATH=.` from worktree root / `python -m`) or
they silently import MAIN repo src/. Multi-ship session: PID-only kills, bounded foreground polling.

## Open design choices to settle at plan (all within latitude)
- Era-key derivation from `RegulationEra.for_season` (string form of the era dimension).
- `braking_zone` excluded (k=4 = the 4 severity cells only) — confirm against "exactly k cells".
- The new frozen constant set names/values (coverage level, under-coverage bound, recency half-life,
  thin-support n floor) — pre-registered before the first real fit.
- Whether `braking_zone`/`sigma_lapsampling` NULLs feed the fit (they don't; time-channel σ = predictive_t
  epistemic + G σ⁺(=0) + any class shared_floor).
