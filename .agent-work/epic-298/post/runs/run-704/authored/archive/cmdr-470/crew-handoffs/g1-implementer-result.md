# Implementation Result

## Assigned gate
`g1-implement (execute.json, work-id cmdr-470, epic #453 / issue #470)`

## Completed slice
Items 1, 2, 3, 5 from the handoff completed. Item 4 (P0 routing at cutoff=0) is BLOCKED by a stop condition — see below.

Specifically:
- **Anchor-drop fix** (`_manifest.py`): `assemble_trained_manifest_from_gold_artifacts` now accepts `source_manifest_path`; when provided, reads `stages.quali.quali_pace_anchor` from the source and injects it into both the default and trained stages. Three new private helpers extracted: `_load_source_quali_pace_anchor`, `_build_module_map`, `_build_default_stages`, `_apply_fusion_config` (also fixes the pre-existing simplification_limits violation on this function).
- **Config flag** (`pipeline.py`): `render_period_config` accepts `inherit_fusion: bool = False`. When `True`, emits `emit_fusion_train_rows = "none"`. Default `False` unchanged.
- **Downstream flag** (`pipeline.py`): `_run_downstream` accepts `inherit_fusion: bool = False`. Extracted two branch helpers (`_assemble_trained_manifest_loso`, `_assemble_trained_manifest_inherit`). In inherit mode: skips `run_static_hierarchical_fusion_training.py`, calls `assemble_trained_sampled_runtime_manifest.py` with `--fusion-config` pointing at `self._live_gold_fusion_config` (injectable) and `--source-manifest` pointing at the period gold manifest. Both paths now pass `--source-manifest` (anchor fix on both flows). `LIVE_GOLD_FUSION_CONFIG = Path("params/gold/fusion/fusion.json")` constant exported.
- **Orchestrator** (`orchestrator.py`): `PipelinePort.run_cutoff_period` protocol and `WalkforwardOrchestrator.__init__` accept `inherit_fusion: bool = False`. `_cutoff_race_rows` passes it through.
- **CLI** (`run_walkforward_backtest.py`): `--inherit-fusion` flag added (default OFF). Threads to orchestrator and to `build_dry_run_plan`. Dry-run plan includes `"inherit_fusion"` key.
- **Assemble script** (`assemble_trained_sampled_runtime_manifest.py`): `--source-manifest` argument added; passed to the function.
- **Tests** (`test_pipeline.py`): 3 new tests for `render_period_config` with `inherit_fusion=True/False`.
- **Tests** (`test_pipeline_inherit_fusion.py`): 15 new tests covering inherit-mode subprocess wiring, live-fusion-config injection, anchor preservation, and default-mode unchanged.
- **Tests** (`test_orchestrator.py`): existing mock pipelines updated to accept `inherit_fusion` kwarg (backward-compatible).

## Stop condition hit: P0 at cutoff=0 (item 4)

The gold-cycle config validation at `src/evo_predictor/gold_cycle/config.py` line 256-258 requires `eval_year_train_through_round >= 1`. Cutoff=0 would require emitting `eval_year_train_through_round = 0` which fails the validator with:

```
data.eval_year_train_through_round must be >= 1; got 0.
```

Per handoff stop condition: "If cutoff=0 is rejected by the gold-cycle config validation, STOP and return (float the design) rather than hacking around it." This stop condition was hit. P0 routing via cutoff=0 is not implemented. **Under inherit mode, P0 still reuses `per_race_predictions`** (the default `reuse_promoted_gold=True` path — unchanged).

Design note for Commander: Options are (a) relax the validator to accept 0 for research mode (touching `gold_cycle/config.py`, outside my scope), (b) run P0 with a special "no gold cycle" path that goes straight to assemble from the live gold details + live fusion config without a gold cycle run at all, or (c) accept that P0 stays on the reuse path under inherit mode (the three retrained periods P1-P3 still benefit from inherit-fusion).

## Scope

**Files changed:**
- `src/evo_predictor/fusion_training/_manifest.py` — anchor-drop fix, 4 new helpers
- `src/evo_predictor/walkforward/pipeline.py` — `inherit_fusion` flag, `LIVE_GOLD_FUSION_CONFIG`, `_assemble_trained_manifest_loso`, `_assemble_trained_manifest_inherit`, refactored `_run_downstream`
- `src/evo_predictor/walkforward/orchestrator.py` — `inherit_fusion` parameter on `PipelinePort` protocol + `WalkforwardOrchestrator`
- `src/evo_predictor/walkforward/periods.py` — no changes (periods.py untouched; P0 period build unchanged)
- `scripts/assemble_trained_sampled_runtime_manifest.py` — `--source-manifest` argument
- `scripts/run_walkforward_backtest.py` — `--inherit-fusion` flag, `build_dry_run_plan` updated
- `tests/unit/evo_predictor/walkforward/test_pipeline.py` — 3 new tests added
- `tests/unit/evo_predictor/walkforward/test_orchestrator.py` — mock pipelines accept `inherit_fusion` kwarg
- `tests/unit/evo_predictor/walkforward/test_pipeline_inherit_fusion.py` — NEW file, 15 tests

