# Issue #387 — Understanding (mechanism + measurement plan)

## The mechanism (verified in code)

- `RetroTruthConfig.lambda_ridge = 1.0` (`src/latent_power/retro_solution.py:32`) feeds the BT
  Newton solver `solve()` in `src/latent_power/retro_solve.py`.
- The solved objective (`_evaluate_loss`, retro_solve.py:402) is:
    `NLL_BT + lambda_ridge * sum(pi^2)`
  With binary pair outcomes y in {0,1} and a clean event order, the data NLL wants to push
  |pi| large (saturate sigmoids); the ridge `lambda * sum(pi^2)` pulls all pi toward 0. At
  lambda=1.0 the ridge dominates, so per-event spread collapses to a near-constant scale set
  by the ridge/curvature balance, not by how spread/chaotic the event was. -> per-event std
  ~0.2414, CV ~= 0.001 (the issue's table; reproduced from artifacts).
- `comparable_scale` (`src/latent_power/retro_comparable.py`) multiplies pi by ONE global
  constant per (entity_scope, phase) (~4.0-5.4, in `params/retro_truth/comparable_scales.json`).
  Rank-preserving, single scalar -> cannot restore event-to-event variation. Confirmed.

## What the labels feed (downstream impact surface)

- The training supervision label is `target_mu` = per-pair retro `power_diff` = pi[i]-pi[j]
  (`load_target_mu_for_event` -> `attach_target_mu_or_drop_entities` -> `PairBatch.target_mu`).
- The module loss is Student-t NLL: `r = target_mu - mu_pred`; `log(sigma) + ((nu+1)/2)*log1p(r^2/(nu*sigma^2))`
  (`src/latent_power/losses.py:student_t_nll`).
- KEY invariance (documented in `nll_eval.py:27-29`): the NLL skill is invariant to a JOINT
  rescale of (target_mu, sigma). So `comparable_scale`'s global rescale is absorbed by the
  sigma head -> it adds NO event-conditioned spread signal. The per-event spread of target_mu
  is what a sigma head could learn an event-conditioned target from; with CV~=0 that signal
  is absent -> "sigma head can only bootstrap from its own residuals" (issue/§1.3).

## The binding caveat, grounded

- §1.3 + §5 line "Retro order == event order (no softer ceiling)" = DURABLE: the retro labels
  already reproduce the observed finishing order exactly. Ordering is correct and must NOT move.
- §7.6.2 (#381, merged) showed the ordering-accuracy gap is MODEL-side (standalone race_weekend
  head evidence-weighting), not label-side. So do NOT "fix" ordering while restoring magnitude.

## The two options (issue frames both; user leans #1 IF cost acceptable)

1. Magnitude-preserving re-solve: lower / non-scalar lambda_ridge (or a solve that does not
   collapse the data likelihood). Risk to MEASURE: does lowering lambda perturb per-event
   ordering (rank corr old-vs-new pi per event) and downstream labels?
2. External event-conditioned spread target from observed dispersion (finishing-gap variance /
   pack compression), ordering labels untouched.

## The measurement yardstick (what makes this decidable WITHOUT a retrain)

I have 1040 existing retro artifacts on disk (lambda=1.0) + DBs 2018-2025. I can:
- Re-solve every (event, phase) at a sweep of lambda (e.g. 1.0, 0.3, 0.1, 0.03, 0.01, ~1e-3)
  using the SAME `solve()` on the SAME PhaseObservation (reconstructed from existing artifacts'
  pairwise diagnostics: pair_index, observed_y, start_bias, weight are all persisted).
- Per event, per phase, per lambda measure:
    (a) ORDERING STABILITY: Spearman/Kendall rank-corr of new pi vs old pi (lambda=1.0), AND
        vs the observed event order (the durable anchor). Fraction of events with rank corr=1.0,
        count of pairwise sign flips. THIS IS THE FRONT-AND-CENTER TRADE NUMBER.
    (b) MAGNITUDE RESTORED: per-event std of pi and its CV across events (target: CV >> 0.001).
- This is a pure CPU re-solve over persisted pairwise data; no DB pull, no NN retrain. Fast.

## Decision logic (per orders)

- If a lower-lambda re-solve restores CV (event-to-event spread) AND keeps per-event ordering
  intact (rank corr ~1.0, ~0 sign flips) -> option 1 is viable; recommend it WITH the numbers.
- If lowering lambda enough to restore magnitude measurably degrades ordering -> STOP at that
  finding and report (do not silently fall back to option 2). User wants to see that evidence.

## Open question(s) to confirm with the Admiral (interrogation)
1. Scope of deliverable: is this issue's acceptance met by (a) the characterization + measured
   trade + a chosen approach + a defined/registered event-conditioned spread target artifact
   that #386 can consume — WITHOUT running a full gold-cycle retrain to prove downstream Brier?
   (The retrain/fused-Brier confirmation is itself deferred per §4.6/§6 and is #390's done-bar.)
2. If option 1 is viable, does "restore magnitude" mean re-solve + re-write the 1040 artifacts
   in this PR, or land the solver capability + a chosen lambda + the spread-target definition
   and let the artifact regeneration ride the next gold cycle (artifacts are derived)?
