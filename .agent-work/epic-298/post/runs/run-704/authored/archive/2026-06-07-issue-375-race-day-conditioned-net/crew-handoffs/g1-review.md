# Reviewer Handoff — G1 STOP-GATE (issue #375)

You are a constellation-reviewer. INDEPENDENT verification: RE-DERIVE the key numbers yourself; do not
trust the implementer's reported figures. Repo root: C:\Programs\f1Brainz. Windows; `py` not `python`;
`PYTHONIOENCODING=utf-8` in shells that capture subprocess output. Branch
`constellation/issue-375-race-day-conditioned-net` (worktree).

## Gate
g1 — STOP-GATE. The verdict here fixes #375's ordering scope, so correctness is load-bearing.

## What Was Implemented
An offline G1 reconciliation: a grid/lap-3 PERSISTENCE ordering baseline + an ordering-metric
translation (pairwise sign-accuracy, rank MAE, Spearman) comparing {persistence, Model1 linear pool,
Model2b antisymmetric MLP} for tasks {race_start, race}, under LOSO + event-cluster bootstrap, plus a
G1 verdict section appended to `docs/evo/fusion_rework_findings.md` stating the ordering-scope decision.

## How to Inspect the Diff
```
git -C C:/Programs/f1Brainz/.claude/worktrees/agent-a2d028d13259581aa diff --stat HEAD
git -C C:/Programs/f1Brainz/.claude/worktrees/agent-a2d028d13259581aa diff HEAD -- scripts/fusion_replay/ docs/evo/fusion_rework_findings.md tests/
```
(Implementer may not have committed; also inspect the working tree. Evidence at
`.agent-work/issue-375-race-day-conditioned-net/evidence/g1_ordering_reconcile.{json,txt}`.)

## Task Statement
See `.agent-work/issue-375-race-day-conditioned-net/crew-handoffs/g1-implement.md`. The gate must
answer, in ORDERING metrics: does race_start's #374 interaction gain represent real ordering
improvement beyond grid persistence, or is it confidence-shaped? And fix the in-scope ordering set.

## Close Criteria (each becomes a review check; RE-DERIVE where numeric)
1. **Fair-ceiling sanity reproduces.** Independently run the metalearner (or the implementer's script)
   on the records and confirm Model1 LOSO pairwise-LL ~= 0.33702 (race_start) and ~= 0.47799 (race),
   matching #374. If these drift materially, the linear ceiling is not fair -> BLOCK.
2. **Persistence baseline is legitimate.** Verify prior-stage order is sourced correctly: quali order
   via `get_session_classification(year, round, 'Q')` for race_start; lap-3 via
   `get_race_start_order(year, round, expected_target_lap=3)` for race. Verify the sign prediction is
   `prior_pos_i < prior_pos_j => i ahead`. Spot-check ONE event by hand from the DB and confirm the
   baseline's pairwise calls. Verify missingness is explicit (drops counted, not silently imputed).
   Cross-check the persistence sign-accuracy against the #377/ceiling persistence numbers (grid->lap3
   ~0.875 for race_start, lap3->finish ~0.776 for race) — the race_start persistence sign-accuracy on
   THIS pair population should be in that neighbourhood; a wildly different value signals a bug.
3. **Sign-accuracy metric is correct & antisymmetry-safe.** Confirm it is fraction of held-out pairs
   with sign(prediction)==winner, floor 0.5, computed on the i<j one-sided pairs (consistent with the
   harness). Confirm Model2b's logit antisymmetry is preserved (the OddMLP construction).
4. **CIs and seed-stability present and sound.** Event-cluster bootstrap (B=1000, seed=0) on the key
   deltas (Model2b-Model1 and Model2b-persistence, for sign-acc/rank MAE/Spearman). Seed spread across
   >=3 seeds reported; the verdict must not rest on a seed-fragile margin.
5. **Verdict follows mechanically.** The scope decision in the findings section must follow the
   stated mechanical rule from the numbers (Model2b vs persistence AND vs Model1 on sign-accuracy, CI
   excludes 0 -> in scope; flat/CI-includes-0 -> confidence-shaped, drop from ordering; ambiguous ->
   race-only). Verify the conclusion matches the evidence; flag any overclaim.
6. **Tests green** and **no excluded files touched** (no src/evo_predictor production code, no
   sampled_runtime, no quali anchor / ceiling doc edits, full set not regenerated).

## Allowed Scope (what the implementation was permitted to touch)
`scripts/fusion_replay/` (metalearner extend or new g1 script), `docs/evo/fusion_rework_findings.md`
(append), new `tests/unit/evo_predictor/`, the work-area evidence dir. NOTHING in `src/evo_predictor/`.

## Specific Exclusions (flag if touched)
`src/evo_predictor/*` production code, `sampled_runtime.py`, `quali_pace_anchor.py` + its config keys,
`docs/evo/prediction_ceiling_and_priorities.md`.

## Constraints the Implementation Must Respect
- DB read-only, canonical, absolute path; no FastF1; explicit missingness.
- Frozen #374 methodology (LOSO 2018-2025; event-cluster bootstrap B=1000 seed=0).
- Simplification limits pass on touched src/tests paths.

## Evidence Produced
`g1_ordering_reconcile.{json,txt}`; the new findings section; pytest output. (Verify each; re-run the
test command yourself.)

## Suggested Model Tier
stronger — statistical re-derivation.

## Stop Conditions
BLOCK if: a headline number cannot be reproduced (Model1 ceiling, persistence sign-accuracy, or the
Model2b deltas); the persistence baseline is mis-sourced; missingness is silently imputed; the verdict
overclaims beyond the CIs; an excluded file was touched; or tests fail.

## Commander focus points (scrutinize these specifically)
1. **Tests.** The implementer did NOT add unit tests, claiming "evidence-only gate." But it added a NEW
   persistence baseline AND a NEW sign-accuracy metric in `scripts/fusion_replay/g1_ordering_reconcile.py`.
   The implement handoff listed tests as in-scope (persistence correctness on a tiny synthetic event,
   sign-accuracy metric correctness, missingness-drop counting). Decide whether the absence of tests for
   load-bearing new logic is a BLOCK. At minimum, re-derive the persistence sign-accuracy and the
   sign-acc metric on a hand-built tiny example to confirm correctness yourself.
2. **Scope-claim tension (load-bearing).** The verdict says "ordering head = race-only," but the
   implementer's own race numbers show Model2b is FLAT vs Model1 on ALL three ordering metrics (sign-acc
   delta -0.00037, Spearman -0.00024, rank MAE +0.00018 — all CIs include 0). The brief's mechanical
   rule requires Model2b to beat BOTH persistence AND Model1 on sign-accuracy (CI excluding 0) to keep a
   task in the ordering scope. Race beats persistence but is FLAT vs Model1. Confirm: does "race-only"
   overclaim? The honest reading is that the CURRENT Model2b (4 module Delta-pi only) does NOT clear the
   bar for either task; race only stays alive IF G2's prior-stage-order conditioning (absent from
   Model2b) adds ordering over Model1. Verify the findings section states this conditional honestly and
   does not imply race already clears the G2 success bar. Flag any overclaim.
3. Run `PYTHONIOENCODING=utf-8 py -m src.utils.simplification_limits scripts/fusion_replay/g1_ordering_reconcile.py`
   (or per TESTING.md if scripts/ is exempt) and report.

## Return Format
REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings WITH your independently re-derived numbers
(state the values you computed), blockers, out-of-scope observations. Explicitly address the two
commander focus points above.
