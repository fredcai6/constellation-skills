# Implementer Handoff — G1 STOP-GATE (issue #375)

Concise. You are a constellation-implementer. Repo root: C:\Programs\f1Brainz. Windows; `py` not
`python`; set `PYTHONIOENCODING=utf-8` in every shell that captures subprocess output AND in child
envs. You are in a git worktree on branch `constellation/issue-375-race-day-conditioned-net`. Only
worktree-local files exist; untracked files are real.

## Gate
g1 (STOP-GATE). NO production net code in this gate. Offline measurement + a written verdict only.

## Task
Reconcile race_start's measured +1.23pp pairwise-LL interaction gain (#374) against the grid->lap3
0.875 persistence ceiling, expressed in ORDERING metrics, for BOTH downstream tasks {race_start, race}.
Produce the G1 verdict that fixes #375's ordering scope.

## Background you must read first (do not skip)
- `docs/evo/fusion_rework_findings.md` — the #374 gate section (your baselines: Model1 LOSO pairwise-LL
  race_start ~0.33702, race ~0.47799; Model2b gaps race_start +0.01230 [+0.00810,+0.01683], race
  +0.00624 [+0.00364,+0.00892]). You build a NEW section at the END of this file.
- `scripts/fusion_replay/metalearner.py` — REUSE this. It already has: `build_pairwise_dataset` (per
  task, 4 module Delta-pi + dev_delta + y + event_ids + seasons), `_loso_cv_linear` (Model1),
  `_loso_cv_mlp` (Model2b OddMLP), `_event_mean_of_means_gap`, `_bootstrap_gap_ci` (event-cluster
  bootstrap), and `_secondary_metrics` (per-event rank MAE + Spearman for Model1 vs best Model2 via
  win-sum reconstruction). Do NOT reinvent LOSO/bootstrap/MLP.
- `scripts/fusion_replay/scorecard.py` — `_preprocess_events` opens the DB per event
  (`_get_constructor_by_driver` -> `DatabaseManager(db_path).get_race_driver_teams`). You will add an
  analogous per-event prior-stage-order lookup using the SAME `db_cache` pattern.
- `.agent-work/issue-375-race-day-conditioned-net/evidence/investigation-findings-distilled.md` — scope
  realities.

## Records are ALREADY GENERATED AND VERIFIED COMPLETE (do not regenerate)
Records for {race_start, race}, years 2018-2025, are in
`.agent-work/issue-375-race-day-conditioned-net/records/`. The commander verified on
2026-06-07 that all 8 in-scope modules (4 race_start + 4 race) x 8 years (2018-2025) are
present: exactly 32 `*race_start*.record.npz` + 32 `*_race_power*.record.npz` = 64 records,
each with matching `.record.json`. Coverage is COMPLETE — do NOT regenerate. (Quali records
also exist for 2024 only; ignore them — quali is out of scope.) If you nonetheless find a
missing in-scope module-year, STOP and report it (do not regenerate; the commander owns
generation).

## Deliverables
1. **Persistence ordering baseline.** Build a third comparator alongside Model1 and Model2b: for each
   event, the PRIOR-STAGE ORDER as a pi-like score (lower position = higher rank). Prior-stage order
   from the DB (read-only, absolute path `C:/Programs/f1Brainz/data/f1_data_{year}.db`):
   - **race_start prior stage = quali/grid order:** `DatabaseManager(db_path).get_session_classification(year, round_num, 'Q')` -> `{driver_id: quali_position}`. Drivers absent from the dict have no quali classification — represent missingness explicitly (drop from the persistence comparison for that pair, or substitute the field-size+1 sentinel; pick one, document it, count drops). DO NOT silently impute.
   - **race prior stage = lap-3 order:** `DatabaseManager(db_path).get_race_start_order(year, round_num, expected_target_lap=3)` -> `{driver_id: lap3_running_position}`. Same missingness handling.
   Convert position to a pairwise sign prediction: for pair (i,j), predict i ahead of j iff
   prior_pos_i < prior_pos_j. This is the persistence baseline's ordering call (it has no probability;
   for log-loss treat it as a hard 0/1 or a fixed-margin logit — for SIGN-ACCURACY it is just the sign;
   report sign-accuracy + rank MAE + spearman for persistence, and note pairwise-LL is not its native
   metric).
2. **Ordering-metric translation.** For BOTH race_start and race, under the SAME LOSO + event-cluster
   bootstrap as #374, report these ORDERING metrics for the three comparators {persistence, Model1,
   Model2b}:
   - **pairwise SIGN-ACCURACY** (fraction of held-out pairs where the predicted sign matches the
     winner; this is NEW — add it; floor 0.5). For Model1/Model2b, sign = sign(held-out logit).
   - **rank MAE** and **Spearman** (per-event, equal weight per event) — `_secondary_metrics` already
     does this for Model1 vs best-Model2; extend it to also score the persistence baseline.
   - Also carry the existing pairwise-LL gap (Model1 vs Model2b) for continuity with #374.
   - Provide event-cluster bootstrap 95% CIs (B=1000, seed=0) for the KEY deltas:
     Model2b - Model1 (sign-acc, rank MAE, spearman) AND Model2b - persistence (same three).
   - Seed-stability: re-run the MLP LOSO for >=3 seeds (e.g. 0,1,2) and report the spread of the
     Model2b sign-accuracy / pairwise-LL gap across seeds (so the verdict is not seed-fragile).
