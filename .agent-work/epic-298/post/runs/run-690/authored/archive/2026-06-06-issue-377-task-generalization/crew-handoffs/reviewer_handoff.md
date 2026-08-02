# Reviewer Handoff — issue #377 fact-check of fusion_task_generalization.md

You are an INDEPENDENT REVIEWER. Invoke the `constellation-reviewer` skill and drive its survey.
Your job: **re-derive (do NOT trust) every number** in the deliverable doc against its cited
artifacts, and **flag any claim stronger than its evidence**. This is a WRITE-UP review: there is
no code diff — the "diff" is a single new markdown file.

You are READ-ONLY. Do not edit any file. Do not run anything under `src/` or `scripts/` that
writes. Do not background any task. Run everything foreground. Use `py` (never `python`); always
prefix python with `PYTHONIOENCODING=utf-8`.

## Working directory
`C:\Programs\f1Brainz\.claude\worktrees\agent-acab912ce15ad36bd` (a git worktree on branch
`constellation/issue-377-task-generalization`). All paths below are relative to it.

## The deliverable under review
`docs/evo/fusion_task_generalization.md`

## Artifacts the doc cites (your sources of truth — re-derive against THESE)
- **[SC]** `.agent-work/archive/2026-06-06-issue-373-correlated-fusion/evidence/scorecard.json`
  — the #373 replay scorecard. Has per-task `R_diagnostics.R_estimated_offdiag`,
  `R_diagnostics.condition_number_before/after_shrinkage`, and `variant_means` for
  `baseline`, `A`, `ablation_RI`, `cheapB` (and lambda variants).
- **[FD]** `docs/evo/fusion_rework_findings.md` — #373 findings (decomposition table, cheap-B).
- **[CD]** `docs/evo/prediction_ceiling_and_priorities.md` — persistence ceilings (§1.1, §1.2),
  retro spread (§1.3), compound work (§7.1/§7.5/§7.7), spread target (§9.3/§9.5), quali
  localization (§7.6.2/§7.6.3).
- **[CEIL-RUN]** `.agent-work/issue-377-task-generalization/evidence/ceiling_diagnose_output.txt`
  — captured output of `scripts/diagnose_prediction_ceiling.py` from this run. You MAY re-run
  `PYTHONIOENCODING=utf-8 py scripts/diagnose_prediction_ceiling.py` yourself (read-only,
  ~30–60s) to independently confirm the persistence numbers.

## Specific numbers to RE-DERIVE (the load-bearing ones)

1. **Per-task cross-module correlations (doc §1.1 table).** From [SC], for each task
   (quali / race_start / race), pull `R_estimated_offdiag` and confirm the doc's grouping:
   - constructor↔driver same-evidence = `Crec↔Drec` and `Cwk↔Dwk`
   - recent↔weekend same-scope = `Drec↔Dwk` and `Crec↔Cwk`
   Confirm quali ≈ 0.869/0.860 (C↔D) and 0.731/0.716 (rec↔wk); race_start ≈ 0.833/0.833 and
   0.895/0.894; race ≈ 0.842/0.840 and 0.874/0.818. Confirm condition numbers
   105.6→25.4 / 1187.3→34.6 / 226.4→30.5. A helper to read [SC]:
   `PYTHONIOENCODING=utf-8 py -c "import json; d=json.load(open(r'.agent-work/archive/2026-06-06-issue-373-correlated-fusion/evidence/scorecard.json')); [print(t, d['tasks'][t]['R_diagnostics']['R_estimated_offdiag']) for t in ['quali','race_start','race']]"`

2. **The decomposition table (doc §1.4).** From [SC] `variant_means`, for each task compute:
   Δ reformulation = `ablation_RI − baseline`; Δ correlation = `A − ablation_RI`;
   Δ total = `A − baseline`, for metrics rank_mae, spearman, pairwise_ll, cov80. Confirm the
   doc's table values (e.g. quali rank_mae Δreform −0.178 / Δcorr +0.198 / Δtotal +0.020;
   race_start rank_mae −0.679 / +0.048 / −0.631; race rank_mae −0.435 / +0.269 / −0.167).
   Confirm these match [FD]'s own decomposition table too.

