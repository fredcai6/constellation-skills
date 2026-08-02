# Review Result

## Assigned Gate
`g1-review (work-id cmdr-470, epic #453 / issue #470)`

## Result
`APPROVE`

verdict: APPROVE

## Handoff compliance
All 8 close criteria satisfied across the two-pass implementation (g1-implement partial + g1-implement-p0 complete). The change does exactly what the handoff asked: `--inherit-fusion` flag added (default OFF), P1-P3 skip per-period fusion training and assemble from period gold details + live gold fusion config with `--source-manifest`, P0 in inherit mode runs only the sampled-runtime comparison against the live gold manifest over R1-6. Default behavior provably unchanged. Anchor-drop bug fixed for both paths.

## Scope drift
No scope drift. Modified files match declared scope exactly: `pipeline.py`, `orchestrator.py`, `periods.py`, `_manifest.py`, `run_walkforward_backtest.py`, `assemble_trained_sampled_runtime_manifest.py`, `test_pipeline.py`, `test_orchestrator.py` (modified), plus two new test files. Specific exclusion confirmed: `git diff -- src/evo_predictor/gold_cycle/config.py` returns empty. Pre-existing working-tree mods to `docs/agents/CREW_CONTEXT.md` and `ORCHESTRATOR_CONTEXT.md` are a prior session's changes per handoff instructions — correctly ignored.

## Evidence verdict
Evidence present and independently verified by reviewer:
- `py -m pytest tests/unit/evo_predictor/walkforward/ -q` → 153 passed in 4.41s (reviewer-run, matches implementer claim).
- `py -m src.utils.simplification_limits --paths [4 files]` → PASS (reviewer-run).
- pyright on `src/` = 0 errors. The 2 pre-existing pyright errors in `scripts/assemble_trained_sampled_runtime_manifest.py` are out of scope (excluded from `pyrightconfig.json include`; implementer verified pre-existing via stash check).
- TDD evidence in both implementer results: ImportError → red test → green implementation → refactor-while-green.

## Code/doc quality
Code quality is good. `_manifest.py` was correctly refactored into 4 private helpers to fix a pre-existing simplification_limits violation (function_lines was 137, now 60). `render_period_config` cleanly emits the correct TOML value. `_run_p0_live_gold_scoring` is clearly separated from `_run_downstream`. Docstrings on new helpers are adequate. No silent dual-format acceptance, no hidden fallback, no impure cache. Inline docs in `periods.py` (`Period.live_gold_p0`, `build_inherit_periods`) form a clear contract for future callers.

## Map impact verdict

- **Evidence supports claimed change:** Yes. `capability:walkforward.inherit-fusion-mode` is backed by tests in `test_pipeline_inherit_fusion.py` (15 tests) and `test_p0_inherit_routing.py` (37 tests). `capability:walkforward.anchor-preservation` is backed by `TestAnchorDropFix::test_anchor_carried_when_source_manifest_provided`. Default mode unchanged backed by 116 original tests green.
- **Constraints not violated:** `constraint:one-canonical-path` — flag is tracked dual path, default canonical unchanged. `constraint:leakage-attestation` — P0 inherit has `train_max_round=0`, `prior_through_round=0`, both < R1..6. `constraint:anchor-alpha-0.5` — now enforced via `--source-manifest` on both paths.
- **Notes match the diff:** Structural anchors named in Map Impact accurately match the diff (all 4 files, correct function/constant names). Capabilities and constraints accurately described. No overstated or missing structural impact.
- **Decision candidates surfaced:** P0 at cutoff=0 blocked by gold-cycle config validator was correctly surfaced in pass 1 and resolved via Commander Option B in pass 2. No unilateral decisions made by implementer on design questions.
- **Durable context routed:** Map Impact notes route capabilities and constraints correctly. Triage candidate (gold_cycle config `eval_year_train_through_round >= 1` as possible future relaxation) noted in implementer result.

## Reconciliation check
No architecture drift requiring Cartographer flag. `docs/architecture/index.md` not checked in this review — the change adds a new flag-gated path within existing walkforward module boundaries with no new module seams, no new public DB patterns, and no new config schemas. The `build_inherit_periods()` export and `Period.live_gold_p0` field are additive and documented inline. The Map Impact notes are sufficient for Cartographer to pick up the new capability anchors at next reconcile.

## Blockers
None.

## Out-of-scope observations
- The `_run_p0_live_gold_scoring` method calls `_build_prior_root` (copies 2018-2024 gold priors) even though the live gold manifest's embedded module paths already point at `params/gold/runtime_bundles/`. This is consistent with how P1-P3 pass `--compound-prior-root` and the comparison script uses it separately — not a bug, but worth noting in case the prior-root copy is ever found redundant for P0.
- The inherit-mode trained manifest name `inherited_fusion.sampled_runtime_manifest.json` is a fixed non-slug name. This is unambiguous (one file per period dir) and the comparison is given the explicit path. Minor naming inconsistency vs. P1-P3's fusion-slug naming; acceptable for a research mode.
- `run_walkforward_backtest.py`'s `build_dry_run_plan` only uses `build_periods()` (not `build_inherit_periods()`) for the dry-run period list regardless of `inherit_fusion`. The plan output will list the default P0 reuse path even in inherit-fusion dry run. This is cosmetic (the real run uses the correct period builder) but could mislead a dry-run reader. Triage candidate for a future cleanup issue.

## Workflow Feedback

- **Handoff gaps:** The handoff's close criterion CC3 says "does NOT call `render_period_config`" — verifying this required reading `run_cutoff_period` to confirm the early-return branch before the `render_period_config` call. The handoff could name the exact line/condition for faster targeted verification. Minor friction, not a blocker.
- **Context rediscovered:** Had to verify that `build_dry_run_plan` still only calls `build_periods()` (not `build_inherit_periods()`) even when `inherit_fusion=True` — this is the out-of-scope observation above. The handoff didn't mention dry-run plan behavior, which is a small blind spot.
- **Instructions improvised around:** The skill references `references/checklist-engine.md` but that file does not exist in the installed skill directory (only `scripts/checklist_engine.py` and `templates/`). I read the engine source directly instead. The engine worked correctly; no behavioral impact. The missing reference file is a skill packaging gap.
- **What would have made this easier:** A note in the handoff that `build_dry_run_plan` intentionally uses `build_periods()` only (cosmetic dry-run limitation) would have saved a confirmatory check. The handoff was otherwise unusually thorough and made the review straightforward.

## Return status
`complete`
