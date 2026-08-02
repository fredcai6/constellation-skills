# Implementer Handoff — issue-414 G2

You are a fresh crew member. Implement exactly this bounded task. Do not read any transcript. Invoke the `constellation-implementer` skill and drive it.

Repo root (run all commands from here): `C:\Programs\f1Brainz\.claude\worktrees\agent-a82dd9d22cd9863fc`
Set `PYTHONIOENCODING=utf-8` in every shell. Python is `py` (never `python`). Do NOT run anything in the background — all work here completes in well under a minute per run.

## Gate
g2

## Task
Build `scripts/scope_quali_anchor_414.py` (DB-only; stdlib + numpy; reuse the existing harness — DO NOT fork the ceiling math) plus `tests/unit/evo_predictor/test_scope_quali_anchor_414.py`. The script measures whether a TARGETED post-hoc fix to the race_weekend qualifying head recovers the bulk of its ~19pp pairwise sign-accuracy gap below the data ceiling, on the IDENTICAL shared-pair population the §7.6.2 diagnostic uses.

## Protected Intent
MEASUREMENT-GRADE ONLY. This is a flag/script that post-processes the race_weekend `pi` and re-scores it. ZERO production behaviour change: do NOT modify `quali_power_adapter.py`, the gold bundle, the sampled runtime manifest, any production scoring path, `src/evo_predictor/fusion.py`, `src/evo_predictor/fusion_training/`, or `docs/evo/fusion_rework_findings.md`. Apples-to-apples with §7.6.2 is sacred: the post-processed source must be scored on the SAME shared non-tie pair set per event as the baseline.

## Background you need (already established)
- The race_weekend quali head = module `driver_quali_power_from_race_weekend`. Its features are within-event practice pace only; it has NO cross-channel "general pace" anchor. It extracts pairwise sign-acc 0.6149 vs a data ceiling (best_across_fp min-sector pace over FP1/FP2/FP3) of 0.8061 — a ~19pp gap, concentrated on EASY/far-apart pairs (model 0.687 vs ceiling 0.937 at gap≥9).
- Regenerated per-event records (inference on the committed gold bundle, no retrain) live at `.agent-work/issue-414-quali-head-scoping/records/{rw,rh}_{2018..2025}.record.json` (+ `.npz`). Read via `src.evo_predictor.module_record.load_module_record`. Each event has `pi`, `entity_ids`, `actual_positions`.
- The diagnostic `scripts/diagnose_quali_same_pairs.py` already computes, per event, the SHARED non-tie pair set across {model=-pi, best_across_fp, blend_rank, target=DB Q}, recomputes the ceiling per regime, and stratifies by target Q-gap band (the `far (gap>=9)` band is the EASY slice). It reads records from `QUALI_SAME_PAIRS_RECORDS_DIR` (env-var; defaults to the 381 path). Set that env var to the 414 records dir.

## The measurement (do exactly this)
Reuse the diagnostic's internals — import `scripts.diagnose_quali_same_pairs as sp` and `scripts.diagnose_quali_evidence as dqe`. For the race_weekend channel, mirror the diagnostic's per-event flow (NORMAL weekends only; same regime split: HEADLINE 2018-2024, OOS 2025; ceiling recomputed per regime), but substitute a POST-PROCESSED model source for `-pi`:

Per event, for the common driver set `common = set(model) & set(best_across_fp) & set(blend_rank) & set(target)`:
- `pi_vec` = the head's `pi` restricted to `common`, expressed as the model ordering source `m = {d: -pi[d]}` (lower=better, matching the harness `_model_source`).
- `anchor = best_across_fp_source(con, rnd, agg_theoretical_best, ("FP1","FP2","FP3"))` restricted to `common` (lower=faster — same orientation as `m`).
- Build the SHARED non-tie pair list with `sp._shared_nontie_pairs(common_sorted, target_restricted, [m, baf, blr])` EXACTLY as the diagnostic does, so the pair population is identical to the baseline.

