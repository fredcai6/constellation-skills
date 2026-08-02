# Implementer Handoff — G1: inherit-gold-fusion mode (flag-gated, test-led)

## Gate
g1-implement (execute.json, work-id cmdr-470, epic #453 / issue #470)

## Task
Add a **flag-gated inherit-gold-fusion mode** to the walk-forward backtest pipeline so a period trains
the 12 base modules only and INHERITS the live gold fusion + calibration instead of training fresh
per-period fusion. Default (flag OFF) must preserve the existing per-period-LOSO behavior exactly.

Concretely, in `src/evo_predictor/walkforward/`:

1. **`pipeline.py` `render_period_config`**: thread an `inherit_fusion: bool` parameter. When True, emit
   `emit_fusion_train_rows = "none"` (base modules only) instead of `"leave_one_season_out"`. Everything
   else in the config (anchor on alpha 0.5, quali_pace_gap, sigma calibration) stays identical.

2. **`pipeline.py` `_run_downstream`** (and `SubprocessPipeline.run_cutoff_period`): thread the same flag.
   When inherit mode is on:
   - DO NOT call `scripts/run_static_hierarchical_fusion_training.py`.
   - Assemble the period's trained manifest from the period's own gold details + the **LIVE gold fusion
     config** `params/gold/fusion/fusion.json` (and the live calibration is already baked into that
     fusion config) via `scripts/assemble_trained_sampled_runtime_manifest.py`
     (`--gold-details <period gold details> --fusion-config params/gold/fusion/fusion.json
     --output-manifest <period report dir>/...sampled_runtime_manifest.json`).
   - Then run `run_sampled_runtime_comparison.py` against that inherited-fusion trained manifest exactly
     as today (explicit `--default-manifest` = period gold manifest, `--trained-manifest` = the assembled
     inherited manifest, restricted to the period's rounds).
   - Make the live gold fusion path injectable (constructor arg / module constant, e.g.
     `LIVE_GOLD_FUSION_CONFIG = Path("params/gold/fusion/fusion.json")`) so tests can point at a fixture.

3. **ANCHOR PRESERVATION (the #440 anchor-drop bug — verify and fix).** `assemble_trained_manifest_from_gold_artifacts`
   in `src/evo_predictor/fusion_training/_manifest.py` currently rebuilds `stages` from scratch and does
   NOT copy `stages.quali.quali_pace_anchor` — so the trained manifest it writes DROPS the anchor, and the
   comparison (`sampled_runtime.py` reads `stage.quali_pace_anchor`) would score WITHOUT the anchor. Fix:
   `assemble_trained_manifest_from_gold_artifacts` must carry the `quali_pace_anchor` block (enabled +
   alpha) into the trained manifest's quali stage. Source it from the period's gold
   `*.sampled_runtime_manifest.json` (`stages.quali.quali_pace_anchor`) — add an optional
   `--source-manifest` / `source_manifest_path` input to the script + function for this. The period gold
   manifest already lives beside the gold details in the period report dir. Add a focused test asserting
   the assembled trained manifest carries `stages.quali.quali_pace_anchor.enabled=true, alpha=0.5` when the
   source gold manifest had it. NOTE: this fix benefits the existing LOSO flow too — keep the default flow
   passing the source manifest as well so both flows preserve the anchor (verify existing tests stay green).

4. **P0 at cutoff=0 under inherit mode.** Under inherit mode, P0 (rounds 1-6) must flow through the cutoff
   pipeline at cutoff=0 (NOT reuse `per_race_predictions`), so all 4 periods score on the identical
   sampled-runtime path. `periods.py build_periods()` currently makes P0 `cutoff=None,
   reuse_promoted_gold=True`, and `render_period_config` raises if `cutoff is None`. Add an inherit-mode
   period construction (e.g. `build_periods(inherit_fusion=False)` or a separate
   `build_inherit_periods()`) where P0 is `cutoff=0, reuse_promoted_gold=False, eval_round_range=(1,6),
   train_max_round=0, prior_through_round=0`. The orchestrator then routes P0 through `run_cutoff_period`.
   Leakage attestation still holds (train_max_round=0 < R, prior_through_round=0 < R for R1..6). The
   cutoff-0 gold-cycle config means `eval_year_train_through_round=0` / `eval_round_range=[1,6]` — confirm
   the gold-cycle research-mode config accepts cutoff 0 (no 2025 round joins training; pure 2018-2024 base).
   If cutoff=0 is rejected by the gold-cycle config validation, STOP and return (float the design) rather
   than hacking around it.

5. **CLI thread.** `scripts/run_walkforward_backtest.py`: add `--inherit-fusion` (default OFF). Pass it to
   the orchestrator -> pipeline and to period construction. With the flag OFF, the dry-run plan and the
   real run behave exactly as today.

## Protected Intent
Default behavior unchanged (existing harness + tests). The inherit path is the leakage-safe cheap flow the
walk-forward run opts into. The anchor must survive into every assembled trained manifest. No leakage:
as-of cutoffs and the enforced attestation must still hold.

## Test Mode
TEST-LED. Existing `tests/unit/evo_predictor/walkforward/*` MUST stay green (proves default unchanged).
Add unit tests for the inherit path. The heavy subprocess calls are mocked (see existing
`test_pipeline_downstream.py` `_FakeSubprocess` pattern) — no real training in tests.

## Close Criteria
- `render_period_config(..., inherit_fusion=True)` emits `emit_fusion_train_rows = "none"`; with
  `inherit_fusion=False` (default) emits `"leave_one_season_out"` (unchanged).
- `_run_downstream` in inherit mode does NOT invoke `run_static_hierarchical_fusion_training.py`, DOES
  invoke `assemble_trained_sampled_runtime_manifest.py` with `--fusion-config` pointing at the live gold
  fusion config, and still passes explicit period `--default-manifest`/`--trained-manifest` to the
  comparison restricted to the period's rounds.
- `assemble_trained_manifest_from_gold_artifacts` preserves `stages.quali.quali_pace_anchor` (enabled +
  alpha) from the source gold manifest into the trained manifest (anchor-drop bug fixed); tested.
- Inherit-mode periods route P0 through `run_cutoff_period` at cutoff=0; attestation passes for R1-6.
- `--inherit-fusion` CLI flag threads end to end, default OFF preserves existing behavior.
- Existing walkforward unit suite green; new inherit-path tests green.
- `py -m src.utils.simplification_limits` clean on every touched file; pyright clean on touched src.

## Allowed Scope
`src/evo_predictor/walkforward/{pipeline.py,orchestrator.py,periods.py}`,
`src/evo_predictor/fusion_training/_manifest.py`,
`scripts/{run_walkforward_backtest.py,assemble_trained_sampled_runtime_manifest.py}`,
`tests/unit/evo_predictor/walkforward/*` (+ a focused test for the assemble anchor fix, e.g.
`tests/unit/evo_predictor/` fusion_training test if one exists, else add one).

## Specific Exclusions
- Do NOT run the real walk-forward backtest (that is G2, commander-driven).
- Do NOT touch the canonical gold-cycle/full-refresh harness, `pipeline_validation`, or the multiseason
  backtest.
- Do NOT modify or regenerate `params/gold/` artifacts, nor `reports/walkforward/multiseason_fantasy.*`.
- Do NOT change the default-OFF behavior of any existing code path.

## Constraints
- `py` not `python`; utf-8 child env on any captured subprocess; PYTHONUTF8=1 for unicode-printing scripts.
- DB-only; as-of cutoffs strictly enforced; the enforced leakage attestation must still gate the run.
- One-canonical-path doctrine: the flag is a tracked dual path; default is the unchanged canonical one.
- Anchor alpha 0.5 preserved in every assembled manifest.

## Map Anchors (inbound)
- **Structural:** `src/evo_predictor/walkforward/pipeline.py` (render_period_config line ~159,
  _run_downstream lines ~295-365); `orchestrator.py` P0 routing; `periods.py` build_periods;
  `fusion_training/_manifest.py` assemble; `scripts/run_walkforward_backtest.py`;
  `scripts/assemble_trained_sampled_runtime_manifest.py`.
- **Capability:** walk-forward downstream alternate inherit path; `struct:evo.sampled_runtime` (scoring);
  `struct:evo.fusion` (inherited live gold fusion).
- **Constraints:** one-canonical-path (flag, default unchanged); leakage attestation holds; anchor preserved.
- **Decision anchors:** pre-confirmed single sampled-runtime path incl P0 at cutoff=0; baseline 829.
- **Evidence expectations:** existing walkforward suite green (default unchanged); new tests: inherit emits
  none + assembles from live gold fusion + anchor preserved + no fusion training call + P0 routes via cutoff.

## Required Evidence
- `py -m pytest tests/unit/evo_predictor/walkforward/ -q` output (all green).
- New inherit-path test output (green).
- `py -m src.utils.simplification_limits <touched files>` output (clean).
- pyright output on touched src (clean).
- A short note confirming the anchor-drop fix and the default-unchanged guarantee.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/walkforward/ -q
py -m pytest tests/unit/evo_predictor/ -q -k "manifest or fusion_training or assemble"
py -m src.utils.simplification_limits src/evo_predictor/walkforward/pipeline.py src/evo_predictor/walkforward/orchestrator.py src/evo_predictor/walkforward/periods.py src/evo_predictor/fusion_training/_manifest.py
```
(pyright: run the project's pyright invocation on the touched src files.)

## Suggested Model Tier
stronger — reason: multi-file thread (config/downstream/periods/CLI) + a subtle anchor-preservation fix in
a shared assembler with a default-unchanged guarantee; risk of silently breaking the existing flow.

## Authority
Single-path decision (sampled-runtime, P0 at cutoff=0, baseline 829) is MADE (Admiral pre-confirmed) — do
not re-litigate. You decide the exact flag plumbing and test structure. You may NOT: change default
behavior, run the real backtest, touch params/gold or multiseason_fantasy.*, or expand beyond the
inherit-fusion mode.

## Stop Conditions
Stop and return if: the gold-cycle research config rejects cutoff=0 (float the P0 design); the anchor fix
requires touching the comparison/scoring core beyond `_manifest.py` + the assemble script; allowed scope
must be exceeded; an exclusion must be touched; a decision outside this authority is needed.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced
(paste the verification command outputs), assumptions used, stop conditions hit, out-of-scope observations,
workflow feedback (what in this handoff or the workflow made the work harder than it needed to be).
