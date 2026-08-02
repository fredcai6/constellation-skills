# Implementation Result

## Assigned gate
g3 — capacity-control gate (issue #451, cmdr-451): wide-net (hidden_dim=384) as-is retrain vs G2 control OOS baseline 0.5868

## Completed slice
1. Verified git status src/ clean (no feature edit — adapter at reverted 23-feature production form).
2. Created `.agent-work/451/records_g3_wide/`; copied `rh_2025` (and rh/rw 2018-2024) from `records_g2_control` so shared-pairs construction matches G2 control exactly.
3. Retrained `driver_quali_power_from_race_weekend` with `--hidden-dim 384` (3x default 128), `--train-years 2018..2024`, `--eval-year 2025`, `--seed 0`, 23 features as-is. FOREGROUND. Completed in ~8 minutes.
4. Emitted `rw_2025.record.json` / `.record.npz` from trained bundle into `records_g3_wide`.
5. Ran `scripts/diagnose_quali_same_pairs.py` UNMODIFIED on `records_g3_wide`. Captured stdout.
6. Wrote `g3_numbers.json` with required keys.

## Scope
**Files changed:**
- `.agent-work/451/g3-implementer-plan.json` — engine plan (new)
- `.agent-work/451/records_g3_wide/` — 33 files: rh 2018-2025 and rw 2018-2025 (rw_2025 is wide-net; rw_2018-2024 and all rh carried from records_g2_control)
- `.agent-work/451/scratch_runs/g3_wide_oos/` — 4 files: trained bundle (latent_power_manifest.json, model_checkpoint.pt, module_diagnostics.json, training_batches.json)
- `.agent-work/451/evidence/harness_g3_wide_stdout.txt` — full harness output (new)
- `.agent-work/451/evidence/g3_numbers.json` — required evidence file (new)
- `.agent-work/451/evidence/g3-implementer-result.md` — this file (new)

**Specific exclusions touched:** none — no feature edit, no gold cycle/fusion/Piece-2, no harness modification, no promoted-default change, no src/params change.

## Behavior changed
No production behavior changed. All artifacts are in `.agent-work/451/**` only.

## Map Impact
- **Structural anchors touched:** InnerNetwork width (`nn_hidden_dim=384`); confirms the train+emit CLIs work as expected.
- **Claims/evidence produced:** G3 OOS wide-net rw=0.5880 vs control 0.5868 (delta +0.0012); capacity excluded as bottleneck. Supports the hypothesis (a) representation verdict from G2.
- **Constraints/assumptions touched:** The 23-feature as-is constraint was honored exactly; no schema version bump.

## Test mode
**Required:** evidence-only (retrain + harness run; no unit tests applicable)
**Satisfied:** yes — g3_numbers.json written and verified; harness stdout captured; git src/ clean confirmed before and after.

## IMPLEMENTER_RESULT — core numbers

### Wide-net OOS 2025 (hidden_dim=384, 3x default 128, seed=0, 23 features as-is)

| Metric | Wide-net (G3) | Control (G2) | Delta |
|---|---|---|---|
| rw OOS 2025 | **0.5880** | 0.5868 | **+0.0012** |
| ceiling (best_across_fp) | 0.7643 | 0.7643 | 0 |
| gap to ceiling | 0.1763 | 0.1775 | -0.0012 |
| pairs | 3352 | 3352 | 0 |
| events | 18 | 18 | 0 |

### Verdict direction: **capacity_excluded = True**

Wide-net rw=0.5880 is within +0.0012 of control 0.5868 — well within the ±0.02 verdict threshold. Tripling the hidden dimension from 128 to 384 does not lift OOS performance. The 0.1763 gap to the 0.7643 ceiling is effectively unchanged. Extra capacity on the same 23 features cannot extract more ordering signal — because the signal is not in those features.

**This is consistent with hypothesis (a): the deficit is representational (feature absence), not a capacity or training-signal bottleneck.**

Commander decides the final verdict.

### Harness output excerpt (OOS 2025)
```
OOS CONFIRMATION — clean 2025
channel          | model (pi)             best_across_fp         blend_rank
race_weekend     | 0.5880 (ev=18,p=3352)   0.7643 (p=3352)   0.7709 (p=3352)
recent_history   | 0.7581 (ev=18,p=3352)   0.7643 (p=3352)   0.7709 (p=3352)
  residual = ceiling_acc - model_acc:
    race_weekend      vs best_across_fp = +0.1763   vs blend_rank = +0.1829
```

## git status src/ clean confirmation
- **BEFORE retrain:** `git status --porcelain src/` → empty (confirmed)
- **AFTER retrain + emit + harness:** `git status --porcelain src/` → empty (confirmed)

No src/ edit was made at any point. The adapter stayed at `driver_quali_power_from_race_weekend.v2` (23 features).

## Assumptions
- rw records for 2018-2024 in records_g3_wide were carried from records_g2_control (same bundle). These do not affect the OOS 2025 scoring directly; they are needed only for the HEADLINE regime which the handoff did not require but which the harness always computes. The OOS 2025 pairs (3352) match G2 control exactly (same rh_2025, same driver population).
- The manifest confirms `nn_hidden_dim=384` and `feature_dim=23` — as-is control confirmed.
- HEADLINE rw=0.6560 is identical to G2 control (expected: rw_2018-2024 are unchanged G2 control records; only 2025 is from the wide-net).

## Stop conditions hit
None. Retrain completed without error. Harness ran cleanly.

## Out-of-scope observations
None.

## Workflow Feedback
- **Handoff gaps:** The handoff said "reuse the G2-control rh_2025 record so the shared-pairs set matches G2 control." This was clear. However, the harness also loads rw_2018-2024 and rh_2018-2024 for the HEADLINE regime — the handoff didn't mention copying those. I inferred the correct approach by inspecting the harness source (HEADLINE_YEARS = 2018-2024) and mirroring G2's setup. This was a minor gap: the handoff could say "populate records_g3_wide with all G2 control records except rw_2025."
- **Context rediscovered:** The `--emit-module-record` flag requires `--output` (not documented in the handoff commands). I discovered this from the CLI help and mirrored the G2 approach.
- **Instructions improvised around:** none — the FOREGROUND retrain worked cleanly.
- **What would have made this easier:** The emit command could be spelled out fully in the handoff (including `--output`), and the records dir setup could mention "copy all rh+rw 2018-2024 from records_g2_control too (harness HEADLINE_YEARS needs them)."

## Return status
`complete`
