# Implementation Result

## Assigned gate
Issue #470, item 4 — P0 routing under inherit mode (live-gold-scoring branch)

## Completed slice
Under `inherit_fusion=True`, the orchestrator now builds periods via `build_inherit_periods()`
where P0 carries `live_gold_p0=True` and `reuse_promoted_gold=False`. When
`run_cutoff_period` is called for that P0, it skips the gold cycle/fusion/assemble and runs
only `run_sampled_runtime_comparison.py` with both `--default-manifest` and
`--trained-manifest` pointing at the live gold manifest
(`params/gold/sampled_runtime_manifest.json`, injectable). The comparison is restricted to
R1-6 via `--race-name`. Results are extracted identically to P1-P3.

Default mode is unchanged: `build_periods()` P0 keeps `reuse_promoted_gold=True` and
`live_gold_p0=False`; the orchestrator's default `run()` routes P0 through `_p0_race_rows`
exactly as before.

## Scope
**Files changed:**
- `src/evo_predictor/walkforward/periods.py` — added `live_gold_p0: bool = False` field to `Period`; added `build_inherit_periods()`
- `src/evo_predictor/walkforward/pipeline.py` — added `LIVE_GOLD_MANIFEST` constant; added `live_gold_manifest` param to `SubprocessPipeline.__init__`; added `_run_p0_live_gold_scoring` method; updated `run_cutoff_period` to branch on `inherit_fusion and period.live_gold_p0`
- `src/evo_predictor/walkforward/orchestrator.py` — imported `build_inherit_periods`; updated `run()` to use `build_inherit_periods()` when `self._inherit_fusion`, with an inline docstring explaining both paths
- `tests/unit/evo_predictor/walkforward/test_p0_inherit_routing.py` — new test file (37 tests)

**Specific exclusions touched:** no — `gold_cycle/config.py` not touched, `render_period_config` not called for P0 in inherit mode, comparison/scoring core not touched.

## Behavior changed
Yes. Under `inherit_fusion=True` only:
- `WalkforwardOrchestrator.run()` now uses `build_inherit_periods()` which routes P0 through `run_cutoff_period` (not `_p0_race_rows`).
- `SubprocessPipeline.run_cutoff_period` for a `live_gold_p0=True` period runs ONLY the sampled-runtime comparison with the live gold manifest as both default and trained manifest; no gold cycle, no fusion training, no assemble.
- All four periods (P0 through P3) call `run_cutoff_period` in inherit mode; P0 gets the special live-gold-scoring path.

## Map Impact
- **Capabilities added/changed/affected:** walk-forward inherit-fusion mode now has a complete P0 path (was previously blocked because gold_cycle/config.py rejects cutoff=0). P0 in inherit mode scores the LIVE GOLD trained manifest directly — leakage-safe (train_max_round=0 < R, prior_through_round=0 < R for all R in 1..6).
- **Structural anchors touched:** `Period` dataclass gained `live_gold_p0: bool` field (default False); `SubprocessPipeline` gained `_live_gold_manifest`; new `build_inherit_periods()` exported from periods module.
- **Constraints/assumptions touched:** The gold_cycle/config.py validator constraint (`eval_year_train_through_round >= 1`) is honored — P0 in inherit mode never calls `render_period_config` or the gold cycle at all.
- **Decision candidates / resolved decisions:** Commander Option B implemented: P0 in inherit mode IS the no-in-season-retrain promoted gold, so it scores the LIVE GOLD manifest directly. No compromise.

## Test mode
**Required:** test-first (TDD)
**Satisfied:** yes — tests written first (RED: ImportError), then implementation (GREEN: 37 new tests pass), then verified existing 116 still pass (153 total).

## Evidence

```bash
py -m pytest tests/unit/evo_predictor/walkforward/ -q
```

**Result:** 153 passed in 4.25s (116 original + 37 new)

