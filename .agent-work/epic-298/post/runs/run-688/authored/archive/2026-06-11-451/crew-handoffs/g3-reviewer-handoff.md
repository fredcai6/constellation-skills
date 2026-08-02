# Reviewer Handoff — G3 (issue #451, cmdr-451) — capacity control

You are a constellation-reviewer crew (Sonnet). Invoke constellation-reviewer, then INDEPENDENTLY verify the G3 capacity-control retrain. Worktree `C:/Programs/f1Brainz-worktrees/cmdr-451`; `py`; `PYTHONIOENCODING=utf-8`; absolute paths (cwd resets).

## What was implemented
One as-is (23-feature) retrain of `driver_quali_power_from_race_weekend` on the OOS split (train 2018-2024, eval 2025), seed 0, but `--hidden-dim 384` (3x default 128). Scored on the §7.6.2 harness. Result: wide-net rw OOS=0.5880 vs G2 control 0.5868 (+0.0012); ceiling 0.7643; 3352 pairs. `capacity_excluded=True`. Evidence in `.agent-work/451/evidence/g3_numbers.json` + `g3-implementer-result.md`.

## How to inspect
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-451
git status --porcelain src/      # MUST be empty — this is an as-is control, NO feature edit
PYTHONIOENCODING=utf-8 py -c "import json;d=json.load(open('.agent-work/451/evidence/g3_numbers.json'));print(json.dumps(d,indent=1))"
cat .agent-work/451/evidence/harness_g3_wide_stdout.txt | tail -20
# confirm the trained manifest shows hidden_dim 384:
PYTHONIOENCODING=utf-8 py -c "import json,glob;[print(p, json.load(open(p)).get('config',{}).get('nn_hidden_dim','?')) for p in glob.glob('.agent-work/451/scratch_runs/g3_wide_oos/**/latent_power_manifest.json',recursive=True)]"
```

## Close criteria
1. **As-is control (no feature edit):** `git status src/` empty; the probe edit from G2 is NOT present (the adapter is the production 23-feature form). The manifest `feature_dim`=23.
2. **Capacity actually bumped:** the trained manifest shows `nn_hidden_dim`=384 (not 128).
3. **Clean contrast vs G2 control:** same split (train 2018-2024 / eval 2025), same seed 0, same 23 features — differs from G2 control ONLY by hidden_dim. So the rw delta isolates capacity.
4. **No leakage / harness fidelity:** eval 2025 held out of training; `diagnose_quali_same_pairs.py` unmodified; ceiling 0.7643 and pairs 3352 match the G2 control OOS read (shared-pairs set identical).
5. **Verdict follows:** wide-net rw≈control (0.5880 vs 0.5868) → capacity_excluded=True is justified.

## Constraints / exclusions
DB-only; harness reuse-not-fork. Do not re-run unless you suspect tampering (a cheap harness re-read on the existing records is encouraged). Do not decide the final verdict.

## Required evidence
Your checks (git src clean, manifest hidden_dim=384, ceiling/pairs match, numbers reproduce). Verdict APPROVE/BLOCK.

## Return format
REVIEW_RESULT: verdict, what you verified with outputs, defects (severity), out-of-scope notes, workflow feedback. Write to `C:/Programs/f1Brainz-worktrees/cmdr-451/.agent-work/451/evidence/g3-review-result.md`.
