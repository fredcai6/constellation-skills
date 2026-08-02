# Triage Recommendation: Confirm or schedule full gold module retrain

## Classification
`unresolved decision`, `research hardening`

## Source checklist/artifact
- reconcile-summary.md T4
- g4 artifact regen approach (sidecar refresh vs full retrain)

## Structural anchor
`struct:evo.gold_cycle`, `outputs/evo_runs/gold_module_training_cycle/`

## Problem
Issue-292 g4 refreshed committed sidecars (unc_diag, fusion_train_rows merge, fusion/rt_comparison alignment) on May-26 gold cycle bundles rather than running a full gold retrain. Need explicit decision whether that baseline is acceptable for merge.

## Current truth
- Compact validation passes
- 81 focused tests pass
- Gold cycle stem `gold_cycle_260526_004033_2018thru2024` unchanged at module-weight level
- Sidecars and validation artifacts updated in g4

## Desired/future concern
Promoted baseline should match the observability contract under real trained weights, not only patched JSON sidecars.

## Evidence
- g4 pilot notes
- reconcile-summary.md T4

## Impact
Merge without retrain may leave module metrics/weights stale relative to latest code paths (though issue-292 did not change training math).

## Suggested scope
Human decision: accept May-26 baseline for issue-292 merge OR schedule full `py -m src.evo_predictor.run gold-cycle --config configs/evo/gold_defaults.toml` and recommit reports.

## Non-goals
- Blocking issue-292 observability merge on unrelated training experiments
- Changing gold training hyperparameters

## Acceptance criteria
- [ ] Explicit recorded decision (issue comment or ADR note)
- [ ] If retrain chosen: new gold_cycle stem committed and compact validation passes

## Recommended priority
`medium`

**Reason:** Baseline authority for promoted reports.

## Issue creation authority
`ask user`
