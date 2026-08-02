# Review Result — G3 Capacity Control (issue #451, cmdr-451)

## Assigned Gate
G3 — capacity-control retrain: wide-net (hidden_dim=384) as-is OOS vs G2 control baseline 0.5868

## Result
**APPROVE**

## Handoff compliance
All five close criteria satisfied:

1. **As-is control (no feature edit):** `git status --porcelain src/` returned empty — confirmed before and after retrain. Production adapter at `driver_quali_power_from_race_weekend.v2` (23-feature form). No `cross_channel_min_pace`, `v3-probe`, or 24-feature references exist in any `.py` source file. Schema version confirmed: `DRIVER_QUALI_POWER_FEATURE_SCHEMA_VERSION = "driver_quali_power_from_race_weekend.v2"` in `quali_power_adapter.py`.

2. **Capacity actually bumped:** `latent_power_manifest.json` (`.agent-work/451/scratch_runs/g3_wide_oos/`) reports `nn_hidden_dim=384` and `feature_dim=23`. Both confirmed by direct JSON read.

3. **Clean contrast vs G2 control:** `training_batches.json` confirms train years = `[2018, 2019, 2020, 2021, 2022, 2023, 2024]` (149 events), eval year = `[2025]` (24 events). The retrain plan (`g3-implementer-plan.json`, task `m2-retrain-wide`) specifies `--seed 0`. Same 23 features as G2. Differs from G2 control only by `--hidden-dim 384`.

4. **No leakage / harness fidelity:** `training_batches.json` confirms strict year separation (2025 held out of training). `diagnose_quali_same_pairs.py` has zero diff against HEAD (git diff empty). Harness stdout (`harness_g3_wide_stdout.txt`, line 27) confirms `race_weekend | 0.5880 (ev=18,p=3352) 0.7643 (p=3352)` — ceiling 0.7643 and pairs 3352 exactly match G2 control OOS values from `g2_numbers.json` (`ceiling_best_across_fp=0.7643`, `pairs=3352`). Shared-pairs set is identical.

5. **Verdict follows:** wide-net rw=0.5880 vs control rw=0.5868 → delta=+0.0012, well within ±0.02 threshold. `capacity_excluded=True` justified.

## Scope drift
None. All artifacts are confined to `.agent-work/451/**`. No `src/` edit was made. No gold cycle, no fusion, no harness fork, no promoted-default change. Specific exclusions respected.

## Evidence verdict
Evidence is present and sufficient:
- `g3_numbers.json`: structured evidence with all required keys (`hidden_dim`, `rw`, `ceiling`, `pairs`, `split`, `delta_vs_control`, `capacity_excluded`).
- `harness_g3_wide_stdout.txt`: captured harness output confirming line-level OOS numbers.
- `g3-implementer-result.md`: table comparing G3 vs G2 across rw, ceiling, pairs, events with deltas.
- `latent_power_manifest.json`: confirms `nn_hidden_dim=384` and `feature_dim=23` from trained bundle.
- `training_batches.json`: confirms split integrity (train 2018-2024, eval 2025, no leakage).

Cheap re-read: harness stdout line 27 independently confirms `0.5880 (ev=18,p=3352)` and `0.7643 (p=3352)` — numbers reproduce exactly.

Note: seed=0 appears in the plan (`m2-retrain-wide` imperative specifies `--seed 0`) and in `g3_numbers.json` notes. It is not stored in the manifest config field; this is a minor documentation gap in the trained artifact (low severity, observation only).

## Code/doc quality
No production code changed. Evidence files are complete, structured, and self-consistent. The implementer result table is clear and correctly references G2 control numbers. The verdict rationale in `g3_numbers.json` is accurate and appropriately defers final verdict to Commander.

## Map impact verdict
- **Evidence supports claimed change:** Yes. Harness stdout, manifest, and `g3_numbers.json` all corroborate: hidden_dim was tripled, feature count stayed at 23, OOS rw moved +0.0012 — consistent with the claim that capacity is not the bottleneck.
- **Constraints not violated:** The 23-feature as-is constraint was honored (no src edit, schema v2, feature_dim=23 in manifest). DB-only constraint honored (no FastF1 direct calls). Harness reused, not forked.
- **Notes match the diff:** Map Impact notes in the implementer result correctly state: structural anchor `nn_hidden_dim=384` confirmed, claim `capacity_excluded=True` produced, 23-feature constraint honored. Diff is .agent-work-only, which matches the notes.
- **Decision candidates surfaced:** Implementer correctly deferred final verdict to Commander. No authority overstepped.
- **Durable context routed:** The capacity exclusion finding feeds into the #451 hypothesis-elimination arc. No new architectural structure was introduced; no Cartographer routing required for this experiment artifact.

This is an experimental evidence artifact, not an architecture-significant change. Map impact notes are proportionate and accurate.

## Reconciliation check
No production code or architecture changed. No structural baseline drift. No contracts modified. Nothing to reconcile.

## Blockers
- none

## Out-of-scope observations
- The seed=0 flag is not persisted in the trained `latent_power_manifest.json` config object (it shows as NOT FOUND). This is a minor observability gap in the artifact format — reproducibility requires consulting the plan or evidence notes. Triage candidate for the manifest schema if cross-run reproducibility audits are needed in future.

## Workflow Feedback
- **Handoff gaps:** The handoff says "a cheap harness re-read on the existing records is encouraged" but gives no explicit command for it. The harness re-read was satisfied by reading the captured `harness_g3_wide_stdout.txt` directly (not re-running). The distinction between "re-run the harness" and "read the captured stdout" was ambiguous; I treated stdout inspection as sufficient, which it is for the stated purpose.
- **Context rediscovered:** The engine script referenced in the skill (`scripts/checklist_engine.py`) does not exist in the worktree or the skill bundle. I drove the survey manually (inline pass/fail per check) and reported this as a misfit per skill instruction. No behavior changed — the checks were rigorous — but the engine path was a dead reference.
- **Instructions improvised around:** `references/checklist-engine.md` was not found in the skill bundle. Drove survey manually through the 6 template checks (r0–r5) plus the 5 handoff-specific checks, recording pass/fail explicitly in this result rather than via engine commands.
- **What would have made this easier:** Either bundle the engine script into the skill or note that the engine path is optional/environment-dependent. The current wording ("drive it as a survey through the engine") implies the script is required, creating friction when it's absent.

## Return status
`complete`