**Specific exclusions touched:** no — `periods.py` is listed in scope but was untouched (P0 routing blocked). No gold-cycle config, no comparison/scoring core, no params/gold, no multiseason_fantasy.

## Behavior changed
Yes. New `--inherit-fusion` flag enables an alternate per-period downstream path in `SubprocessPipeline`. Default OFF leaves all existing behavior unchanged. Anchor-drop bug fixed for both LOSO (default) and inherit paths via `--source-manifest` being passed in both branches of `_run_downstream`.

## Map Impact

- **Structural anchors touched:**
  - `src/evo_predictor/walkforward/pipeline.py` — `render_period_config` (new `inherit_fusion` param, line ~104); `_run_downstream` extracted into two branch helpers (lines ~324-428 area); new `LIVE_GOLD_FUSION_CONFIG` constant; new `SubprocessPipeline(live_gold_fusion_config=...)` constructor arg
  - `src/evo_predictor/walkforward/orchestrator.py` — `PipelinePort` protocol updated; `WalkforwardOrchestrator` new `inherit_fusion` constructor param
  - `src/evo_predictor/fusion_training/_manifest.py` — `assemble_trained_manifest_from_gold_artifacts` new `source_manifest_path` param; 4 private helpers extracted (also fixes pre-existing simplification_limits violation)
  - `scripts/assemble_trained_sampled_runtime_manifest.py` — `--source-manifest` CLI arg

- **Capabilities added/changed/affected:**
  - `capability:walkforward.inherit-fusion-mode` — new dual path: per-period trains base modules only (`emit_fusion_train_rows="none"`), inherits live gold fusion + calibration, assembles trained manifest directly; gated by `--inherit-fusion` flag
  - `capability:walkforward.anchor-preservation` — anchor now preserved in BOTH paths (LOSO and inherit) via `--source-manifest` on the assemble step; previously dropped silently

- **Constraints/assumptions touched:**
  - `constraint:one-canonical-path` — honored: flag is tracked dual path, default is unchanged canonical
  - `constraint:leakage-attestation` — honored: train_max_round and prior_through_round unchanged for P1-P3; P0 still on reuse path
  - `constraint:anchor-alpha-0.5` — now enforced via `--source-manifest`; carried from gold manifest into trained manifest

- **Decision candidates / resolved decisions:**
  - P0 at cutoff=0 BLOCKED: gold-cycle config rejects `eval_year_train_through_round < 1`. Commander must decide the redesign.

- **Claims/evidence produced:**
  - Inherit mode does NOT call fusion training: `TestInheritModeSkipsFusionTraining::test_fusion_training_script_not_called` ✓
  - Inherit mode assembles from live gold fusion config: `TestInheritModeUsesLiveGoldFusion` ✓
  - Anchor preserved from source manifest: `TestAnchorDropFix::test_anchor_carried_when_source_manifest_provided` ✓
  - Default mode unchanged: `TestDefaultModeUnchanged` ✓ + all 98 original tests green

- **Triage candidates:**
  - P0 at cutoff=0 design blocked by gold-cycle config `eval_year_train_through_round >= 1` constraint; needs Commander decision on redesign approach

## Test mode
**Required:** TEST-LED (TDD)
**Satisfied:** yes — existing tests confirmed green before changes (98 tests); new tests added for all specified behaviors; all run green

## Evidence

```bash
py -m pytest tests/unit/evo_predictor/walkforward/ -q
```

**Result:** 116 passed (98 original + 18 new) in 3.93s

```
tests\unit\evo_predictor\walkforward\test_as_of_cutoff.py .............. [ 12%]
.......                                                                  [ 18%]
tests\unit\evo_predictor\walkforward\test_multiseason.py ....            [ 21%]
tests\unit\evo_predictor\walkforward\test_orchestrator.py .............. [ 33%]
.............                                                            [ 44%]
tests\unit\evo_predictor\walkforward\test_pipeline.py .................. [ 60%]
..                                                                       [ 62%]
tests\unit\evo_predictor\walkforward\test_pipeline_downstream.py .....   [ 66%]
tests\unit\evo_predictor\walkforward\test_pipeline_inherit_fusion.py ... [ 68%]
............                                                             [ 79%]
tests\unit\evo_predictor\walkforward\test_run_scripts.py ..............  [ 91%]
tests\unit\evo_predictor\walkforward\test_runner_cutoff_wiring.py ...... [ 96%]
....                                                                     [100%]
116 passed in 3.93s
```

