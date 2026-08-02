# Issue #379 — Reconciliation Brief (pre-interrogation)

Branch: `constellation/issue-379-practice-evidence-v2` off `origin/main` @ d2f59df (includes #400/#368, #383).
Worktree: `C:/Programs/f1Brainz/.claude/worktrees/agent-a2987a0486f201762`.

## Ground verified
- #400 preprocessor rework present: median-relative sole encoding (`_compute.py`),
  sprint session-aware buckets (`_split_run_buckets`, `_lap_pipeline.py:452`).
- Diagnostic harness reproduces §7.6 numbers on my worktree DBs (deterministic).

## Part A — SQ as primary Q evidence on sprint weekends
**VERDICT: substantially ALREADY LANDED (issue premise "feeds only FP1" is STALE).**
SQ is consumed on modern sprint weekends at BOTH channels:
1. Lap-feature channel: `get_practice_session_types` returns `["FP1","SQ","S"]` (constants.py:298,
   `SPRINT_PRACTICE_SESSIONS`); `_split_run_buckets` routes FP1+SQ → short-run/quali-sim bucket,
   S → long-run. So qs_* features draw on SQ low-fuel laps.
2. Classification-rank channel: `data_adapter/_assemble.py` + `_build.py` feed `sq_pos` on sprint
   weekends (DriverFeatures.is_sprint_weekend → use sq_pos/s_pos not fp2_pos/fp3_pos); and
   `quali_actual = sq if is_sprint` (_build.py:412) — SQ IS the quali target.
2021 handled: `LEGACY_SPRINT_PRACTICE_SESSIONS=["FP1","FP2"]` (no SQ; matches Admiral standing order).

REMAINING (real, small):
- `docs/evo/practice_preprocessor.md` "Sprint Weekend Handling" section is STALE — still says
  "only FP1 / Pass session_types=['FP1']" (the doc HEADER was updated by #400 but this section wasn't;
  internal contradiction). Doc fix needed.
- Acceptance wants "a test on the sprint session-selection path" — need to confirm whether one
  pins get_practice_session_types / _split_run_buckets routing; add if absent.

## Part B — rank-blend FP1/2/3 on min-sectors (normal weekends)
**VERDICT: PARTIALLY landed. min-sectors correct; cross-session combination is the gap.**
- min-sectors ✓: `_compute_sector_features` theoretical_best = min(s1)+min(s2)+min(s3) (_lap_pipeline.py:297).
- Cross-session combination: production POOLS all FP1/FP2/FP3 laps per driver
  (`groupby("driver_id")`, _lap_pipeline.py:288) then takes min-sectors over the pool. In findings
  taxonomy this is **best_across_fp / theo_best ≈ 0.7968**, NOT **blend_rank / theo_best ≈ 0.8029**.
- Gap on data-only ceiling: blend_rank 0.8029 vs best_across_fp 0.7968 = **~0.6pp**.

GENUINE remaining gap, BUT:
- It is a MODEL-INPUT change → requires calibrated baseline evidence (ORCHESTRATOR_CONTEXT evidence table).
- Small measured edge (~0.6pp ceiling, single-session pooled already captures most of it).
- Epic #378 notes Step-1 cheap fixes are "exactly what Piece 2 (context-conditioned net, #375) would
  otherwise learn as context-weighting" — risk of pre-empting the learned solution.
- SCOPE-CHANGING per decision protocol → SURFACE to Admiral, do not unilaterally implement.

## Baseline numbers (my worktree, reproduced)
- Normal Q: blend_rank/theo_best 0.8029 (148ev) · best_across_fp/theo_best 0.7968 · FP3-only matched 0.7896 vs blend_rank matched 0.8088.
- Sprint Q: SQ→Q 0.7594 (21ev) · FP1→Q 0.6758 · S→Q 0.7296.

## Prior stopped run (reference only, NOT reused)
Branch `constellation/issue-379-practice-evidence` (in sibling worktree, based on fa9e48b WITHOUT #400):
- g1 cf56416: brought diagnose_quali_evidence.py onto its branch (now already on main via #400).
- g2 4200415: added TestSprintWeekendSqIsPrimaryQualiEvidence regression + fixed the stale doc section.
Its g2 conclusion matches mine on Part A. Its tests/doc-fix may be salvageable (re-validate on true main).
