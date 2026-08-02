# Triage candidates from #375 (race-day conditioned net — honest NULL)

These are follow-up candidates surfaced during the #375 run. NONE were filed as issues
(background run, user away); the admiral/user decides whether to file. Listed for the
checkpoint together with the #375 verdict (PR #428).

## 1. Calibration-only race head (probability sharpening, not ordering)
The conditioned net produced a real, seed-stable pairwise-LL gain over the fair linear pool
(+0.00497, CI [+0.00203,+0.00775]) that is CALIBRATION-shaped — it sharpens probabilities without
reordering drivers. #375's ordering head correctly NULLs this (ordering CIs include 0), but if
probability sharpness is valued in its own right (e.g. for the uncertainty/spread pathway or for
downstream MC race sim confidence), a calibration-only race head is a separate, well-scoped objective
with G2's numbers as the baseline. Different success metric (calibration/coverage, not ordering CIs).

## 2. Uncertainty-head offline measurement (+ optional production plumbing)
`src/evo_predictor/fusion_conditioned_net.py::ConditionedUncertaintyHead` is built (distinct, zero
ordering leverage, softplus-positive) but UNMEASURED. The spread-target artifacts exist for 2021-2025
(`params/spread_target/`). A follow-up could measure it against the spread-target convention (#408) and,
ONLY if justified, wire it at runtime — a heavier change (loader + RuntimeStageConfig slot + CLI), opt-in
default-OFF, composed with the pending quali-anchor activation retrain. Out of #375 scope (ordering-head
verdict reached without it).

## 3. race_start calibration-only head (symmetric to #1)
G1 showed race_start's interaction gain is also calibration-shaped (flat vs grid persistence AND vs the
linear pool on ordering; persistence binds at ~0.875 sign-accuracy). A calibration-only race_start head
is a separate candidate if sharpness there is valued; ordering is a dead end for race_start.

## 4. (Housekeeping, admiral's call) Stale commit subject in branch history
Commit 4b276ee/c7b71ce carries "WIN race ordering" — the initial incorrect verdict, corrected by the
next commit to NULL. HEAD is unambiguously NULL throughout and the PR/docs/verdict are all correct. Not
load-bearing; only matters if the branch history is ever squashed/cleaned before a final merge. Left
as-is (brief prefers new commits over history rewrite; rewrite is the admiral's decision).
