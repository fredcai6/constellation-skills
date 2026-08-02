# Review Result — G2 Feature-Ablation Retrain (issue #451, cmdr-451)

## Assigned Gate
`g2 — decisive feature-ablation retrain gate: CONTROL vs +PACE on §7.6.2 same-pairs harness, two splits`

## Result
`APPROVE`

## Handoff compliance
The gate asked for four retrains of `driver_quali_power_from_race_weekend` (CONTROL and +PACE, each on splitA and splitB), run through the §7.6.2 same-pairs harness unmodified, producing `g2_numbers.json` with headline and OOS numbers plus a clear direction claim. All deliverables are present and correct. The probe edit is left in place for reviewer inspection as specified. No exclusions were violated.

## Scope drift
None. `git status --porcelain` shows only `M src/evo_predictor/quali_power_adapter.py` plus untracked `.agent-work/451/`. The `params/` tree is clean (git status returns nothing for params/). No gold cycle, fusion, Piece-2, or committed defaults were touched. All trained bundles are under `.agent-work/451/scratch_runs/`. Scope is exactly as bounded.

## Evidence verdict
All required evidence is present and directly demonstrates the claimed behavior:
- `g2_numbers.json`: as_is_control, pace_feature, notes (with caveat), points_to keys all present.
- `harness_control_stdout.txt`: rw=0.6560 (headline), rw=0.5868 (OOS), pairs=23862/3352, ceilings=0.8061/0.7643.
- `harness_pace_stdout.txt`: rw=0.6792 (headline), rw=0.7700 (OOS), same pairs/ceilings.
- Four trained bundles with manifests confirming feature_dim (23 vs 24) and val_season_cutoff (2024 vs 2025).

The harness stdout files were read directly and the numbers in the evidence JSON match those outputs exactly.

## Code/doc quality
The probe edit is minimal (22 lines: 1 modified, 21 added), well-commented with `# PROBE g2 #451 — revert` markers throughout, and correctly implements a NaN-safe `min(qs_best_raw, lr_best_raw)` using the same fallback logic pattern as the existing `_nanmin2` in `sampled_runtime.py`. `min()` is used (not `max()`), which is the correct lower=faster idiom. The 0.0 fallback when both values are NaN is documented and appropriate for pairwise training (antisymmetric differences; 0.0 contributes no ordering signal). The schema version bump to `v3-probe` is correct and does not pollute any committed default.

## Map impact verdict

- **Evidence supports claimed change:** Yes. OOS harness stdout shows rw=0.7700 vs ceiling=0.7643 for +PACE, and rw=0.5868 for CONTROL on the same 3352 pairs. The +0.183 OOS lift is confirmed directly from the stdout files.
- **Constraints not violated:** Walk-forward discipline confirmed: splitA val_season_cutoff=2024 (train 2018-2023), splitB val_season_cutoff=2025 (train 2018-2024) from manifests. `qs_best_raw`/`lr_best_raw` traced to `practice_preprocessor/_lap_pipeline.py` which is explicitly FP/Sprint-practice-only, pre-Q. DB-only constraint respected.
- **Notes match the diff:** The Map Impact notes in `g2-implementer-result.md` correctly identify `_driver_vector`, `DRIVER_QUALI_POWER_FEATURE_NAMES`, and `DRIVER_QUALI_POWER_FEATURE_SCHEMA_VERSION` as the touched anchors, and correctly describe the feature_dim auto-propagation. No overstated or missing impact.
- **Decision candidates surfaced:** §7.6.3 C3 decision (representation fix touching a promoted default → Admiral float) is explicitly flagged for Commander/Admiral. Implementer correctly deferred the landing decision.
- **Durable context routed:** Triage candidates routed in implementer result: (1) full LOSO retrain for clean headline, (2) z-score variant, (3) missing-indicator consideration. These are appropriate triage entries for Cartographer/future work.

## Reconciliation check
No committed architecture divergence. The probe is branch-local; `feature_schema_version` is bumped to `v3-probe` only in the untracked scratch bundles and the modified-but-not-committed source file. The committed gold records and params remain at v2. Commander should revert the probe edit at integrate per the handoff instruction.

## Blockers
- none

## Out-of-scope observations
- **OOS rw=0.7700 slightly exceeds ceiling=0.7643**: On 18 events / 3352 pairs, this +0.0057 overshoot is likely within sampling variance, but the magnitude (+0.183 over CONTROL) is striking. Whether OOS-at-ceiling is sufficient to float an Admiral-level promotion decision for landing `cross_channel_min_pace` as a permanent feature is a Commander/Admiral call under §7.6.3 C3 — not a defect in this probe gate. Flagged as triage candidate tc1.
- **NaN fallback to 0.0 vs NaN**: The probe falls back to 0.0 (not NaN) when both raw values are missing, differing from `_nanmin2`. This is appropriate for probe purposes but may warrant a companion `_missing` indicator on production landing (codebase sparse-neutral pattern). Flagged as triage candidate tc2.
- **Headline +0.023 vs OOS +0.183 gap**: The gap (6 diluted years vs 1 pure year) is clearly explained. A full LOSO retrain of +PACE for a clean per-year-2024 headline contrast was correctly deferred as out of scope and flagged as triage candidate by the implementer.

## Workflow Feedback

- **Handoff gaps:** The handoff was well-structured with explicit close criteria and inspection commands. One minor gap: the handoff listed `--seed 0` as expected but the standard train CLI arguments (`--retro-root`, `--compound-prior-root`, `--db-root`) were not surfaced. Implementer documented these gaps in their own workflow feedback. For a reviewer verifying the run, this means the exact CLI invocation cannot be fully reconstructed from the handoff alone — only the manifests confirm seed/split indirectly.
- **Context rediscovered:** Had to trace `qs_best_raw`/`lr_best_raw` provenance through three files (`_assemble.py`, `_features.py`, `_lap_pipeline.py`) to confirm pre-Q sourcing. The handoff claimed FP-derivation but did not name the files. This is acceptable for a reviewer spot-check.
- **Instructions improvised around:** The skill references `references/checklist-engine.md` but that file does not exist in the installed skill directory. Used the engine source (`scripts/checklist_engine.py`) and the template JSON directly as the workbench reference — this is a complete substitute.
- **What would have made this easier:** A `commands_used.txt` artifact from the implementer listing the exact train/harness CLI invocations would let a reviewer spot-check one command end-to-end without reconstructing it. The harness stdout files are present and sufficient, but the full commands are absent from evidence (they appear in the implementer result prose but not as a runnable artifact).

## Return status
`complete`