```bash
py -m pytest tests/unit/evo_predictor/ -q -k "manifest or fusion_training or assemble"
```
**Result:** 166 passed, 1627 deselected, 45 warnings

```bash
py -m src.utils.simplification_limits --paths src/evo_predictor/walkforward/pipeline.py src/evo_predictor/walkforward/orchestrator.py src/evo_predictor/walkforward/periods.py src/evo_predictor/fusion_training/_manifest.py
```
**Result:** `PASS (4 files checked)`

```bash
py -m pyright src/evo_predictor/walkforward/pipeline.py src/evo_predictor/walkforward/orchestrator.py src/evo_predictor/walkforward/periods.py src/evo_predictor/fusion_training/_manifest.py
```
**Result:** `0 errors, 0 warnings, 0 informations`

Note: `scripts/assemble_trained_sampled_runtime_manifest.py` has 2 pre-existing pyright errors (None-typed discovery paths assigned to `str | Path` params). These are unchanged from before my edits (verified by stash-and-check). Pyright coverage is `src/` only (pyrightconfig.json `include: ["src"]`).

## TDD evidence

- Failing test observed: ran `py -m pytest tests/unit/evo_predictor/walkforward/test_pipeline_inherit_fusion.py` BEFORE writing implementation → `ImportError`/`AttributeError` on missing `LIVE_GOLD_FUSION_CONFIG`, `inherit_fusion` param, and `source_manifest_path` arg
- Passing test observed: all 15 new tests green after implementation
- Refactor while green: yes — extracted helpers for simplification_limits compliance; all 116 tests still green after refactor

## Docs/contracts touched
- None (no doc files changed)

## Assumptions
- `periods.py` is formally in scope but zero changes needed for items 1/2/3/5 (P0 routing blocked). Left untouched.
- Both `_assemble_trained_manifest_loso` and `_assemble_trained_manifest_inherit` now pass `--source-manifest` (period gold manifest) to the assemble script. This is the correct anchor-fix behavior for both paths.
- Inherit mode names the trained manifest `inherited_fusion.sampled_runtime_manifest.json` (a fixed, non-slug name). This is unambiguous since there is exactly one such file per period dir and the comparison is given the explicit path.

## Stop conditions hit
- **cutoff=0 rejected**: `src/evo_predictor/gold_cycle/config.py` line 256-258 validates `eval_year_train_through_round >= 1`. P0 at cutoff=0 under inherit mode cannot run a gold cycle with this constraint. Item 4 (P0 routing in inherit mode) not implemented. Float to Commander for redesign.

## Out-of-scope observations
- `src/evo_predictor/fusion_training/_manifest.py` had a pre-existing `function_lines=137` simplification_limits violation on `assemble_trained_manifest_from_gold_artifacts` before this change. My refactoring (needed to stay under limits after adding anchor logic) fixed it by extracting 4 private helpers. The function is now 60 lines.
- The gold-cycle config `eval_year_train_through_round >= 1` constraint may be relaxed safely for research mode (it only guards against invalid in-season cutoff semantics, and cutoff=0 is semantically valid: "no 2025 rounds in training"). This is a bounded change to `gold_cycle/config.py` that could unblock P0 routing.

## Workflow Feedback

- **Handoff gaps:** Item 4 says "STOP and return if gold-cycle research config rejects cutoff=0" but doesn't say whether to proceed with items 1/2/3/5 first. I inferred "proceed on the independent items, flag the stop on item 4" — this was reasonable but the handoff could be clearer: "if P0 routing blocked, continue with remaining independent items and flag".
- **Context rediscovered:** Had to grep for the exact validation line in `gold_cycle/config.py` (line 256-258) to confirm the stop condition. The handoff didn't carry the exact validator location, only that it "may reject" cutoff=0.
- **Instructions improvised around:** The handoff says "add unit tests for the inherit path ... follow the existing test_pipeline_downstream.py _FakeSubprocess pattern." I created a new file `test_pipeline_inherit_fusion.py` rather than appending to `test_pipeline_downstream.py` — the file was already long and the inherit tests are a separate concern. This is a style choice that fits the existing pattern of one-concern-per-file in the walkforward test suite.
- **What would have made this easier:** A note that the two pyright errors in `scripts/assemble_trained_sampled_runtime_manifest.py` are pre-existing and out of scope would have saved the verification stash cycle.

## Return status
`partial` — items 1, 2, 3, 5 complete; item 4 (P0 at cutoff=0) blocked by stop condition.
