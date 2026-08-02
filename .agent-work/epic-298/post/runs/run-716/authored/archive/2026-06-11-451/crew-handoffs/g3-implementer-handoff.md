# Implementer Handoff — G3 (issue #451, cmdr-451) — capacity control

You are a constellation-implementer crew (Sonnet). Invoke constellation-implementer, then execute this tight gate. Worktree `C:/Programs/f1Brainz-worktrees/cmdr-451`; `py` not `python`; `PYTHONIOENCODING=utf-8` on captured python; absolute paths (cwd resets). Retrain runs FOREGROUND, fast — never background it.

## Gate
g3 — exclude hypothesis (c) capacity. ONE as-is (23-feature) retrain of `driver_quali_power_from_race_weekend` with a WIDER net, scored on the §7.6.2 harness; if extra capacity does NOT lift rw, (c) is excluded.

## Context
G1 (linear probe of the head's own features = 0.6513, ~ceiling-minus-15pp) and G2 (adding the min-pace input feature lifts OOS rw 0.5868→0.7700 ≈ ceiling) already point to (a) representation. This gate confirms the deficit is NOT a too-small net: if MORE capacity on the SAME 23 features can't extract more ordering, the signal genuinely isn't in the features.

The adapter is currently REVERTED to the production 23-feature form (confirm `git status src/` is clean before starting). Default `nn_hidden_dim`=128.

## Task
Single OOS split (the clean read): `--train-years 2018 2019 2020 2021 2022 2023 2024 --eval-year 2025`, `--seed 0`, as-is 23 features, but `--hidden-dim 384` (3x). Then emit `rw_2025.record.json` from the trained bundle and score `scripts/diagnose_quali_same_pairs.py` UNMODIFIED on a condition-specific records dir (reuse the G2 control rh_2025 record so the shared-pairs set matches G2 control exactly). Compare rw to the G2 CONTROL OOS baseline (0.5868, hidden_dim 128, same split/seed/features).

Commands (mirror G2; verified working):
```bash
PYTHONIOENCODING=utf-8 py src/evo_predictor/run.py train-latent-power-module \
  --module driver_quali_power_from_race_weekend \
  --train-years 2018 2019 2020 2021 2022 2023 2024 --eval-year 2025 \
  --seed 0 --hidden-dim 384 \
  --compound-prior-root params/gold/compound_prior \
  --retro-root C:/Programs/f1Brainz/params/retro_truth \
  --db-root C:/Programs/f1Brainz/data \
  --artifact-root .agent-work/451/scratch_runs --run-name g3_wide_oos
# then emit rw_2025 from the trained bundle dir, into .agent-work/451/records_g3_wide/
# (reuse/copy .agent-work/451/records_g2_control/rh_2025.record.* into records_g3_wide/)
# then run the harness with QUALI_SAME_PAIRS_RECORDS_DIR=.agent-work/451/records_g3_wide
```
The emit `--bundle` is the trained module dir under `.agent-work/451/scratch_runs/g3_wide_oos/...` (find the dir containing `latent_power_manifest.json`).

## Verdict logic to REPORT
- If wide-net rw ≈ 0.59 (within ~±0.02 of control 0.5868) → capacity (c) EXCLUDED: extra capacity on the same features does not help; the deficit is feature/representation.
- If wide-net rw rises materially toward ceiling → capacity is partly the lever (would soften the (a) verdict). Report honestly either way.

## Write evidence
`.agent-work/451/evidence/g3_numbers.json` with keys `wide_net` (dict: hidden_dim, rw, ceiling, pairs, split), `control_ref` (0.5868 from G2), and `capacity_excluded` (bool).

## Allowed scope
`.agent-work/451/**` only. The adapter MUST stay at its reverted 23-feature production form — do NOT re-apply the G2 probe edit (this is an as-is control). READ-only src/params.

## Specific exclusions
NO feature edit (this is as-is). NO gold cycle/fusion/Piece-2. NO harness modification. NO promoted-default change.

## Constraints
Single-module retrain; seed 0; eval year held out (no leakage); DB-only; `py`; utf-8; foreground bounded (<=10 min; if >30 min, STOP).

## Map anchors
Structural: InnerNetwork width (`--hidden-dim`); train+emit CLIs. Evidence: G2 control OOS 0.5868; InnerNetwork is a 3-layer MLP (a priori not capacity-starved for 23 inputs).

## Required evidence
`g3_numbers.json`; harness stdout (saved); confirm `git status src/` clean (no feature edit) before AND after. Quote wide-net rw vs control 0.5868 in your result.

## Verification commands
```bash
git status --porcelain src/      # MUST be empty (as-is control)
PYTHONIOENCODING=utf-8 py -c "import json;d=json.load(open('.agent-work/451/evidence/g3_numbers.json'));print('wide_net' in d, d.get('capacity_excluded'))"
```

## Suggested model tier
simple bounded — one retrain + harness, clear commands.

## Authority
Probe design fixed. You do NOT decide the final verdict. Report numbers + direction.

## Stop conditions
Stop if: the retrain errors irrecoverably; the harness can't score; or producing evidence needs a src/params change.

## Return format
IMPLEMENTER_RESULT: wide-net rw vs control 0.5868, ceiling, pairs; capacity_excluded true/false and why; files changed (only .agent-work/451/**); git status src/ clean confirmation; assumptions; stop conditions; workflow feedback. Write to `C:/Programs/f1Brainz-worktrees/cmdr-451/.agent-work/451/evidence/g3-implementer-result.md`.