3. **The central claim (doc §1.4 / exec summary): "A moves calibration not ordering, per task."**
   Verify: Δ correlation on rank_mae is positive (worse) on ALL three; Δ correlation on spearman
   is negative (worse) on ALL three; Δ correlation on cov80 is positive (toward nominal) on ALL
   three; Δ correlation on pairwise_ll is negative (better) on ALL three. If any sign is
   misreported, flag it.

4. **Persistence baselines (doc §3.1 / exec summary):** grid→lap3 0.875, lap3→finish 0.776,
   grid→finish 0.753; systematic team-pace mean 6.5%; flip-pair model-acc 29.8%. Confirm against
   [CEIL-RUN] (and optionally your own re-run).

5. **Module sign-acc (doc §3.2):** race_start 0.910 (driver) / 0.919 (constructor); race 0.791 /
   0.740; quali 0.745 / 0.769. Confirm against [CEIL-RUN].

6. **Spread-target numbers (doc §2.2/§2.4/§3.2):** `s_e` cross-event CV 0.31 (race) / 0.35
   (race_start) / 0.80 (quali); disagreement rate quali ~3% → race ~16% → race_start ~19%.
   Confirm against [CD §9.5] (search the doc for "cross-event CV" and "disagreement rate rises").

7. **Quali #414 numbers (doc §2.2/§3.2):** standalone race_weekend ~19pp below ceiling; anchor
   recovers ~68–72% at α=0.5; magnitude-only no-op Δ=0.0. Confirm against [CD §7.6.2/§7.6.3].

8. **Compound γ claim (doc §2.4 hyp 1 / Inputs-to-#375 item 5):** the doc says the γ degradation
   crossover did NOT identify, is wrong-signed/confounded, and "a better fit cannot rescue it,"
   and that β reaches ≤13% of feature pairs. Confirm against [CD §7.5/§7.7].

## Overclaim audit (flag any of these)
- Any number that does not match its cited artifact.
- Any claim stated as MEASURED that is actually inference/speculation (the doc uses explicit
  [MEASURED]/[INFERRED]/[SPECULATIVE] tags in Thread 2 and "labelled HYPOTHESIS" in Thread 1.3 —
  check the tags are honest: e.g. the "independence collapses via the shared handoff" MECHANISM
  must be labelled a hypothesis, NOT presented as measured; the doc must NOT claim it measured a
  *conditioned* partial correlation).
- Any place the doc claims the redundancy correction improves ORDERING (it must not — the whole
  result is calibration-not-ordering).
- Any claim that "constructor dominates more on race" is supported (the doc should say it is NOT
  supported).
- Directionality errors on cov80 (higher coverage = toward the 0.80 nominal = better — the doc
  treats positive cov80 Δ as a calibration improvement; verify that framing is consistent).

## Forbidden-file check
Confirm via `git status --short` and `git diff --stat` that the ONLY tracked change is
`docs/evo/fusion_task_generalization.md` (plus untracked `.agent-work/...`). The doc must NOT have
modified `docs/evo/fusion_rework_findings.md` or `docs/evo/prediction_ceiling_and_priorities.md`.

## Close criteria (each becomes a review check)
- C1: every load-bearing number (items 1–8) re-derives to the cited artifact (±rounding).
- C2: the central calibration-not-ordering claim is correct per task (item 3).
- C3: evidence tags are honest — no inference/speculation mislabelled as measured; the Thread-1.3
  mechanism and the conditioned-redundancy gap are labelled as hypothesis/unmeasured.
- C4: no claim is stronger than its evidence (overclaim audit clean, or flagged).
- C5: forbidden files untouched; doc has the required sections (exec summary, Thread 1/2/3,
  Inputs to #375, Inputs to #392).

## Return format (print this clearly at the END of your run)
```
REVIEW_RESULT
verdict: APPROVE | BLOCK
checks:
  C1: pass|fail — <evidence: which numbers you re-derived and whether they matched>
  C2: pass|fail — <...>
  C3: pass|fail — <...>
  C4: pass|fail — <...>
  C5: pass|fail — <...>
findings:
  - <each factual error or overclaim, with the doc location and the correct value/framing>
  (write "none" if clean)
blockers:
  - <anything that prevented a verdict, or "none">
```
APPROVE only if C1–C5 all pass. If any number is wrong or any claim overreaches, BLOCK and name it
precisely so it can be fixed.
