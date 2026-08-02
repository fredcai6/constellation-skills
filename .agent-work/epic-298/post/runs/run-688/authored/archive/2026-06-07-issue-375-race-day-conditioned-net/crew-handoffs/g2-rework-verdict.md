# Implementer Handoff — G2 REWORK: correct the win/null verdict logic (issue #375)

You are a constellation-implementer. Worktree root (cd here):
`C:\Programs\f1Brainz\.claude\worktrees\agent-a2d028d13259581aa`. Windows; `py` not `python`;
`PYTHONIOENCODING=utf-8` in every shell that captures subprocess output AND child envs. Branch
`constellation/issue-375-race-day-conditioned-net` (worktree). Untracked files are real.

## Gate
g2 REWORK. The independent reviewer issued a BLOCK with a precise, narrow fix. The net architecture,
antisymmetry, head separation, and tests all PASSED review. The ONE problem: the eval script's WIN/NULL
logic applied only the pairwise-LL bar and declared WIN, but the FROZEN two-part success bar requires an
ORDERING criterion that the gain does NOT meet. The correct verdict is NULL (calibration-shaped). Your
job: make the eval compute and apply the full two-part criterion, regenerate the evidence, and correct
every place that claims WIN to NULL.

## The correct two-part win criterion (frozen; from g2-implement.md)
A task is a WIN iff BOTH:
1. **Ordering (decisive):** ConditionedNet beats Model1 on pairwise SIGN-ACCURACY with event-cluster
   bootstrap 95% CI EXCLUDING 0, corroborated by SPEARMAN delta vs Model1 CI EXCLUDING 0.
2. **Pairwise-LL bar:** gap ≥ #374 lower bound (race ≥ +0.00364) AND its CI lower > 0.
If criterion 1 fails (ordering CI includes 0), the task is NULL even if criterion 2 passes.

The reviewer's independently re-derived race numbers (B=1000, seed=0, 173 events, 30149 pairs):
- Pairwise-LL gap +0.00497, CI [+0.00203,+0.00775] → criterion 2 PASSES.
- Sign-acc delta vs Model1 +0.00140, CI [−0.00093,+0.00388] → INCLUDES 0 → criterion 1 FAILS.
- Spearman delta vs Model1 +0.00008, CI [−0.00263,+0.00304] → INCLUDES 0 → criterion 1 FAILS.
- => CORRECT VERDICT: **NULL (calibration-shaped)**.
Your regenerated numbers should match these closely (same seed/methodology).

## Task
1. **Fix `run_g2_task` (and any verdict helper) in `scripts/fusion_replay/g2_conditioned_net.py`** to
   compute, for each task, the ConditionedNet-vs-Model1 deltas WITH event-cluster bootstrap 95% CIs
   (B, seed) for BOTH pairwise SIGN-ACCURACY and SPEARMAN. REUSE the already-built helpers — import from
   `scripts.fusion_replay.g1_ordering_reconcile`: `_sign_acc_per_event`, `_bootstrap_delta_ci`, and
   `_secondary_metrics_3way` (or its per-event Spearman arrays); and from `metalearner` as needed. You
   already have the Model1 and ConditionedNet held-out LOSO logits in the eval — feed them to these
   helpers (same pair population; race has 0 dropped pairs).
2. **Set `win_null` via the full two-part criterion.** Add the ordering-CI fields to the result dict and
   the printed table:
   - `delta_sign_acc_g2_vs_m1` + `..._ci95`
   - `delta_spearman_g2_vs_m1` + `..._ci95`
   - `win_null_criteria` string updated to state BOTH parts.
   - `win_null` = "WIN" iff (sign-acc CI lo > 0 AND spearman CI lo > 0 AND gap ≥ bar AND gap CI lo > 0),
     else "NULL". For race this resolves to NULL.
3. **Regenerate the evidence** by re-running the eval; overwrite
   `.agent-work/issue-375-race-day-conditioned-net/evidence/g2_conditioned_net.{json,txt}` and the run
   log. Confirm the JSON now records `"win_null": "NULL"` with the ordering CIs.
4. **Add/extend a unit test** in `tests/unit/evo_predictor/test_fusion_conditioned_net.py` (or the eval's
   test if one exists) for the verdict function: feed synthetic stats where (a) all criteria pass → WIN,
   (b) LL passes but ordering CI includes 0 → NULL, (c) ordering passes but LL below bar → NULL. This
   locks the two-part rule so it cannot silently regress.
5. **Correct the prose** in the run log / IMPLEMENTER_RESULT to state NULL (calibration-shaped). Do NOT
   write the final findings section — that is G3 (the commander composes the verdict doc). If you added a
   G2 subsection to `docs/evo/fusion_rework_findings.md`, correct any WIN claim there to NULL; otherwise
   leave the findings doc to G3.

## Allowed Scope
- `scripts/fusion_replay/g2_conditioned_net.py` (verdict logic + ordering CIs).
- `tests/unit/evo_predictor/test_fusion_conditioned_net.py` (verdict-rule tests).
- Evidence dir (regenerate).
- `docs/evo/fusion_rework_findings.md` ONLY to correct a WIN→NULL claim if you previously added one.

## Specific Exclusions
- Do NOT change `src/evo_predictor/fusion_conditioned_net.py` (the net passed review — leave it).
- Do NOT change the net architecture, the success-bar VALUES, or the methodology.
- Do NOT touch `sampled_runtime.py`, `quali_pace_anchor.py` + keys, `prediction_ceiling_and_priorities.md`.
- Do NOT regenerate records. Do NOT add quali. Do NOT modify `g1_ordering_reconcile.py` behavior
  (import-only).

## Constraints
- Frozen #374 methodology (LOSO; event-cluster bootstrap B=1000 seed=0; ≥3-seed stability already present).
- `py -m src.utils.simplification_limits --paths <touched src/tests>` must pass.
- Honest-null is the CORRECT, COMPLETE outcome — do NOT try to engineer a WIN. Report NULL plainly.

## Required Evidence (paste into IMPLEMENTER_RESULT)
- Regenerated `g2_conditioned_net.json` excerpt showing `"win_null": "NULL"` + the sign-acc and Spearman
  deltas vs Model1 with CIs.
- `PYTHONIOENCODING=utf-8 py -m pytest tests/unit/evo_predictor/test_fusion_conditioned_net.py -q` GREEN.
- `PYTHONIOENCODING=utf-8 py -m pytest tests/unit/evo_predictor/ -k "fusion or replay or metalearner or record or sampled_runtime" -q` GREEN.
- `PYTHONIOENCODING=utf-8 py -m src.utils.simplification_limits --paths <touched paths>` output.

## Suggested Model Tier
standard — narrow, well-specified fix using existing helpers.

## Authority
You implement the two-part criterion exactly as specified and report the resulting NULL. You do NOT move
the bar or the methodology. You do NOT decide #375 closure (G3 + commander + user).

## Stop Conditions
Stop and report if: importing the g1 helpers creates a cycle or behavior change; the regenerated numbers
materially disagree with the reviewer's (e.g. an ordering CI actually EXCLUDES 0 → report it, the verdict
might flip to WIN); you would need to touch an excluded file.

## Return Format
IMPLEMENTER_RESULT: files changed, the regenerated race numbers (LL gap + sign-acc + Spearman vs Model1,
all with CIs), the corrected win_null=NULL, the verdict-rule test cases, all required evidence outputs,
assumptions, stop conditions hit, out-of-scope observations.
