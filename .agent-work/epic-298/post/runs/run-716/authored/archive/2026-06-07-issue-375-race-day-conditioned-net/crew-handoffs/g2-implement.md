# Implementer Handoff — G2 BUILD: conditioned net + offline measurement (issue #375)

You are a constellation-implementer. Worktree root (cd here):
`C:\Programs\f1Brainz\.claude\worktrees\agent-a2d028d13259581aa`. Windows; `py` not `python`;
`PYTHONIOENCODING=utf-8` in EVERY shell that captures subprocess output AND in child envs you spawn.
Branch `constellation/issue-375-race-day-conditioned-net` (worktree). Untracked files are real.

## Gate
g2 BUILD. Build the context-conditioned race-day fusion net (offline-first) and measure it under the
frozen #374 methodology. Honest-null is a VALID, COMPLETE outcome — do NOT manufacture a win.

## READ FIRST (load-bearing context)
1. `docs/evo/fusion_rework_findings.md` — the LAST section "# Issue #375 — G1 STOP-GATE verdict".
   THIS DRIVES YOUR WIN CRITERION. G1 proved: the #374 pairwise-LL interaction gain is
   CALIBRATION-shaped, not ordering-shaped. For BOTH race_start and race, the antisymmetric MLP
   (Model2b) on the 4 module Delta-pi is statistically FLAT vs the fair linear pool Model1 on ALL three
   ordering metrics (sign-acc/rank-MAE/Spearman; all CIs include 0). race_start is also flat vs grid
   persistence. The ONLY untested lever for genuine ORDERING gain is the PRIOR-STAGE-ORDER conditioning
   feature (absent from Model2b). Your net adds exactly that and tests whether it clears the bar.
2. `scripts/fusion_replay/g1_ordering_reconcile.py` — REUSE. `build_g1_dataset(records_dir, task)` already
   returns, per task: `X_delta` (n_pairs,4), `y`, `event_ids`, `seasons`, AND `persistence_logits`
   (= prior_pos_j − prior_pos_i per pair) + `persistence_valid`. The prior-stage-order conditioning
   feature you need is ALREADY computed there. Also reuse `_sign_acc_per_event`, `_secondary_metrics_3way`,
   `_bootstrap_delta_ci`, `run_g1_task` patterns.
3. `scripts/fusion_replay/metalearner.py` — REUSE the proven antisymmetric machinery: `_OddMLP`
   (forward = `g(x) - g(-x)`, logit odd in x), `_fit_mlp` (SCALE-ONLY normalisation — divide by std, NO
   mean centering; mean-centering breaks antisymmetry, see its docstring), `_predict_mlp`,
   `_loso_cv_linear` (Model1 fair ceiling), `_loso_cv_mlp`, `_pairwise_log_loss`,
   `_event_mean_of_means_gap`, `_bootstrap_gap_ci`.
4. `docs/evo/fusion_task_generalization.md` section "Inputs to the #375 conditioning design".
5. `.agent-work/issue-375-race-day-conditioned-net/evidence/investigation-findings-distilled.md` — scope realities.

## In-scope tasks (from G1)
Build and measure BOTH `race_start` and `race`. G1 did NOT clear either on ordering with the current
features; G2 tests whether the prior-stage-order feature changes that. Report per-task win/null.

## Records (ALREADY GENERATED + verified complete)
`.agent-work/issue-375-race-day-conditioned-net/records/` has all 64 race-day records (4 race_start +
4 race modules × 8 years 2018-2025). DO NOT regenerate. Use them via `build_g1_dataset`.

## Deliverable 1 — `src/evo_predictor/fusion_conditioned_net.py` (NEW production module)
A context-conditioned fusion net with TWO DISTINCT heads. Place under `src/evo_predictor/` per the arch
map (`docs/architecture/index.md` — net lives in evo, NOT latent_power). Keep functions < 100 lines
(simplification_limits IS enforced on src/).

**(A) ORDERING head — antisymmetric BY CONSTRUCTION (HARD constraint).**
- logit(x) = g(x) − g(−x), small MLP g (mirror `_OddMLP`; tanh; hidden ~24). NOT fixed product terms.
- Per-pair input x = concat([4 module Delta-pi], [prior_order_delta]) where
  `prior_order_delta = prior_pos_j − prior_pos_i` (this is ALREADY `persistence_logits` from
  `build_g1_dataset`; it is itself antisymmetric under i↔j swap, so it preserves the odd-function
  property). So in_dim = 5.
