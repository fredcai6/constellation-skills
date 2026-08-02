# Reviewer Handoff — G1 (issue #451, cmdr-451)

You are a constellation-reviewer crew (Sonnet). Invoke the constellation-reviewer skill, then verify the G1 implementer's work INDEPENDENTLY. Work in worktree `C:/Programs/f1Brainz-worktrees/cmdr-451`; `py` not `python`; `PYTHONIOENCODING=utf-8` on captured python. Use absolute paths; shell cwd resets between calls.

## What was implemented
G1 reproduced the §7.6.2 same-pairs scoreboard from the committed bundle `gold_cycle_260608_043414` (inference only, no retrain) and ran a read-only walk-forward linear probe of the rw head's own input features. Results in `.agent-work/451/evidence/g1_numbers.json`; implementer result in `.agent-work/451/evidence/g1-implementer-result.md`; scratch probe `.agent-work/451/probe_linear.py`; harness output `.agent-work/451/evidence/same_pairs/same_pairs_numbers.json`.

Reported: baseline FLAGGED rw=0.6711 (vs §7.6.2 0.6149; anchor-active bundle), rh=0.7786, ceiling=0.8061, 23862 pairs (rh/ceiling/pairs reproduced exactly). Linear probe (LOSO) = 0.6513.

## How to inspect
```bash
cd C:/Programs/f1Brainz-worktrees/cmdr-451
git status --porcelain            # expect ONLY .agent-work/451/** untracked; NO src/scripts/params changes
git diff --stat                   # expect empty (no tracked-file edits)
PYTHONIOENCODING=utf-8 py -c "import json;d=json.load(open('.agent-work/451/evidence/same_pairs/same_pairs_numbers.json'));r=d['regimes']['headline_2018_2024'];print('rw',r['race_weekend']['model']['acc'],'rh',r['recent_history']['model']['acc'],'ceil',r['race_weekend']['best_across_fp']['acc'],'pairs',r['race_weekend']['model']['pairs'])"
```
Read `.agent-work/451/probe_linear.py` and confirm the leakage control.

## Task statement
Confirm G1 is a faithful, leakage-free reproduction + probe — NOT a verdict. The Commander draws the verdict.

## Close criteria (verify each, with evidence)
1. **Inference only / no production change:** `git diff` shows no edits to `src/**`, `scripts/**`, `params/**`; only `.agent-work/451/**` is new. The harness script `scripts/diagnose_quali_same_pairs.py` is unmodified (git clean).
2. **Harness fidelity:** the numbers came from `diagnose_quali_same_pairs.py` run unmodified; the shared-pairs invariant holds (the script itself asserts model/baf/blr scored on identical surviving pairs — confirm it ran without the AssertionError and pairs=23862). rh=0.7786 and ceiling=0.8061 reproduce §7.6.2.
3. **Baseline deviation handled honestly:** rw=0.6711 deviation from 0.6149 is FLAGGED with a stated cause (anchor-active bundle) and 0.6711 adopted as the working baseline. This is acceptable per the handoff — verify it is documented, not silently swapped.
4. **Linear probe is walk-forward / leakage-free:** read `probe_linear.py` — confirm the logistic fit does NOT include any pair it later scores (LOSO or train-earlier/score-later), and standardization is fit on train only. Confirm it scores the SAME shared non-tie pairs as the harness (reuses the harness primitives, not a re-derived pair set). Re-run it if cheap and confirm acc≈0.6513.
5. **Internal consistency:** `g1_numbers.json` has `baseline` + `linear_probe`; numbers match the harness output and the result narrative.

## Specific exclusions
Do not re-run the full record regen unless you suspect tampering. Do not judge the localization verdict. Do not propose fixes.

## Constraints
DB-only; reuse-not-fork harness primitives; walk-forward discipline.

## Map anchors (inherited from g1-implement)
Structural: quali_power_adapter feature vector; diagnose_quali_same_pairs harness; committed bundle. Decision: §7.6.3 C3 (sign-accuracy moves only with new ordering signal). Evidence: rw/rh/ceiling/pairs anchor. Confidence flag: anchor-active bundle reproduction.

## Required evidence
Your independent check outputs (git status, harness re-read, probe leakage read). State the verdict APPROVE or BLOCK with specific reasons.

## Return format
Return REVIEW_RESULT with: verdict (APPROVE / BLOCK), what you verified, any defects (with severity), out-of-scope observations, and workflow feedback. Also write it to `C:/Programs/f1Brainz-worktrees/cmdr-451/.agent-work/451/evidence/g1-review-result.md`.
