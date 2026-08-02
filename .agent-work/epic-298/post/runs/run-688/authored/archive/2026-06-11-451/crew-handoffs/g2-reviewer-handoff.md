# Reviewer Handoff — G2 (issue #451, cmdr-451)

You are a constellation-reviewer crew (Sonnet). Invoke constellation-reviewer, then INDEPENDENTLY verify the G2 feature-ablation retrain. Worktree `C:/Programs/f1Brainz-worktrees/cmdr-451`; `py` not `python`; `PYTHONIOENCODING=utf-8`; absolute paths (cwd resets).

## What was implemented
Two single-module retrains of `driver_quali_power_from_race_weekend` (seed 0) under two feature conditions, on two splits, scored on the §7.6.2 same-pairs harness:
- CONTROL = 23 features as-is.
- +PACE = 24th input feature = NaN-safe `min(qs_best_raw, lr_best_raw)` (the #420 cross-channel pace anchor, as an INPUT). Probe edit left in place in `src/evo_predictor/quali_power_adapter.py`.

Reported (in `.agent-work/451/evidence/g2_numbers.json` + `g2-implementer-result.md`):
- splitA (train 2018-2023, eval 2024): control rw=0.6560 → +pace 0.6792 (+0.023), ceiling 0.8061, 23862 pairs.
- splitB OOS (train 2018-2024, eval 2025): control rw=0.5868 → +pace **0.7700** (+0.183), ceiling 0.7643, 3352 pairs.
- points_to = 'a' (representation).

## How to inspect
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-451
git diff src/evo_predictor/quali_power_adapter.py     # the probe edit — confirm it ONLY appends min(qs_best_raw,lr_best_raw) + its name; no other behavior change
git status --porcelain                                # src edit expected (probe); everything else under .agent-work/451/**
PYTHONIOENCODING=utf-8 py -c "import json;d=json.load(open('.agent-work/451/evidence/g2_numbers.json'));print(json.dumps(d,indent=1))"
cat .agent-work/451/evidence/harness_control_stdout.txt | tail -30
cat .agent-work/451/evidence/harness_pace_stdout.txt | tail -30
```

## Task statement
Confirm the CONTROL vs +PACE contrast is a clean, leakage-free, apples-to-apples test, and that the reported direction follows from the numbers. You do NOT decide the final localization verdict.

## Close criteria (verify each)
1. **Probe edit is minimal & correct:** `git diff` shows ONLY the appended feature (value = NaN/None-safe min of qs_best_raw, lr_best_raw) and its name added to the feature-names tuple; no other logic touched. Confirm it is the #420 idiom (min, not max; lower=faster pace).
2. **Single-module fence:** no gold cycle / fusion / Piece-2; only the rw module retrained; trained bundles under `.agent-work/451/scratch_runs/`. The committed `params/gold` bundle is unchanged (`git status` clean for params/).
3. **Determinism / clean contrast:** both conditions use `--seed 0` and the SAME train/eval split per comparison, so control vs +pace differ ONLY by the feature. Confirm from the trained bundles' manifests / the commands in the result.
4. **No leakage / walk-forward:** eval year held out of training (splitA eval 2024 trained on 2018-2023; splitB eval 2025 trained on 2018-2024). The pace feature is FP-derived (pre-Q), so it respects the as-of cutoff. No scored pair appears in training.
5. **Harness fidelity & identical shared pairs:** `diagnose_quali_same_pairs.py` unmodified; the ceiling and pair count are IDENTICAL across control vs +pace on a given split (ceiling/pairs depend on rh + min-sector source, not the rw head) — confirm ceiling=0.8061/0.7643 and pairs=23862/3352 match across both conditions. If they do NOT match, the contrast is confounded — BLOCK.
6. **The headline-dilution caveat is honestly stated:** splitA pools 2018-2024 records but only the 2024 year was retrained per condition (2018-2023 come from the shared G1 gold bundle), so the +0.023 headline delta UNDERSTATES the effect; the clean read is the OOS splitB (+0.183, full eval year retrained). Confirm the result documents this and does not overclaim the headline number.
7. **Direction follows from numbers:** points_to='a' is justified by OOS +pace ≈ ceiling while control reproduces the deficit.

## Specific exclusions
Do not re-run all 4 retrains unless you suspect tampering (re-running ONE condition to spot-check is fine and encouraged if cheap). Do not decide the final verdict. Do not revert the probe edit (Commander does that at integrate).

## Constraints
DB-only; harness reuse-not-fork; walk-forward discipline.

## Map anchors (inherited from g2-implement)
Structural: quali_power_adapter _driver_vector; DriverFeatures qs_best_raw/lr_best_raw; train + emit CLIs. Decision: §7.6.3 C3; decision pressure — small representation fix touches a promoted default → Admiral float. Evidence: #414/#420 anchor; G1 linear probe 0.6513.

## Required evidence
Your independent checks (the diff read, ceiling/pairs match across conditions, a spot re-run if done). Verdict APPROVE or BLOCK with specifics.

## Return format
Return REVIEW_RESULT: verdict (APPROVE/BLOCK), what you verified with outputs, defects (severity), out-of-scope observations (esp. the OOS rw slightly exceeding ceiling — note it as an Admiral-level promotion decision, not a defect), workflow feedback. Write it to `C:/Programs/f1Brainz-worktrees/cmdr-451/.agent-work/451/evidence/g2-review-result.md`.
