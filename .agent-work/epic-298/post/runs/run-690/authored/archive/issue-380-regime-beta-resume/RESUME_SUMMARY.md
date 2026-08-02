# Resume #380 — Completion Summary

Mission: rebase PR #403 (CONFLICTING), reconcile conflicts intent-preserving, RE-VALIDATE
evidence on the new pace encoding, return to MERGEABLE. Do NOT merge.

## Rebase
- Merge-base fa9e48b → rebased onto **current origin/main d801832** (origin advanced from
  8860714 to d801832 mid-run when sibling #404/#382 merged; "8860714 or later" → took latest
  to land genuinely mergeable, since #404 also touched the priorities doc I touch).
- 5 branch commits (3 substantive G1/G2/G3 + 2 archive) replayed; +1 new resume commit.
- Branch now 6 ahead / **0 behind** origin/main. No marker residue. No sibling-lane bleed
  (no #382/#400/#401/#402 source files in my diff — they are the base).

## Conflict resolution (7 known files) — all intent-preserving
1. `configs/evo/gold_defaults.toml` — KEPT BOTH: predecessor `qs_compound_beta_regime="race"`
   in [data] + #400 [training] epochs100/lr1e-3/patience15. (3-way auto-merged; verified.)
2. `docs/architecture/index.md` — KEPT ALL reconcile lines (#356/#368/#371/#369), #380 LAST.
   (auto-merged; verified.)
3. `docs/architecture/packets/evo_predictor.md` — MERGED practice_preprocessor/ paragraph
   (#400 median-relative text + #380 quali_sim bucket routing text into one); KEPT #380 new
   compound_push_regime.py block + #402 #384 sigma note. (manual merge of the shared line.)
4. `docs/evo/prediction_ceiling_and_priorities.md` — compose order §7.5 → §7.6 → §7.7 (#382,
   from d801832) → §8 (#380, mine last). Then UPDATED §8.1 numbers to fresh re-validation.
5. `src/evo_predictor/module_training_orchestration.py` — KEPT BOTH (non-overlapping: #401
   entity_count + predecessor qs_compound_beta_regime threading). (auto-merged; verified.)
6. `src/evo_predictor/practice_preprocessor/_compute.py` — re-applied predecessor routing
   (quali_sim_compound_normalizer param + qs_normalizer fallback, 4 qs-bucket calls per func
   to qs_normalizer, lr calls keep compound_normalizer). Only the two docstrings conflicted;
   3-way merge had already re-applied the routing correctly. KEPT both docstrings.
7. `tests/unit/evo_predictor/test_practice_preprocessor.py` — KEPT #400 rewritten tests +
   predecessor's TestQualiSimRegimeNormalizerRouting class. (auto-merged; 72 tests green.)

## Re-validation (the hard requirement) — PASSED, no β-unit change
- qs_best_adj survives in the new encoding (lower-is-better; pace_encoding_change.md §3).
- β acts on RAW lap times upstream of normalization; median-relative is a monotone transform;
  harness scores within-event pairwise order → ENCODING-INVARIANT. No β-unit adjustment needed.
- Fresh 2022–2025: **CROSS +0.60pp (0.7131→0.7191) vs OVERALL +0.26pp (0.7014→0.7040), ~2.3×.**
- Stale (minmax): CROSS +0.55pp / OVERALL +0.29pp, ~1.9×. Fresh is marginally STRONGER.
- Cross-compound improvement SURVIVES. STOP condition NOT triggered.

## β provenance (optional task)
- Provenance comments already point to docs/evo/compound_crossover_gate_findings.md (now on
  main via #400) — no repoint needed. Vendored β constants verified EQUAL to the doc's primary
  pooled fit (C1 +0.003012 … C6 −0.007365, SEs match).

## Verification
- 347 targeted tests green (push regime, practice preprocessor + constructor, gold config +
  runner, data adapter incl. qs-resolver, orchestration, labeled-batches + record, pipeline +
  validation, run CLI).
- pyright: 0 errors / 0 warnings / 0 informations on all 9 touched src files (local).
- CI: docs pass, arch-map pass, pyright (CI) — see checks.

## Decisions logged
- D1: Rebased onto d801832 (latest), not the stale 8860714, because origin advanced mid-run and
  #404 collided with my priorities-doc edit. Covered by "8860714 or later"; required for true
  MERGEABLE. (cheap/reversible-equivalent, logged.)
- D2: Did NOT history-rewrite to extract the resume RECONCILIATION_PLAN.md accidentally captured
  in the G2 commit — `.agent-work/`-on-branch is the established pattern (predecessor committed
  its full archive package to this same branch). Lower-risk to leave than to force a surgical
  rebase. (logged.)
- D3: Squashed two stray re-validation commits (one had a shell-garbled message) into one clean
  commit cb1a96d via soft reset. (logged.)

## PR state
PR #403: CONFLICTING → **MERGEABLE**. Body updated with fresh numbers + rebase note.
DO NOT merge — the Admiral merges.
