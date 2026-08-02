# Reviewer Handoff — G1: inherit-gold-fusion mode

## Gate
g1-review (work-id cmdr-470, epic #453 / issue #470)

## What was implemented
A flag-gated `--inherit-fusion` mode for the walk-forward 2025 backtest pipeline, default OFF. Built across
two implementer passes. Verify against the diff on branch `issue-470-walkforward` (MAIN checkout).

Files changed (tracked):
- `src/evo_predictor/walkforward/pipeline.py` — `render_period_config(inherit_fusion=...)` emits
  `emit_fusion_train_rows="none"` when True; `_run_downstream(inherit_fusion=...)` inherit branch skips
  fusion training and assembles from period gold details + LIVE gold fusion config
  (`LIVE_GOLD_FUSION_CONFIG = params/gold/fusion/fusion.json`, injectable) via the assemble script with
  `--source-manifest`; new `_run_p0_live_gold_scoring` runs ONLY the sampled-runtime comparison pointing
  both manifests at the live gold manifest (`LIVE_GOLD_MANIFEST = params/gold/sampled_runtime_manifest.json`)
  over R1-6; `run_cutoff_period` branches P0 to the live-gold-scoring path in inherit mode.
- `src/evo_predictor/walkforward/periods.py` — `Period.live_gold_p0` field; `build_inherit_periods()`
  (P0 reuse_promoted_gold=False, live_gold_p0=True, train_max_round=0, prior_through_round=0); default
  `build_periods()` UNCHANGED.
- `src/evo_predictor/walkforward/orchestrator.py` — `WalkforwardOrchestrator(inherit_fusion=...)`,
  `PipelinePort.run_cutoff_period(..., inherit_fusion=...)`; `run()` uses `build_inherit_periods()` in
  inherit mode (all 4 periods via cutoff pipeline), default mode unchanged.
- `src/evo_predictor/fusion_training/_manifest.py` — `assemble_trained_manifest_from_gold_artifacts(
  source_manifest_path=...)` now carries `stages.quali.quali_pace_anchor` from the source manifest into
  the trained manifest (anchor-drop fix). Refactored into helpers (fixes a pre-existing simpl violation).
- `scripts/assemble_trained_sampled_runtime_manifest.py` — `--source-manifest` arg.
- `scripts/run_walkforward_backtest.py` — `--inherit-fusion` CLI flag (default OFF), threaded to
  orchestrator + dry-run plan.
- Tests: `test_pipeline.py`, `test_orchestrator.py` updated; NEW `test_pipeline_inherit_fusion.py`,
  `test_p0_inherit_routing.py`.

## How to inspect the diff
```
git -C C:/Programs/f1Brainz diff -- src/evo_predictor/walkforward/ src/evo_predictor/fusion_training/_manifest.py scripts/run_walkforward_backtest.py scripts/assemble_trained_sampled_runtime_manifest.py
git -C C:/Programs/f1Brainz status --short
```
(IGNORE the pre-existing working-tree mods to docs/agents/CREW_CONTEXT.md + ORCHESTRATOR_CONTEXT.md — another session's, NOT part of this gate.)

## Task statement
Add the inherit-gold-fusion mode (cheap leakage-safe walk-forward downstream) flag-gated with default
behavior unchanged; preserve the quali pace anchor in every assembled trained manifest; under inherit mode
P0 (R1-6) scores the live gold manifest directly (no gold cycle), P1-P3 inherit the live gold fusion.

## Close criteria (verify each)
1. `render_period_config(inherit_fusion=True)` emits `emit_fusion_train_rows="none"`; `False` (default)
   emits `"leave_one_season_out"` (unchanged).
2. Inherit-mode `_run_downstream` for P1-P3 does NOT invoke `run_static_hierarchical_fusion_training.py`,
   DOES assemble with `--fusion-config` = live gold fusion config and `--source-manifest` = period gold
   manifest, and passes explicit period `--default-manifest`/`--trained-manifest` to the comparison
   restricted to the period rounds.
3. Inherit-mode P0 runs ONLY the sampled-runtime comparison with both manifests = the live gold manifest,
   restricted to R1-6; runs NO gold cycle / fusion / assemble; does NOT call `render_period_config`.
4. The anchor (`stages.quali.quali_pace_anchor`, enabled + alpha 0.5) is preserved in the assembled trained
   manifest when the source manifest carries it (anchor-drop bug fixed). Confirm BOTH the LOSO default path
   and the inherit path pass `--source-manifest`.
5. Default (`inherit_fusion=False`) behavior is byte-for-byte the prior behavior: `build_periods()`
   unchanged (P0 reuse_promoted_gold=True), existing 116 walkforward tests green.
6. Leakage attestation still holds: inherit-mode P0 rows have train_max_round=0 and prior_through_round=0
   (< R1..6); P1-P3 unchanged.
7. `gold_cycle/config.py` NOT modified (P0 avoids the cutoff>=1 validator by not running a gold cycle).
8. Tests green; simplification_limits + pyright clean on touched src.

## Constraints
- One-canonical-path doctrine honored: flag is a tracked dual path, default unchanged.
- DB-only; as-of cutoffs enforced; anchor alpha 0.5 preserved.

## Map anchors (inbound)
Inherits g1-implement anchors: `src/evo_predictor/walkforward/{pipeline,orchestrator,periods}.py`,
`fusion_training/_manifest.py`, the two scripts; `struct:evo.sampled_runtime`, `struct:evo.fusion`;
constraints one-canonical-path + leakage-attestation + anchor-preserved.

## Evidence from IMPLEMENTER_RESULT
- `py -m pytest tests/unit/evo_predictor/walkforward/ -q` → 153 passed (116 existing + 37 P0 + earlier
  inherit tests). Commander re-ran independently: 153 passed.
- `py -m src.utils.simplification_limits` on touched src → PASS.
- pyright on touched src → 0 errors. (`scripts/assemble_trained_sampled_runtime_manifest.py` has 2
  PRE-EXISTING pyright errors unrelated to this change — out of scope.)
- Result files: `.agent-work/cmdr-470/crew-handoffs/g1-implementer-result.md` and `...-result-p0.md`.

## Verification commands
```
py -m pytest tests/unit/evo_predictor/walkforward/ -q
py -m src.utils.simplification_limits src/evo_predictor/walkforward/pipeline.py src/evo_predictor/walkforward/orchestrator.py src/evo_predictor/walkforward/periods.py src/evo_predictor/fusion_training/_manifest.py
```

## Authority
The single-path decision (sampled-runtime, P0 = live gold over R1-6, baseline 829) and the Option-B P0
design are MADE (commander/Admiral) — do not re-litigate; verify the implementation matches them.

## Return Format
Return REVIEW_RESULT: verdict APPROVE or BLOCK, findings (per close criterion), any out-of-scope
observations, and workflow feedback. If BLOCK, name exactly what must change.