3. **Run + capture.** Add a CLI entry (extend metalearner CLI or a small sibling script in
   `scripts/fusion_replay/`, e.g. `g1_ordering_reconcile.py`) restricted to {race_start, race}. Run it
   against the records dir; write JSON + a human-readable table to
   `.agent-work/issue-375-race-day-conditioned-net/evidence/g1_ordering_reconcile.{json,txt}`.
4. **G1 VERDICT in `docs/evo/fusion_rework_findings.md`** (NEW section at end, titled e.g.
   "# Issue #375 G1 - race_start ordering reconciliation (stop-gate)"). State, with the numbers:
   - Does race_start show REAL ordering improvement (Model2b) BEYOND grid persistence, or is the
     interaction gain confidence/calibration-shaped (sign-accuracy & rank ordering ~flat vs
     persistence and vs Model1)?
   - Same read for race.
   - The resulting SCOPE DECISION, applying this rule mechanically:
     * Model2b beats BOTH Model1 AND persistence on sign-accuracy with CI excluding 0 -> task stays in
       the ORDERING scope.
     * Model2b's ordering edge over persistence is ~flat (CI includes 0) though pairwise-LL improved ->
       the gain is confidence-shaped; DROP that task from the ordering case (note it may still serve the
       uncertainty head).
     * Ambiguous -> keep race only, report.
   - Conclude with the explicit in-scope set for the net's ORDERING head (one of: {race_start, race} /
     {race} / {race} with race_start flagged ambiguous).
   ALL THREE outcomes are acceptable and complete. Report mechanically; do not manufacture signal.

## Allowed Scope
- `scripts/fusion_replay/metalearner.py` (extend), and/or a NEW `scripts/fusion_replay/g1_*.py`.
- `docs/evo/fusion_rework_findings.md` (append new section).
- New tests under `tests/unit/evo_predictor/` (e.g. `test_g1_ordering_reconcile.py`): persistence
  baseline correctness on a tiny synthetic event; sign-accuracy metric correctness; missingness drop
  counting.
- The work-area evidence/ dir.

## Specific Exclusions
- NO `src/evo_predictor/` production code. NO net module. NO `sampled_runtime.py` edits.
- DO NOT touch `quali_pace_anchor.py`, its config keys, or `docs/evo/prediction_ceiling_and_priorities.md`.
- DO NOT regenerate the full record set. DO NOT add quali to the analysis (out of scope).

## Constraints
- DB is canonical, READ-ONLY, absolute path. No FastF1. Missingness explicit (never silent-impute).
- Frozen #374 methodology: LOSO over seasons 2018-2025, event-cluster bootstrap B=1000 seed=0.
- `py -m src.utils.simplification_limits` on touched src/ + tests/ paths must pass (scripts/ may be
  exempt — check TESTING.md; if scripts/ is checked, keep functions within limits).
- Tunable thresholds/weights in named constants, not inline magic.

## Required Evidence
- `g1_ordering_reconcile.{json,txt}` with the three-comparator ordering metrics + CIs + seed spread.
- The new findings section (paste its text into your IMPLEMENTER_RESULT).
- Test output: `py -m pytest tests/unit/evo_predictor/ -k "fusion or replay or metalearner or record or sampled_runtime" -q` GREEN.
- Sanity in your result: confirm Model1 LOSO pairwise-LL reproduces ~0.33702 (race_start) / ~0.47799
  (race) — the fair-ceiling check.

## Verification Commands
```
PYTHONIOENCODING=utf-8 py -m pytest tests/unit/evo_predictor/ -k "fusion or replay or metalearner or record or sampled_runtime" -q
PYTHONIOENCODING=utf-8 py -m src.utils.simplification_limits <touched paths>
```

## Suggested Model Tier
stronger — measurement design + statistical care + a load-bearing verdict.

## Authority
Scope is fixed by the brief + this handoff. You DECIDE the missingness representation for the
persistence baseline (drop vs sentinel) — document it. You do NOT decide #375's overall win/null (that
is G2) — G1 only decides the ORDERING-SCOPE set via the mechanical rule above. If the records dir is
incomplete or a DB accessor errors, STOP and report (do not work around with FastF1 or imputation).

## Stop Conditions
Stop and return if: records dir lacks the 64 race-day records and you cannot proceed; a DB accessor is
missing/errors; you would need to touch an excluded file; the mechanical scope rule is genuinely
ambiguous (report the ambiguity rather than guessing the verdict).

## Return Format
IMPLEMENTER_RESULT: completed deliverables, files changed, the three-comparator ordering numbers (with
CIs + seed spread) for race_start AND race, the G1 scope decision + the new findings section text, test
output, missingness decision, assumptions, stop conditions hit, out-of-scope observations.