```bash
py -m src.utils.simplification_limits --paths src/evo_predictor/walkforward/pipeline.py src/evo_predictor/walkforward/orchestrator.py src/evo_predictor/walkforward/periods.py
```

**Result:** PASS (3 files checked)

```bash
py -m pyright src/evo_predictor/walkforward/pipeline.py src/evo_predictor/walkforward/orchestrator.py src/evo_predictor/walkforward/periods.py
```

**Result:** 0 errors, 0 warnings, 0 informations

## TDD evidence, if required

- Failing test observed: `ImportError: cannot import name 'build_inherit_periods'` (exit code 2, 0 items collected)
- Passing test observed: 37 passed in 0.30s after implementation
- Refactor while green: yes — docstrings, constant comments, and `_run_p0_live_gold_scoring` docstring refined while all tests stayed green

## Docs/contracts touched
- `src/evo_predictor/walkforward/periods.py` docstring for `Period.live_gold_p0` and `build_inherit_periods` are new inline docs that form the contract for future callers.
- `src/evo_predictor/walkforward/pipeline.py` `LIVE_GOLD_MANIFEST` constant comment and `_run_p0_live_gold_scoring` docstring are the internal contract.
- `src/evo_predictor/walkforward/orchestrator.py` `run()` docstring extended to explain both default and inherit-mode routing.

## Assumptions
- The live gold manifest at `params/gold/sampled_runtime_manifest.json` is the correct artifact to score P0 against in inherit mode (confirmed by Commander Option B decision).
- Scoring P0 with both `--default-manifest` and `--trained-manifest` pointing at the same live gold manifest is valid: the comparison will show zero delta between default and trained (they are the same), but per-round position distributions are still produced from that manifest for scoring.
- `_build_prior_root` is called for the P0 live-gold-scoring path to maintain a consistent compound-prior root (2018-2024 cross-season), matching what P1-P3 use.

## Stop conditions hit
None. All implementation stayed within `pipeline.py`, `orchestrator.py`, and `periods.py`. `gold_cycle/config.py` not touched. Comparison/scoring core not touched.

## Out-of-scope observations
- The `_run_p0_live_gold_scoring` method builds the prior root (copies 2018-2024 dirs from gold) but the live-gold manifest's embedded module paths already point at the committed `params/gold/runtime_bundles/`. The comparison script presumably uses `--compound-prior-root` separately; this is consistent with how P1-P3 pass `--compound-prior-root` and is not a deviation.
- `test_p0_inherit_routing.py:TestInheritP0LiveGoldScoringBranch._run_p0_inherit` creates the `_FakeSubprocessP0` result (comparison output) to cover R1-6. A real run will produce a `*.trained.json` from the comparison with all 6 rounds.

## Workflow Feedback
- **Handoff gaps:** The handoff correctly named `LIVE_GOLD_MANIFEST` as the injectable but did not specify a default value path — had to infer `params/gold/sampled_runtime_manifest.json` from the spec prose. The spec prose confirmed it ("the live gold manifest `params/gold/sampled_runtime_manifest.json`"), so this was not a blocker, just a cross-reference.
- **Context rediscovered:** The `Period.live_gold_p0` field approach was the clean way to signal the P0 branch without touching `render_period_config`'s `cutoff is None` guard or passing any special sentinel cutoff value. The handoff said "keep `render_period_config` OUT of the P0 path" without specifying the marker pattern — the dataclass field was the natural fit given the frozen dataclass.
- **Instructions improvised around:** The checklist engine path (`scripts/checklist_engine.py`) was not found in the skill directory — drove plan inline rather than through the engine. Used the skill's template fields and stage structure (m0-context, implement, verify) as the mental model without the engine binary.
- **What would have made this easier:** A pre-filled `Period` field table showing which fields are new vs. existing in the handoff would save one file-read. The handoff was otherwise unusually complete and made implementation straightforward.

## Return status
complete
