# Implementer Handoff

## Gate
`g4` — held-out-weekend DIAGNOSTIC (strictly-pre). THE leakage-critical gate (#670). This SIZES the join's value; it does NOT re-establish join correctness (#667 did).

## Task
Build `scripts/run_heldout_diagnostic_670.py` that, over the consolidated season slice, for each held-out weekend W (round R with sufficient strictly-prior data) predicts each driver's weekend utilization and scores THREE priors against W's ACTUAL observed utilization, then emits a diagnostic report (md + json) to an ISOLATED out-dir. Compose LANDED pieces (`join_weekend_prior`, `fit_driver_fingerprints`); build NO new model.

**Inputs (read-only):** consolidated slice `.agent-work/670-season-run/artifacts/scratch/refutil_season_2023.db` (`driver_class_observables` + `reference_laps`); covered rounds from `season_results.json` (rounds 3-22 covered; 1-2 parked).

## The three arms (ALL driver-performance inputs strictly-pre; the DIFFERENCE among arms is what we measure)
For held-out weekend W at round R, driver d, channel ch ∈ {utilization, energy}:
1. **fingerprint × composition** = `join_weekend_prior(W_composition, cells_d@as_of_round=R-1)` → PredictiveT with mean m1.
2. **driver-overall-only baseline** = `join_weekend_prior(UNIFORM_composition, the SAME cells_d@R-1)` → mean m2. This is the join's **T7-1 uniform-composition form** (equal shares → resolved-weighted mean reduces to the unweighted driver mean). THIS IS THE ONE DOCUMENTED BASELINE — state it + justify per #667 TC-1 in the report.
3. **golf null** = the field / NO-driver-term prediction: the per-class FIELD mean pooled over rounds < R (strictly prior, NO driver term), composed with W_composition → m3, carried with an honest predictive interval (Student-t or the field cross-driver dispersion — NO baked normality). Pin this definition in code + report.

## LEAKAGE GUARDS (covering EVERY arm's inputs — verify in code AND test)
- `fit_driver_fingerprints` uses SQL `round_idx <= as_of_round` (INCLUSIVE), so pass **as_of_round = R-1** to EXCLUDE round R. Assert in code + a test that NO round ≥ R row enters the fingerprint fit.
- The **golf-null field pool MUST exclude round R** (pool over rounds < R only). Assert in code + a test.
- (These two guards are the subtle-and-silent correctness the OPUS tier exists for.)

## COMPOSITION handling (Admiral D1 — REQUIRED)
- W_composition = the **FIELD-REFERENCE** row's `time_shares` (`reference_id="__field__"`, row_kind="field") — the field-MEDIAN-across-all-constructors per-class corner share. CONFIRMED it is field-median, NOT driver-specific. Use it IDENTICALLY across all 3 arms (it is shared track-geometry, so it cannot advantage the fingerprint arm over the baseline — the COMPARISON stays fair, which is what the diagnostic measures).
- (a) Keep a PROMINENT caveat in the report: W's composition is track-geometry derived from W's own reference lap (not strictly-prior on a 2023-only slice); it is shared across arms and carries no DRIVER-specific leakage (the fingerprint cells ARE strictly-pre). (b) Where a strictly-prior same-circuit composition exists in the slice, add a sensitivity readout (NOTE: a 2023-only slice has NO prior-year same-circuit composition, so this will usually be ABSENT — state that plainly). (c) In code + review, CONFIRM the composition read is the field row, never a driver's own R-laps.

## Truth + scoring
- The prediction target = the driver's ACTUAL composition-weighted weekend utilization at W: compose W's ACTUAL per-class `driver_class_observables` (for d at round R) with the SAME W field-composition weights (utilization→time_deficit_s; energy→deployment_share). This is the observed scalar each arm's PredictiveT predicts.
- Score each arm with a metric honoring Student-t σ: mean predictive log-score (primary) + interval coverage + mean |resid|. Report per-arm AGGREGATE over all held-out driver-weekends AND a per-class/per-channel + per-round breakdown.
- STATE in the report that this sizes COMPOSITION-WEIGHTING value (arm1 vs arm2) and WHOLE-DRIVER-TERM value (arms 1/2 vs golf null) — NOT the full hierarchical pool vs an independent aggregate.

## Held-out set + thin-cell honesty (Admiral)
- Held-out rounds = the covered rounds with strictly-prior fingerprint data. Round 3 (as_of_round=2, no covered prior) is UNRESOLVABLE → report as thin/unavailable, do NOT force it. Early rounds (4-5) have 1-2 prior rounds → thin/unresolved fingerprints → report as HONEST thin-cell behavior (no-frame-kill), do not force. The signal being small/thin is a COMPLETE result.

## Close Criteria
- `scripts/run_heldout_diagnostic_670.py` produces `heldout_diagnostic_670_report.{md,json}` under `.agent-work/670-season-run/artifacts/` with: the 3-arm per-arm aggregate scores, per-round/per-class/per-channel breakdown, the golf-null floor, the composition caveat (prominent), the thin-early-rounds note, and the one-documented-baseline statement.
- Zero leakage: as_of_round=R-1 for the fingerprint fit AND the golf-null field pool excludes round R — both asserted in code and by tests.
- Composition confirmed field-reference; Student-t σ preserved on all arms (no normal approximation); NO new model (composes join_weekend_prior + landed cells + a field-mean pool).
- `tests/unit/physics/fingerprint/test_heldout_diagnostic.py`: (i) LEAKAGE-GUARD for the fingerprint fit (no round ≥ R rows enter); (ii) LEAKAGE-GUARD for the golf-null field pool (no round ≥ R rows enter); (iii) T7-1: join under uniform composition == unweighted resolved-cell mean (the baseline identity); (iv) golf-null-is-a-floor sanity; (v) the composition used is the field row, not a driver row. Tests may use a small synthetic slice; do NOT run the real full pipeline in unit tests.
- All existing fingerprint tests pass; pyright-0 on new code.

## Allowed Scope
NEW: `scripts/run_heldout_diagnostic_670.py`, `tests/unit/physics/fingerprint/test_heldout_diagnostic.py`. Import freely from `src/physics/fingerprint/{join,fit,store,address,vocabulary}.py`, `src/physics/utilization/reference_utilization_store.py`, `src/physics/pilot/pipeline.py` (e.g. `derive_pilot_vocabulary`). Do NOT edit any of those modules or any frozen set.

## Specific Exclusions
- Do NOT modify `join.py`/`fit.py`/`store.py`/frozen sets. Do NOT build a new statistical model (compose landed pieces). Do NOT use round ≥ R data for ANY driver-performance input. Do NOT touch docs/architecture/*; do NOT run FastF1/online.

## Constraints
- ZERO leakage (as_of_round=R-1; golf-null pool < R); Student-t σ preserved (no baked normality); ONE documented baseline; OFFLINE; read-only slice; pinned 3.14 interpreter (`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`, NEVER `py`); worktree-first sys.path guard; pyright-0.

## Map Anchors (inbound)
- **Structural:** `src/physics/fingerprint/join.py::join_weekend_prior` (T7-1: uniform composition → unweighted resolved-cell mean; arms 1+2 — see its module docstring); `src/physics/fingerprint/fit.py::fit_driver_fingerprints` (`round_idx <= as_of_round` INCLUSIVE → use R-1); `reference_utilization_store.py` field row (`__field__`, field-median composition); `derive_pilot_vocabulary` (pipeline.py) for the severity vocabulary.
- **Capability:** size-the-join-value — fingerprint×composition vs driver-overall-only vs golf null, strictly-pre.
- **Constraints:** zero-leakage (ALL arms); student-t preserved; no new model; one documented baseline; composition-is-field-reference-track-geometry.
- **Decision anchors:** decision:diagnostic-baseline — join T7-1 uniform-composition form (same code path, composition flattened). `@grade: guess · leans g4-implement · settle: state+justify in report per #667 TC-1.` · decision:composition-source — field-reference W composition as shared track-geometry, caveated. `@grade: settled/human (Admiral D1 endorsed) · leans g4-implement`
- **Evidence expectations:** two leakage guards (fingerprint fit + golf-null pool, no round≥R rows); golf-null is the floor; T7-1 baseline identity holds; composition = field row.
- **Map confidence flags:** diagnostic correctness is subtle-and-silent (leakage) — the OPUS-tier reason; robust review to follow.

## Deliverable Path Check
- **Committed** — `scripts/run_heldout_diagnostic_670.py`, `tests/unit/physics/fingerprint/test_heldout_diagnostic.py` (tracked; check-ignore exit 1). The diagnostic report md/json land under `.agent-work/670-season-run/artifacts/` = **Local-only** (folded into the G5 committed season report).

## Required Evidence
- LOAD-BEARING (prove rigorously): `... -m pytest tests/unit/physics/fingerprint/test_heldout_diagnostic.py -q` passes INCLUDING both leakage guards + the T7-1 identity (paste); `... -m pytest tests/unit/physics/fingerprint -q` passes; a REAL run of the diagnostic over the actual slice produces the report (paste the per-arm aggregate scores + which rounds resolved vs thin).
- CONFIRMATORY: pyright-0; a one-line confirmation the composition read targets the `__field__` row.

## Verification Commands
```bash
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/fingerprint/test_heldout_diagnostic.py -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe -m pytest tests/unit/physics/fingerprint -q
C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/run_heldout_diagnostic_670.py
```

## Suggested Model Tier
`stronger` — reason: leakage correctness is subtle-and-silent (the launch order's stated OPUS-tier reason); a wrong as_of_round or a golf-null pool that includes round R silently mis-sizes the join's value and would be reported as real under no-frame-kill.

## Authority
Decided (this handoff + Admiral D1): the ONE baseline is join T7-1 uniform-composition; composition = field-reference W row shared across arms; as_of_round=R-1; golf-null pool < R; Student-t preserved. You choose the exact predictive-log-score formula + the loop structure and DOCUMENT them. You must NOT: use round≥R data for any driver input, edit join/fit/frozen sets, or build a new model. If zero-leakage seems to require changing join/fit, STOP and return.

## Stop Conditions
Stop and return if: achieving strictly-pre requires editing join.py/fit.py; the slice lacks a field row or per-class observable a computation needs; a decision beyond this authority (e.g. a second baseline) is needed.

## Return Format
Write IMPLEMENTER_RESULT to `.agent-work/670-season-run/crew-results/g4-implementer-result.md` (slice, files changed, the exact scoring formula + loop, the two leakage guards' test evidence, the per-arm aggregate scores, which rounds resolved vs thin, the composition-source confirmation, assumptions, workflow feedback). Then SendMessage cmdr-670 a thin pointer before ending your turn.