- Missingness: where `persistence_valid` is False (driver absent from prior-stage order, or tie), the
  prior_order_delta is NaN. You MUST handle this explicitly — DO NOT feed NaN to torch. Options (pick
  one, document it): (a) impute prior_order_delta=0 for invalid pairs AND add a binary
  "prior_order_missing" flag feature — BUT a raw 0/1 flag is NOT antisymmetric; if you add a missingness
  flag it must be symmetric (same for i,j swap) which BREAKS the odd construction unless you keep the
  flag OUT of the odd-MLP input and instead drop invalid-prior pairs from the ordering-head TRAIN/EVAL
  set. RECOMMENDED: train/eval the ordering head on prior-VALID pairs only (report the pair count and
  the dropped fraction), so every input dim is genuinely antisymmetric and the comparison to Model1 is
  on the same pair population. Document your choice; keep antisymmetry exact.
- Scale-only normalisation (divide by per-feature std, no mean centering) — REQUIRED to preserve
  antisymmetry through normalisation. Reuse the `_fit_mlp` approach.

**(B) UNCERTAINTY head — DISTINCT, ZERO ordering leverage (#408 component).**
- Targets the production spread-target convention: `params/spread_target/<year>/<round>/<phase>.json`
  (exchange-rate / s_e semantics). NOTE: spread_target artifacts exist for 2021-2025 ONLY (not
  2018-2020) — so the uncertainty head's offline measurement spans a NARROWER season set; state this and
  do LOSO over the available seasons only.
- It predicts a magnitude / spread, NOT an ordering. It must NOT influence the ordering head's logits.
  Keep the two heads in separate methods/params; a test must prove the ordering head output is
  unchanged by the uncertainty head.
- If wiring the uncertainty target loader is heavy (the investigation notes s_e/spread_target are
  offline artifacts not loaded at runtime), it is ACCEPTABLE to implement the uncertainty head's OFFLINE
  measurement against the spread_target files and DEFER production plumbing to a follow-up (the brief
  permits this). Production wiring is G3, default OFF. Do NOT block G2 on heavy uncertainty plumbing —
  the ordering head win/null is the primary G2 result.

## Deliverable 2 — offline train/eval harness in `scripts/fusion_replay/`
Extend or add a sibling script (e.g. `g2_conditioned_eval.py`). Reuse `build_g1_dataset` +
metalearner LOSO/bootstrap/seed machinery. Per in-scope task:
- LOSO over seasons (ordering head: 2018-2025; uncertainty head: spread_target seasons only).
- Comparators: Model1 (fair linear pool, the ceiling), Model2b (4-module OddMLP, the G1 baseline), and
  ConditionedNet (your 5-input ordering head). All on the SAME prior-valid pair population for an
  apples-to-apples Model1 vs ConditionedNet comparison.
- Metrics: pairwise-LL gap vs Model1 AND ordering metrics (sign-acc, rank-MAE, Spearman) vs Model1, with
  event-cluster bootstrap 95% CIs (B=1000, seed=0) and >=3-seed stability.
- Calibration: also report calibration (e.g. reliability / coverage) vs the correlated-fusion (#373)
  option so the bar's "without degrading calibration" clause is checkable. If #373 correlated fusion is
  not readily invocable offline here, report the ConditionedNet's own calibration (reliability curve /
  ECE-like) and note the #373 comparison as a G3/follow-up — do not block.

## FROZEN SUCCESS BAR — apply MECHANICALLY (do not move it)
Per in-scope task, the ordering head is a WIN iff BOTH:
1. **Ordering gain (G1's lens, the decisive test):** ConditionedNet beats Model1 on pairwise SIGN-ACCURACY
   with the event-cluster bootstrap 95% CI EXCLUDING 0 (and Spearman delta vs Model1 CI excluding 0 as
   corroboration). This is the honest ordering test — G1 showed a pairwise-LL gain ALONE can be pure
   calibration, so an LL win without an ordering win is a NULL for the ordering head.
2. **Pairwise-LL bar (continuity with #374):** ConditionedNet beats Model1 by >= the #374 lower CI bound
   (race_start >= +0.00810, race >= +0.00364 pairwise-LL) WITHOUT degrading calibration vs the
   correlated-fusion option.
If criterion 1 fails (ordering CI includes 0) the task is a NULL even if criterion 2 passes — report it
plainly as calibration-shaped, consistent with G1. Honest-null is complete and acceptable. State the
per-task WIN or NULL call explicitly with the numbers.

## Deliverable 3 — unit tests (`tests/unit/evo_predictor/test_fusion_conditioned_net.py`)
- **Antisymmetry invariant (exact):** for random x, `logit(net, -x) == -logit(net, x)` to float tolerance
  (e.g. atol=1e-5), BEFORE and AFTER fit, including through the scale-only normalisation.
- **Head separation:** mutating/disabling the uncertainty head leaves ordering-head logits bit-identical.
- **Shape/contract:** in_dim=5, batch in → (n,) logits out; uncertainty head returns a spread/magnitude.
- **Missingness handling:** invalid-prior pairs are dropped (or imputed-per-your-choice) deterministically;
  no NaN reaches torch.
Keep tests fast and hermetic (synthetic tensors; no DB/records/network).

## Allowed Scope
- NEW `src/evo_predictor/fusion_conditioned_net.py`.
- `scripts/fusion_replay/` (new `g2_conditioned_eval.py` and/or extend; you MAY import from
  `g1_ordering_reconcile.py` and `metalearner.py`).
- NEW `tests/unit/evo_predictor/test_fusion_conditioned_net.py` (and eval-harness tests if useful).
- Evidence dir. You MAY append a short G2 results subsection to `docs/evo/fusion_rework_findings.md`
  (or leave the full write-up for G3 — your call; at minimum dump JSON+table to evidence).

## Specific Exclusions
- NO `sampled_runtime.py` edits in G2 (production wiring is G3).
- DO NOT touch `quali_pace_anchor.py`, its config keys, §7.6.4, or `prediction_ceiling_and_priorities.md`.
- DO NOT regenerate records. DO NOT add quali. DO NOT modify `g1_ordering_reconcile.py` analysis
  behavior (import from it; extraction-only refactor allowed if behavior-identical + re-verified).

## Constraints
- DB read-only, canonical, absolute `C:/Programs/f1Brainz/data/f1_data_{year}.db`. No FastF1. Explicit
  missingness (never silent-impute without a documented, antisymmetry-safe choice).
- Frozen #374 methodology (LOSO; event-cluster bootstrap B=1000 seed=0; >=3 seeds for stability).
- Antisymmetry-by-construction is a HARD constraint. Ordering & uncertainty heads MUST be distinct;
  uncertainty head has zero ordering leverage.
- `py -m src.utils.simplification_limits --paths <touched src/ and tests/ paths>` must pass (src/ and
  tests/ ARE enforced; scripts/ is NOT scanned by default roots, but keep it reasonable).
- prefer torch (2.10 CPU installed); sklearn ABSENT; `py -m pip install` only if genuinely needed and
  LOG it in your result.
- Tunable hyperparameters (hidden, epochs, lr) in named constants, not inline magic.

## Required Evidence (paste into IMPLEMENTER_RESULT)
- `g2_conditioned_eval.{json,txt}` in evidence dir: per task, Model1 vs Model2b vs ConditionedNet on
  pairwise-LL gap + ordering metrics (sign-acc/rank-MAE/Spearman) vs Model1, with CIs + seed spread +
  calibration, + the prior-valid pair counts/dropped fraction.
- `PYTHONIOENCODING=utf-8 py -m pytest tests/unit/evo_predictor/test_fusion_conditioned_net.py -q` GREEN.
- `PYTHONIOENCODING=utf-8 py -m pytest tests/unit/evo_predictor/ -k "fusion or replay or metalearner or record or sampled_runtime" -q` GREEN (no regressions).
- `PYTHONIOENCODING=utf-8 py -m src.utils.simplification_limits --paths <touched src/tests paths>` output.
- Sanity: Model1 LOSO pairwise-LL reproduces ~0.336 (race_start) / ~0.477 (race) on the prior-valid
  population (fair-ceiling check; will differ slightly from full-population due to dropped pairs — note it).
- The explicit per-task WIN/NULL call with numbers.

## Suggested Model Tier
stronger — net design + antisymmetry rigor + statistical measurement + an honest win/null call.

## Authority
You decide: net architecture details (hidden size/epochs/lr within reason), the missingness handling for
the prior-order feature (document it; keep antisymmetry exact), and whether to defer heavy uncertainty
production plumbing (offline measurement is the G2 requirement). You do NOT move the success bar and you
do NOT decide overall #375 closure (that is G3 + the user). Report the mechanical win/null per task.

## Stop Conditions
STOP and report if: antisymmetry cannot be preserved with the chosen feature encoding (do not ship a
non-antisymmetric ordering head); a required artifact (records/spread_target/DB accessor) is missing or
errors; you would need to touch an excluded file; the success bar is genuinely ambiguous to apply
(report the ambiguity, don't guess the verdict). A clean NULL is NOT a stop condition — it is a result.

## Return Format
IMPLEMENTER_RESULT: files changed; net architecture + missingness choice; per-task numbers (Model1 vs
Model2b vs ConditionedNet: pairwise-LL gap + ordering metrics vs Model1, CIs, seed spread, calibration);
the per-task WIN/NULL call applying the frozen bar mechanically; uncertainty-head status (measured /
deferred-plumbing); all required evidence outputs; pip installs (if any); assumptions; stop conditions
hit; out-of-scope observations.
