# Resume #380 — Rebase + Re-validate (PR #403 CONFLICTING)

Predecessor shipped on merge-base fa9e48b; main advanced to 8860714 (PR #400 #401 #402).
Rebase `constellation/issue-380-regime-beta` (5 commits, 3 substantive) onto origin/main.

## Pre-flight finding: injection point SURVIVES (no STOP)
New `_compute.py` (origin/main, PR #400) still:
- splits laps into quali_sim / long_run buckets via `_split_run_buckets` BEFORE normalization
- calls qs-bucket helpers with `compound_normalizer`: qs_adj (`_compute_sector_features`),
  qs_rep_adj (`_compute_representative_features`), short_quantiles (`_compute_quantile_features`),
  short_bucket_repeatability (`_compute_bucket_repeatability_features`)
- same structure in `compute_constructor_race_features_from_laps`
=> predecessor's surgical routing re-applies in fully recognizable form. STOP condition NOT triggered.

## β-units assessment (theory; empirical re-validation REQUIRED)
`CompoundNormalizer.normalize_lap_time` adjusts RAW lap times (seconds, via baseline) to
"equivalent C3 at age 0" — this is UPSTREAM of the median-relative normalization (PR #400).
The new median-relative encoding `(t − median)/median` is applied AFTER compound adjustment.
β values (`normalized_fractional` effect space) act on raw lap-time adjustments, NOT on the
normalized features. So β units should remain valid in principle. BUT the mission mandates
empirical re-validation on the new encoding — qs_best_adj still exists, still lower-is-better
(confirmed in docs/evo/pace_encoding_change.md §3).

## Conflict resolution plan (7 files)
1. configs/evo/gold_defaults.toml — KEEP BOTH: predecessor's `qs_compound_beta_regime` in [data]
   + main's [training] epochs100/lr1e-3/patience15.
2. docs/architecture/index.md — KEEP ALL reconcile lines; predecessor's #380 line LAST.
3. docs/architecture/packets/evo_predictor.md — MERGE practice_preprocessor/ paragraph (main's
   median-relative text + predecessor's quali_sim bucket routing text); KEEP predecessor's new
   compound_push_regime.py block; KEEP main's module_uncertainty_diagnostics #384 edit.
4. docs/evo/prediction_ceiling_and_priorities.md — main's §6 #384 note + §7 feasibility FIRST,
   then predecessor's §8 shipped-encodings LAST (append-compose).
5. src/evo_predictor/module_training_orchestration.py — KEEP BOTH (non-overlapping: main's
   entity_count at ~L624; predecessor's qs_compound_beta_regime threading at L226/319/371/437).
6. src/evo_predictor/practice_preprocessor/_compute.py — re-apply predecessor's routing: add
   quali_sim_compound_normalizer param + qs_normalizer fallback to both funcs; switch the 4
   qs-bucket calls per func to qs_normalizer; lr calls keep compound_normalizer.
7. tests/unit/evo_predictor/test_practice_preprocessor.py — KEEP main's rewritten tests + append
   predecessor's TestQualiSimRegimeNormalizerRouting class. Verify it passes new encoding.

## Re-validation acceptance (HARD)
push β must still improve the CROSS-COMPOUND subset directionally (magnitude may shift with
median-relative units). If cross-compound improvement does NOT survive => STOP + report to Admiral.

## Optional (cheap)
Repoint compound_push_regime.py provenance comments to now-on-main
docs/evo/compound_crossover_gate_findings.md (already the referenced path — verify).

## Done bar
PR #403 MERGEABLE; fresh validation numbers in PR body; ~322 targeted tests green; pyright clean.
Do NOT merge. Force-push branch (mine alone).
