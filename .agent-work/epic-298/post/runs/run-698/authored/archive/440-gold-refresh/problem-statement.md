# Problem Statement — issue #440 (epic #453 Wave-3 capstone)

## Resolved ask (matches LO-440 exactly)
Run BOTH products end to end in the MAIN checkout, banking Wave-1/2 changes (#410 pooled beta,
#413 manifest skew guard, #425 allfp_best_raw + anchor migration):

1. **Full gold refresh** per `docs/evo/analysis_refresh.md` Steps 1-6 (SKIP Step 0 — priors current),
   through pipeline_validation 7/7 green. Promotion EXCLUDED (hard stop).
2. **Walk-forward 2025 backtest** (#439): leakage-free total fantasy score vs prior baseline
   (`reports/walkforward/multiseason_fantasy.{json,md}`).
3. **#390 fused-Brier** ride-along: new fused Brier vs prior promoted baseline 0.2008.
4. **Acceptance extras**: regenerate perf-history ledger (#433) + Step-6 fantasy/strategy artifacts;
   review runbook and report gaps.

## Protected intent / HARD STOP
- NEVER run promote_gold.py for real (--dry-run preview allowed).
- NEVER alter live params/gold beyond legitimate non-promotion runbook writes.
- NEVER merge. Candidate sits in params/gold_candidate for user sign-off.
- A measured regression / flat result is a COMPLETE deliverable (honest-null clause).

## Success criteria (what proves done)
- pipeline_validation: 7/7 pass.
- Step-2 gate: fusion_train_rows carry non-null pairwise_nll; retro-truth coverage both entity scopes.
- THE COMPARISON computed: walk-forward fantasy vs baseline; multi-season candidate-vs-live; fused Brier vs 0.2008.
- Candidate built + evaluated (tools refuse live gold — correct).
- Perf ledger + Step-6 artifacts regenerated (not stale).
- PR opened "Part of #453, addresses #440"; summary comment on #440.

## Decision authority
Admiral PRE-CONFIRMED this problem statement (the human's delegate). Promotion decision is
reserved for the user's explicit sign-off on the Admiral-presented numbers.