Candidates (each scored on that SAME shared pair list, pooled per regime, plus the gap≥9 EASY slice via `sp._stratified_pairwise`):
- **C1 [PRIMARY] pace-anchor blend.** Per event, z-standardize within `common`: `zm = (m - mean(m)) / std(m)`, `za = (anchor - mean(anchor)) / std(anchor)` (guard std==0 -> treat as all-zeros). Blended source `s = (1-α)*zm + α*za`. Sweep α in `{0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0}`. Lower=better (both zm and za are lower=better). Score sign-acc of `s` vs target on the shared pairs.
- **C2 rank-anchor (robustness).** Same as C1 but replace zm/za with within-`common` ranks: `rm = rankdata(m)`, `ra = rankdata(anchor)` (average ranks for ties), blend `s = (1-α)*rm + α*ra`, same α sweep. (This checks the verdict is not a z-scaling artifact.)
- **C3 magnitude-only no-op.** Apply a STRICTLY MONOTONE within-event transform to `m` that preserves order (e.g. `s = sign(m)*abs(m)**1.5` after centering, or simply `s = 3*m + 7`, or `s = sinh(m)`) and show sign-acc is IDENTICAL to α=0 to numerical precision. This demonstrates a pure recalibration of magnitude CANNOT move pairwise sign-accuracy.

## Endpoints that MUST hold (these are your correctness pins)
- **α=0** for C1 and C2 must reproduce the §7.6.2 baseline EXACTLY (overall headline race_weekend ≈ 0.6153 on the 414 records; EASY gap≥9 ≈ 0.6926; pairs 23862). At α=0, `s` is a strictly-increasing function of `m` (rank for C2; identity-scaled for C1) so the ordering — hence sign-acc — equals the baseline model. If it does not match to ~1e-9, your plumbing is wrong: fix it, do not paper over it.
- **α=1** for C1 must equal the `best_across_fp` ceiling on the shared pairs (overall headline ≈ 0.8061; EASY ≈ 0.9365), because `s` becomes a monotone function of the anchor. Label α=1 in all output as "= data ceiling (definitional, NOT a model win)".

