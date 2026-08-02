# Consolidated problem statement — issue #375 (race-day context-conditioned fusion net)

Source of truth: the admiral's commander brief (checkpoint-2 re-scope, user-ratified 2026-06-06).
This is a BACKGROUND job; the user is away. The brief pre-rules all major decisions and explicitly
forbids user questions ("No user questions; blocked => early return marked BLOCKED"). Therefore the
`understand` human checkpoint was consumed at checkpoint-2 ratification; the brief IS the confirmed,
protected problem statement. No live Interrogator pass is run (it would violate the brief and cannot
reach an away user). Surfacing-of-decisions happens via the PR + #375 verdict comment (the user's
later checkpoint), exactly as the honest-null clause prescribes.

## The ask (one paragraph)
Build a context-conditioned fusion net for RACE-DAY tasks {race_start, race} only (quali EXCLUDED,
deferred per #374). Two heads, kept distinct: (1) an ORDERING head, antisymmetric by construction
(logit(x)=g(x)-g(-x), flexible capacity, NOT fixed product terms), operating on the 4 module Delta-pi
plus derivable #377 conditioning (prior-stage order foremost); (2) an UNCERTAINTY head (the #408
magnitude / s_e component) against the production spread-target convention, with ZERO ordering
leverage. Measure offline-first: LOSO over seasons, event-cluster bootstrap CIs, seed-stability,
reusing the #374 metalearner methodology. Beat a FAIR linear ceiling (Model1) by >= the #374 gap's
lower CI bound per in-scope task without degrading calibration vs the correlated-fusion option.

## Protected intent (must NOT be violated)
1. Do NOT modify the quali anchor (`quali_pace_anchor.py`, its config keys, §7.6.4) or
   `docs/evo/prediction_ceiling_and_priorities.md`. May touch `sampled_runtime.py` for MY net's
   opt-in wiring WITHOUT altering the anchor attach.
2. Production integration is OPT-IN, DEFAULT OFF. Default-ON is not this issue.
3. HONEST-NULL: if the net cannot beat the fair linear ceiling offline (either/both tasks), that is a
   COMPLETE successful deliverable — report, do NOT wire production code for a losing net, do NOT close
   #375 (comment the verdict; admiral/user decide at checkpoint). Win => PR "Closes #375".
4. DB is canonical, read-only, absolute path `C:/Programs/f1Brainz/data/`. No FastF1. py not python.
   PYTHONIOENCODING=utf-8 in shells + child envs of captured subprocesses.
5. Records are non-committed generated artifacts (gitignored). Untracked files don't exist in worktrees.

## Mandatory STOP-GATE (G1, before any net code)
Reconcile race_start's +1.23pp pairwise-LL interaction gain (#374) against the grid->lap3 0.875
persistence ceiling, IN ORDERING METRICS. Translate Model2b's race_start gain into pairwise
sign-accuracy / rank MAE / spearman vs (a) the best linear pool (Model1) and (b) grid-order
persistence. Outcomes all acceptable: real ordering gain beyond persistence => full scope; gain is
confidence-shaped (ordering ~ flat) => DROP race_start from the ordering case (keep for uncertainty
head if useful), proceed race-only; ambiguous => race-only and report. Write G1 verdict into findings
BEFORE building.

## Success bar (frozen before training, applied mechanically)
Per in-scope task: ordering head beats the fair linear pool (Model1) by >= the #374 gap's LOWER CI
bound (race_start >= +0.00810 pairwise-LL; race >= +0.00364 pairwise-LL), without degrading
calibration vs the correlated-fusion (#373) option. Antisymmetry-by-construction is a hard constraint.

## Scope realities discovered (investigation; bake into plan)
- Prior-stage order IS derivable offline (DB session_classifications at replay, as scorecard already
  opens the DB per event) AND in production (quali_pos / race_start_target_lap_positions).
- Race-pace deviation from prior order is a POST-EVENT label -> NOT an inference feature. Practice-pace
  evidence already lives inside the 4 module pi. So the deployable ordering conditioning set is
  [4 module Delta-pi, prior-stage-order position]; richer pace-deviation is offline-only/blocked.
- s_e / disagreement_rate are offline artifacts (params/spread_target/), NOT loaded at runtime;
  production wiring of the uncertainty head is heavier (loader + config slot) -> candidate for a
  follow-up if offline-justified, not necessarily wired this issue.
