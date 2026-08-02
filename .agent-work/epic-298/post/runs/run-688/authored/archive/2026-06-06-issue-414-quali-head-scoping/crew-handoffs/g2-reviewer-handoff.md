# Reviewer Handoff — issue-414 G2

You are a fresh, independent reviewer. Verify this bounded change yourself; re-derive numbers, do not trust the implementer's claims. Invoke the `constellation-reviewer` skill and drive it. Do not read any transcript.

Repo root (run all commands from here): `C:\Programs\f1Brainz\.claude\worktrees\agent-a82dd9d22cd9863fc`
Set `PYTHONIOENCODING=utf-8`. Python is `py` (never `python`). Read/verify only — nothing long-running; do NOT background anything.

## Gate
g2

## What Was Implemented
A measurement-grade scope study of whether a TARGETED post-hoc pace-anchor blend on the race_weekend qualifying head (`pi`) recovers its ~19pp pairwise sign-accuracy gap below the data ceiling, on the IDENTICAL shared-pair population the §7.6.2 diagnostic uses. Two new files:
- `scripts/scope_quali_anchor_414.py` — the measurement (C1 z-blend pace anchor with α-sweep; C2 rank-anchor robustness; C3 magnitude-only no-op).
- `tests/unit/evo_predictor/test_scope_quali_anchor_414.py` — 4 pinning tests.
Evidence: `.agent-work/issue-414-quali-head-scoping/evidence/scope_anchor_numbers.json` and `g2_scope_run.txt`.

## How to Inspect the Diff
```
git status --short
git diff --stat
```
The two new files are untracked (`??`). The pre-existing `M scripts/diagnose_quali_same_pairs.py` (env-var override) is from G1, NOT this gate — out of scope for your review.

## Task Statement
Confirm the candidate `pi'` is scored on the SAME shared non-tie pair set per event as §7.6.2 (apples-to-apples), the endpoint pins are exact, the magnitude-only no-op is real, and the result is reported honestly (α=1 is the data ceiling, not a model win).

## Close Criteria (verify each INDEPENDENTLY — re-derive, do not just re-run their script)
- (1) **α=0 == baseline (exact).** C1 and C2 at α=0 reproduce the §7.6.2 race_weekend baseline (headline overall ≈ 0.6153, EASY gap≥9 ≈ 0.6926, pairs 23862). Confirm via `--check-baseline` (exit 0) AND by reasoning: at α=0 the blend source is an order-preserving function of `-pi`, so sign-acc must equal the baseline model.
- (2) **α=1 == ceiling (exact, definitional).** C1 at α=1 equals the `best_across_fp` ceiling on the shared pairs (headline overall ≈ 0.8061, EASY ≈ 0.9365). Confirm the output LABELS α=1 as "= data ceiling, definitional, NOT a model win" (honesty requirement).
- (3) **Shared-pairs invariant.** The candidate is scored on exactly `sp._shared_nontie_pairs(...)` per event — same pair count as the diagnostic (23862 headline / 3352 OOS). Verify the script builds `common_set = set(model)&set(baf)&set(blr)&set(target)` and uses the imported `sp._shared_nontie_pairs` / `sp._acc_on_pairs` / `sp._stratified_pairwise` (NO forked ceiling math).
- (4) **C3 no-op is real.** A strictly-monotone within-event transform of `pi` leaves sign-acc unchanged (delta exactly 0). Confirm the transform used is genuinely strictly-monotone and the delta is ~0.
- (5) **Independent re-derivation.** Recompute AT LEAST ONE (candidate, α, slice) cell from raw records (`load_module_record`) + DB (`dqe.*`) WITHOUT calling their `score_regime`/`build_numbers`, and confirm it matches the JSON. Suggested cell: C1 α=0.2 headline overall (expect 0.6947) and EASY (expect 0.8062). [A correct independent recompute of this exact cell is known to yield 0.6947 / 0.8062 on n=23862 / 8345.]
- (6) **No production change.** Only the two new files added (plus the G1 diagnostic edit). `params/`, `src/evo_predictor/` adapters/scorers, fusion files, and the manifest are untouched. No retrain.

## Commands (run yourself)
```
QUALI_SAME_PAIRS_RECORDS_DIR="C:/Programs/f1Brainz/.claude/worktrees/agent-a82dd9d22cd9863fc/.agent-work/issue-414-quali-head-scoping/records" PYTHONIOENCODING=utf-8 py scripts/scope_quali_anchor_414.py --check-baseline
QUALI_SAME_PAIRS_RECORDS_DIR="C:/Programs/f1Brainz/.claude/worktrees/agent-a82dd9d22cd9863fc/.agent-work/issue-414-quali-head-scoping/records" PYTHONIOENCODING=utf-8 py -m pytest tests/unit/evo_predictor/test_scope_quali_anchor_414.py -q
```
For (5), write a short throwaway python snippet that re-derives the cell from scratch using `dqe.best_across_fp_source`, `dqe.classification_order`, `load_module_record`, and `sp._shared_nontie_pairs`.

## Allowed Scope
Read-only verification + running the script/tests + a throwaway re-derivation snippet. Do NOT modify any committed file.

## Constraints the Implementation Must Respect
- Apples-to-apples: identical shared pair set to §7.6.2; ceiling recomputed per regime; NORMAL weekends; no cross-regime pooling.
- No forked ceiling math; no production change; no retrain.
- Honesty: α=1 labelled as the definitional ceiling.

## Evidence Produced
Implementer reports: C1 headline a=0.2 overall 0.6947 / EASY 0.8062; a=0.5 0.7452/0.8691 (rec +0.68/+0.72); a=1.0 0.8061/0.9365 (ceiling). C2 a=0.5 0.7399/0.8737. C3 delta 0.0. Tests 4 passed. Re-derive at least the a=0.2 cell yourself.

## Suggested Model Tier
stronger — the verdict downstream depends on these numbers; independent re-derivation is the crux.

## Stop Conditions
Return BLOCK if: α=0 ≠ baseline or α=1 ≠ ceiling; the pair population differs from §7.6.2; the ceiling math is forked; the no-op delta is non-zero; your independent re-derivation disagrees with the JSON; any production file changed; α=1 is presented as a model win rather than the ceiling.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-criterion finding with the numbers you independently re-derived, blockers, out-of-scope observations.