## Output
- Print a table per regime: candidate, α, OVERALL sign-acc, EASY(gap≥9) sign-acc, with the ceiling rows (overall 0.8061 / EASY 0.9365 headline; 0.7643 / recompute EASY OOS) shown for reference, and the recovered-fraction `(acc(α) - acc(0)) / (ceiling - acc(0))` for the overall and EASY columns.
- Write a machine-readable JSON to `.agent-work/issue-414-quali-head-scoping/evidence/scope_anchor_numbers.json` containing every (candidate, regime, α) -> {overall_acc, easy_acc, overall_pairs, easy_pairs} plus the per-regime ceilings and the C3 no-op deltas.
- Add a `--check-baseline` flag that asserts α=0 reproduces the §7.6.2 headline numbers within tolerance and exits 0/1 (the Commander's gate references `py scripts/scope_quali_anchor_414.py --check-baseline`). When run with `--check-baseline`, set the records dir from `QUALI_SAME_PAIRS_RECORDS_DIR` if set, else default to the 414 records path.

## Tests (tests/unit/evo_predictor/test_scope_quali_anchor_414.py) — pin all four
- (a) C1 α=0 and C2 α=0 reproduce the baseline model sign-acc on a real event (or the pooled headline) to ~1e-9.
- (b) C1 α=1 equals the best_across_fp ceiling sign-acc on the shared pairs to ~1e-9.
- (c) C3: a strictly-monotone within-event transform of `pi` yields identical pooled sign-acc to α=0 (the no-op invariant).
- (d) shared-pairs invariant: the candidate is scored on exactly `sp._shared_nontie_pairs(...)` (same pair count as the diagnostic for that event).
Use the real 414 records (set `QUALI_SAME_PAIRS_RECORDS_DIR` in the test, or import and point `sp.RECORDS_DIR`). Keep tests deterministic and fast (a single event or the pooled headline is fine).

## Allowed Scope
- NEW: `scripts/scope_quali_anchor_414.py`
- NEW: `tests/unit/evo_predictor/test_scope_quali_anchor_414.py`
- READ-ONLY reuse (import, do not fork): `scripts/diagnose_quali_same_pairs.py`, `scripts/diagnose_quali_evidence.py`, `src/evo_predictor/module_record.py`.

## Specific Exclusions
- NO production behaviour change. NO retrain. Do NOT modify `quali_power_adapter.py`, the gold bundle, the manifest, any adapter/scorer, `src/evo_predictor/fusion.py`, `src/evo_predictor/fusion_training/`, `docs/evo/fusion_rework_findings.md`, or `docs/evo/prediction_ceiling_and_priorities.md` (that doc is the Commander's to write in G3).
- Do NOT fork the ceiling math or the shared-pairs primitive — import them from `sp`/`dqe`.
- Do NOT pool across the 2018-2024 and 2025 regimes.

## Constraints
- DB-only; py; PYTHONIOENCODING=utf-8; deterministic.
- Reuse `sp._shared_nontie_pairs`, `sp._stratified_pairwise`, `sp._acc_on_pairs`, `dqe.best_across_fp_source`, `dqe.classification_order`, `dqe.agg_theoretical_best`, `dqe.open_db`, `dqe.events_for_year`, `dqe.is_sprint_weekend`. (Inspect `sp` for exact names/signatures — they are module-level.)
- If you touch only `scripts/` + `tests/`, no `src.utils.simplification_limits` run is needed. Run `py -m pytest tests/unit/evo_predictor/test_scope_quali_anchor_414.py -q` and it must pass.

## Required Evidence
- `py -m pytest tests/unit/evo_predictor/test_scope_quali_anchor_414.py -q` output (all pass).
- The script's full stdout table captured to `.agent-work/issue-414-quali-head-scoping/evidence/g2_scope_run.txt`.
- The emitted `scope_anchor_numbers.json`.
- `py scripts/scope_quali_anchor_414.py --check-baseline` exit 0.
- `git status --short` showing only the two new files (+ untracked .agent-work artifacts).

## Verification Commands
```
QUALI_SAME_PAIRS_RECORDS_DIR="C:/Programs/f1Brainz/.claude/worktrees/agent-a82dd9d22cd9863fc/.agent-work/issue-414-quali-head-scoping/records" PYTHONIOENCODING=utf-8 py scripts/scope_quali_anchor_414.py
QUALI_SAME_PAIRS_RECORDS_DIR="C:/Programs/f1Brainz/.claude/worktrees/agent-a82dd9d22cd9863fc/.agent-work/issue-414-quali-head-scoping/records" PYTHONIOENCODING=utf-8 py scripts/scope_quali_anchor_414.py --check-baseline
PYTHONIOENCODING=utf-8 py -m pytest tests/unit/evo_predictor/test_scope_quali_anchor_414.py -q
```

## Suggested Model Tier
stronger — correctness-critical analytical plumbing (the α=0/α=1 endpoint pins and the shared-pairs substitution must be exact); honesty about the ceiling endpoint matters.

## Authority
Candidate set (C1 pace-anchor blend, C2 rank-anchor, C3 no-op), the anchor choice (best_across_fp min-sector), and the apples-to-apples requirement are decided by the Commander. You must NOT invent a different anchor signal, change the pair population, retrain, or wire anything into production. If α=0 won't reproduce the baseline, STOP and report — do not adjust tolerances to force a pass.

## Stop Conditions
Stop and return if: α=0 does not reproduce the baseline; α=1 does not equal the ceiling; the shared-pairs invariant cannot be preserved; producing required evidence needs a production change or retrain; you would need to touch an excluded file.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, the full candidate×α table (overall + EASY + recovered-fraction, both regimes), the C3 no-op result, test output, the evidence/JSON paths, assumptions, stop conditions hit, out-of-scope observations.
