# Reviewer Handoff — G3: scorecard runner + measurement + ordering-vs-calibration verdict

You are a fresh, INDEPENDENT reviewer crew. You did NOT write this code or the findings. Work ONLY
from this handoff. Repo: f1Brainz (Windows; `py` not `python`). Branch
`constellation/issue-373-correlated-fusion`; cwd = worktree root
(`C:\Programs\f1Brainz\.claude\worktrees\agent-a8cafc9a5b22bcd57`). Set `PYTHONIOENCODING=utf-8`
before EVERY python command (records/logs contain non-ASCII; cp1252 will crash). Your job is to
VERIFY, not to fix. Re-run everything yourself.

## What G3 produced (the deliverable the epic #372 gate depends on)
The measurement: **does correctly handling cross-module redundancy (a correlated-covariance fusion
update) move ORDERING, or only CALIBRATION?** Plus the runner that computes it and the written
verdict.

Artifacts to inspect:
- `scripts/fusion_replay/scorecard.py` — the runner (loads real per-event module records, canonical
  join on year:round:gp, estimates R per task, scores baseline / A / cheap-B / ablations).
- `tests/unit/evo_predictor/test_fusion_scorecard.py` — its unit tests (synthetic).
- `.agent-work/issue-373-correlated-fusion/evidence/scorecard.json` — the produced scorecard.
- `docs/evo/fusion_rework_findings.md` — the findings doc + VERDICT (this is the headline output).
- Records already generated at `.agent-work/issue-373-correlated-fusion/records/` (96 files, 12
  modules × 2018-2025).

## The claimed verdict (verify it follows from the numbers)
"Modelling the cross-module error correlation R moves CALIBRATION, not ORDERING." The key argument
is a DECOMPOSITION using the R=I ablation: A's effect splits into (1) a per-entity *reformulation*
(baseline → R=I) and (2) the *correlation* (R=I → A); only (2) is what #373 tests, and (2) is
flat-to-negative on ordering (rank MAE / Spearman) but positive on calibration (coverage, pairwise-LL).

## Review checklist — VERIFY EACH (PASS/FAIL with evidence)

1. **Tests pass and are meaningful.** Run:
   `py -m pytest tests/unit/evo_predictor/test_fusion_scorecard.py -q` and
   `py -m pytest tests/unit/evo_predictor/ -k "fusion or record or replay or scorecard" -q`.
   Read the scorecard tests — confirm the normaliser test and the driver-drop test actually assert
   behaviour (not tautologies).

2. **Scorecard reproduces.** Run the runner yourself:
   `py -m scripts.fusion_replay.scorecard --records-dir .agent-work/issue-373-correlated-fusion/records --out /tmp/scorecard_review.json`
   Confirm: all 3 tasks score **173/173 events**; the printed baseline/A/cheap-B numbers MATCH the
   findings doc table (to rounding); `ablation_RI == A_lambda100` (both R=I) to ~0.
   Then diff your /tmp/scorecard_review.json against the committed scorecard.json (numbers should
   match). NOTE the runner uses real DB at C:/Programs/f1Brainz/data (read-only).

3. **The decomposition is correct.** From the scorecard JSON (or by reading the runner), recompute
   for at least one task: Δreform = (R=I − baseline) and Δcorr = (A − R=I) for rank MAE, Spearman,
   cov80. Confirm the findings-doc decomposition table is arithmetically right and that Δcorr on
   ordering (rank MAE, Spearman) is indeed flat-to-negative on ALL three tasks, while Δcorr on
   calibration (cov80, pairwise-LL) is positive. THE VERDICT HINGES ON THIS — check it hard.

4. **R estimation is sound + redundancy premise confirmed.** Confirm the estimated R off-diagonals
   are in the 0.71-0.89 range (high), constructor↔driver same-evidence blocks are the highest, and
   condition numbers shrink under λ. Confirm R is estimated in standardized-residual space
   (residual = module_π − target_μ) over the joined events (read `_run_task` / `_compute_event_residuals`).

5. **cheap-B corroborates.** Confirm cheap-B (correlation only in the constructor↔driver block)
   shows the same pattern (ordering flat-to-worse, calibration slightly better) — i.e. the verdict
   is not an artefact of estimating a full 4×4 R.

6. **Coverage / missingness stated honestly.** Confirm the findings doc does NOT overclaim:
   it must state (a) 173/173 events, 2018-2025; (b) absolute coverage is LOW under the fixed
   unit-scale config (under-dispersed posteriors) and the measurement isolates the DIRECTION of R's
   effect; (c) the per-event driver drops (esp. race_start ~284) are explicit, counted, not imputed;
   (d) the constructor-name normaliser is collision-guarded. Confirm the scorecard JSON's miss_counts
   back the doc's claims.

7. **No production behaviour change; scope respected.** Confirm scorecard.py imports but does NOT
   modify production fusion; `git diff` shows no edits to fusion.py / _correlation.py / variants.py /
   records.py / scoring.py / baseline.py beyond what G1/G2 committed. Confirm the doc does NOT drift
   into #374 interaction-modelling territory (it should explicitly defer ordering headroom to #374).
   Confirm `docs/evo/prediction_ceiling_and_priorities.md` is NOT touched.

8. **Simplification.** Run
   `py -m src.utils.simplification_limits --paths scripts/fusion_replay/scorecard.py tests/unit/evo_predictor/test_fusion_scorecard.py`
   — must PASS.

## Commands to RUN (paste tails into your result)
```
py -m pytest tests/unit/evo_predictor/test_fusion_scorecard.py -q
py -m pytest tests/unit/evo_predictor/ -k "fusion or record or replay or scorecard" -q
py -m scripts.fusion_replay.scorecard --records-dir .agent-work/issue-373-correlated-fusion/records --out /tmp/scorecard_review.json
py -m src.utils.simplification_limits --paths scripts/fusion_replay/scorecard.py tests/unit/evo_predictor/test_fusion_scorecard.py
```

## Close criteria for APPROVE
All 8 items PASS; scorecard reproduces to 173/173 with matching numbers; the decomposition is
arithmetically correct and supports "calibration not ordering"; the doc is honest about coverage and
scope and does not overclaim.

## Out of scope (note, do not block)
- Re-running under trained covariance scales (noted follow-up in the doc).
- Absolute coverage magnitude (expected low under unit scales).
- #374 interaction modelling.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK); per-checklist PASS/FAIL with specific evidence
(your recomputed Δreform/Δcorr for at least one task, command tails, the events_scored you observed);
any overclaim or arithmetic error found; out-of-scope observations. If BLOCK, the precise minimal fix.
