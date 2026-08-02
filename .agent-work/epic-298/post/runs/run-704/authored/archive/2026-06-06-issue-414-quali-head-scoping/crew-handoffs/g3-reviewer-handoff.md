# Reviewer Handoff — issue-414 G3

You are a fresh, independent reviewer. Verify this docs change yourself. Invoke the `constellation-reviewer` skill and drive it. Do not read any transcript.

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-a82dd9d22cd9863fc`
Set `PYTHONIOENCODING=utf-8`. Python is `py`. Read/verify only — no background work.

## Gate
g3

## What Was Implemented
A new subsection `### 7.6.3 Targeted-fix scoping (#414)` appended to `docs/evo/prediction_ceiling_and_priorities.md`, between §7.6.2 and §7.7. It reports the #414 measured scoping result (cross-channel pace-anchor blend recovers the bulk of the race_weekend quali sign-accuracy gap; magnitude-only recalibration is a no-op), ends with `RECOMMENDATION: BOTH-STAGED`, and a `#408 ABSORPTION:` line.

## How to Inspect the Diff
```
git diff docs/evo/prediction_ceiling_and_priorities.md
git diff --numstat docs/evo/prediction_ceiling_and_priorities.md
```
The G2 evidence to check numbers against: `.agent-work/issue-414-quali-head-scoping/evidence/g2_scope_run.txt` and `scope_anchor_numbers.json`.

## Task Statement
Confirm the subsection is an append-shaped insertion with numbers faithful to the G2 evidence, the verdict follows from those numbers, and the explicit recommendation + #408 lines are present and justified.

## Close Criteria (verify each)
- (1) **Append-shaped.** `git diff --numstat` shows additions only, 0 deletions, on this file. §7.6/§7.6.1/§7.6.2/§7.7 are unchanged (the only change is the new §7.6.3 between §7.6.2 and §7.7). `### 7.7` still immediately follows §7.6.3.
- (2) **Numbers faithful.** Every number in the §7.6.3 table and prose matches `g2_scope_run.txt` / `scope_anchor_numbers.json`. Spot-check at least: C1 headline α=0.2 (0.6947 / 0.8062), α=0.5 (0.7452 / 0.8691, rec +0.681/+0.724), α=1.0 (0.8061/0.9365); C2 α=0.5 (0.7399/0.8737); C3 Δ=0.0; OOS C1 α=0.5 (0.7097/0.8451). Read the JSON yourself to confirm.
- (3) **Verdict follows from numbers + internally consistent.** The BOTH-STAGED recommendation is consistent with: a targeted anchor recovering ~68–72% at α=0.5 (strong but partial), the gap being context-dependent (a global α can't reach per-context optimum), and §7.6.2's routing to #375. The reasoning must not overclaim (it should NOT say the targeted fix fully closes the gap) nor underclaim (it should NOT dismiss a fix that demonstrably recovers the majority).
- (4) **Explicit lines present & justified.** `RECOMMENDATION: BOTH-STAGED` is present. `#408 ABSORPTION:` is present and its logic is sound: #408 is a gap-SCALE (magnitude) head; C3 shows magnitude has zero leverage on sign-accuracy; therefore #408 folds into #375 as the magnitude/uncertainty component, not as a standalone sign-accuracy fix.
- (5) **Zero production change in this gate.** `git status --short` shows only docs modified by THIS gate (the `M scripts/diagnose_quali_same_pairs.py`, `?? scripts/scope_quali_anchor_414.py`, `?? tests/...` are from G1/G2, not this gate). No code, manifest, or fusion file changed for G3.
- (6) **No forbidden files.** `docs/evo/fusion_rework_findings.md`, `src/evo_predictor/fusion.py`, `src/evo_predictor/fusion_training/` are untouched across the whole working tree.
- (7) **Docs hygiene.** Markdown renders (table aligned, fences closed); references (#375, #408, §7.6.2, the script path, the bundle name) are valid/existing.

## Commands (run yourself)
```
git diff --numstat docs/evo/prediction_ceiling_and_priorities.md
git status --short
findstr /n "7.6.3 7.7 RECOMMENDATION: #408" docs\evo\prediction_ceiling_and_priorities.md
PYTHONIOENCODING=utf-8 py -c "import json; d=json.load(open('.agent-work/issue-414-quali-head-scoping/evidence/scope_anchor_numbers.json')); h=d['regimes']['headline_2018_2024']; print('C1 a=0.5', h['c1']['0.5']['acc'], h['c1']['0.5']['easy_acc']); print('C3 delta', h['c3_no_op_delta'])"
```

## Allowed Scope
Read-only verification. Do NOT modify any file.

## Constraints the Implementation Must Respect
- Append-shaped; numbers verbatim from G2; verdict honest; recommendation + #408 lines present; zero production change; no forbidden files.

## Evidence Produced
Implementer reports: 85 insertions / 0 deletions; §7.6.3 at line 643, §7.7 at 728; table cross-check passed; recommendation + #408 lines present.

## Suggested Model Tier
simple bounded — fidelity + logic check.

## Stop Conditions
Return BLOCK if: any existing section changed; a number disagrees with the G2 evidence; the verdict over/underclaims relative to the numbers; the recommendation or #408 line is missing/unjustified; a forbidden or production file changed.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-criterion finding with the numbers you checked, blockers, out-of-scope observations.
