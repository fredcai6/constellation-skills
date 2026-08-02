# Implementer Handoff

## Gate
g3 — end-to-end plumbing (issue #369, work area `.agent-work/issue-369-pace-gap-form/`)

## Task
Wire the G2 `form_encoding` flag end to end: training, runtime, CLI, gold config, docs. Mirror the established pace_normalization plumbing pattern — inspect it first:
```bash
git diff main...origin/claude/compound-regime-feasibility -- src/evo_predictor/module_training_orchestration.py src/evo_predictor/run.py src/evo_predictor/data_adapter/_build.py src/evo_predictor/gold_cycle/runner_support.py configs/evo/gold_defaults.toml
```
(27 insertions; that branch is UNMERGED reference material — mirror its pattern, do not copy its content or depend on it.)

Sub-items, in dependency order:

**(a) Minimal training builder** — `src/evo_predictor/module_adapters/_common.py:286` `_build_recent_history_race_features` gains kwarg `recent_history_form_encoding: str = "position_quality"`. When `== "quali_pace_gap"` AND `task == "quali"`: call the G1 provider `build_quali_pace_gap_history(db, year, round_num)` (from `src.evo_predictor.quali_pace_gap_history`) once per event and set each driver's `quali_pace_gap_history_full` (per-driver list; driver absent from provider dict → all-nan list of length `round_num-1`, consistent with the provider's alignment). Default: field stays None, ZERO extra DB calls.

**(b) Training closures** — `src/evo_predictor/module_adapters/_training_builders.py:291,314` (`_make_training_driver_quali_recent_history`, `_make_training_constructor_quali_recent_history`): closures receive the encoding, pass it to `_build_recent_history_race_features`, and when `quali_pace_gap` construct `RecentHistoryFeatureConfig(form_encoding="quali_pace_gap")` and pass `config=` to the adapter build functions. Thread the kwarg through the generic call contract: `build_labeled_batches_for_module` and `prepare_module_training_data` (`src/evo_predictor/module_training_orchestration.py:214,303`) gain `recent_history_form_encoding: str = "position_quality"`, forwarded to closure calls the same way `race_start_target_lap` flows today (follow the pace_normalization diff's mechanism for the closure contract — all other modules' closures must keep working with the default; choose the same accept-and-ignore vs selective-forward mechanism the pattern uses).

**(c) Runtime feature path** — `src/evo_predictor/data_adapter/_build.py`: `build_race_features` / `build_all_race_features` / `build_multi_season_race_features` gain the same kwarg (default `"position_quality"`); when on, populate `quali_pace_gap_history_full` on each DriverFeatures via the G1 provider (mirroring how `quali_history_full` flows through `_assemble.py` — extend the assemble call chain the same way the pace_normalization diff extends it; default does zero extra DB work).

**(d) CLI** — `src/evo_predictor/run.py`: `--recent-history-form-encoding` (choices `position_quality|quali_pace_gap`, default `position_quality`) on `train-latent-power-module` AND `backtest-latent-power-module` subparsers, forwarded into their command paths to wherever each builds batches (training-data prep and/or race features). Follow the pace_normalization diff's placement.

**(e) Gold config** — `configs/evo/gold_defaults.toml`: knob in the `[data]` section style mirroring the pattern diff (e.g. `recent_history_form_encoding = "position_quality"`); validated in `gold_cycle/config.py` (invalid value → loud config error naming field+value); passed into per-module train args via `gold_cycle/runner_support.py:139` `_module_train_args` (mirror the pattern diff's one-liner).

**(f) Runtime encoding consistency (the design point — decide, implement, document)** — the two quali RH runtime closures (`src/evo_predictor/module_adapters/_runtime_builders.py:428,450`) currently call the adapters with no config (always v1). Requirements:
1. A v2-trained bundle must be served pace-gap features; a v1 bundle position-quality features.
2. Mismatch fails loudly naming module + expected/actual schema. NO silent fallback.

Recommended seam (use unless the code proves it wrong, and document what you chose in your result): the closures receive `config_overrides` (manifest module config) — read `form_encoding` from there to select the adapter config; then add a generic post-build check where the sampled runtime knows the bundle's recorded `feature_schema_version` (explore `sampled_runtime.py` / bundle hydration to find where both the bundle metadata and the produced batch's `feature_schema_version` are in scope) comparing produced vs bundle-recorded, raising with module name + both values on mismatch. If the bundle does NOT record feature_schema_version today, the manifest/bundle side may need to carry the encoding — pick the smallest seam that satisfies 1+2 and document it. Note: the runtime features must also BE there — when the manifest config says `quali_pace_gap`, the RaceFeatures handed to the closure must have the field populated; wire the flag from manifest module config through the sampled runtime's feature-build call path (c) covers the builder side.

**(g) Docs** — update `docs/evo/modules/recent_history_driver.md` and `docs/evo/modules/recent_history_constructor.md`: the `form_encoding` option, v2 schema strings/names, missingness semantics (DNS/no-valid-lap → missing not slowest), default unchanged, and how training/runtime consistency is enforced. Match each doc's existing structure/voice.

**(h) Tests** (extend existing test files where they exist; new files only if none fits):
- gold config validation: valid values accepted, invalid rejected loudly.
- CLI arg flow: parser accepts the flag, default correct (follow existing run.py CLI test conventions if present).
- builder behavior: `_build_recent_history_race_features` populates the field when on (provider stubbed/monkeypatched — no real DB needed), leaves None + makes no provider call when off; data_adapter builder same contract.
- runtime mismatch: v2-expected vs v1-produced (and inverse) raises naming module + schemas.
- closure encoding selection: quali RH training closure under `quali_pace_gap` produces v2 schema batch (stub db with classification + lap data fixtures, or monkeypatch the provider).

## Protected Intent
- **Default off = the entire system is bit-identical**: zero extra DB reads, all 12 production modules' batches byte-identical, full evo unit region green untouched.
- No silent fallback between encodings at runtime — mismatch is a loud failure.
- DB-only; provider is the single data path for gaps.
- Docs updated in the same gate (Documentation Authority).

## Test Mode
TDD required for logic (builder/closure/consistency-check behavior); test-after acceptable for pure arg-plumbing lines (CLI/config threading) provided the flow tests in (h) cover them.

## Close Criteria
- `py -m pytest tests/unit/evo_predictor -q` green (region; includes the default-identity proof).
- New tests from (h) green.
- `py -m src.utils.simplification_limits --paths <every touched file>` — PASS, except pre-existing violations you can prove baseline-identical via `git stash` round-trip (report them; do not fix unrelated functions).
- Pattern-diff conformance: same seams as pace_normalization, no new parallel mechanism.
- Docs updated and accurate against the code as committed.

## Allowed Scope
- `src/evo_predictor/module_adapters/_common.py`, `_training_builders.py`, `_runtime_builders.py`, `_registry.py` (only if closure-contract threading requires it)
- `src/evo_predictor/module_training_orchestration.py`
- `src/evo_predictor/data_adapter/` (`_build.py`, `_assemble.py`, `__init__.py` re-exports if needed)
- `src/evo_predictor/run.py`
- `src/evo_predictor/sampled_runtime.py` + bundle/manifest seam files ONLY as needed for (f) (e.g. `sampled_runtime_manifest_assembly.py`, `pipeline_manifest_v4.py`) — smallest change that satisfies the consistency requirement
- `configs/evo/gold_defaults.toml`, `src/evo_predictor/gold_cycle/config.py`, `src/evo_predictor/gold_cycle/runner_support.py`
- `docs/evo/modules/recent_history_driver.md`, `docs/evo/modules/recent_history_constructor.md`
- `tests/unit/evo_predictor/**` (and `tests/unit/evo_predictor/gold_cycle/` etc. as fits existing layout)

## Specific Exclusions
- The adapters themselves (`quali_recent_history_adapter.py`, `constructor_quali_recent_history_adapter.py`, `recent_history_adapter.py`) — frozen by G2
- `quali_pace_gap_history.py` and the DB layer — frozen by G1
- `src/latent_power/` entirely
- Race / race-start module behavior (their closures may only gain inert default-parameter threading if the contract change requires it — no behavior change)
- `params/gold/` artifacts and any committed report/manifest under `reports/`
- No default flip anywhere: every default is `position_quality`

## Constraints
- `py` not `python`; pyright-clean; per-file style.
- Time-dependent inputs keep the as-of contract (provider already enforces prior-rounds-only — do not add any "latest" fallback).
- The closure-contract change must not perturb non-quali modules: prove via the full region run.
- If the (f) seam forces a manifest schema change beyond adding an optional module-config key, STOP and return — that is a contract decision for the commander/human.

## Required Evidence
- pytest region output + new-test outputs.
- limits output (+ stash-proof for any pre-existing violations).
- A short DESIGN NOTE in the result: the (f) seam chosen, what carries the encoding, where the mismatch check lives, and why it cannot silently fall back.
- Doc diff summary (what changed in each module doc).

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor -q
py -m src.utils.simplification_limits --paths <touched files>
```

## Suggested Model Tier
stronger-leaning bounded — broad wiring with one design seam; mitigated by the pattern diff and frozen G1/G2 contracts.

## Authority
Human-confirmed problem statement: `.agent-work/issue-369-pace-gap-form/PROBLEM_STATEMENT.md`. Frozen: flag name/values, default, v2 schema strings, loud-mismatch requirement, doc targets. You choose: the (f) seam (within the stated bounds, documented), exact kwarg threading mechanism (mirroring the pattern), test placement. You must NOT decide alone: manifest schema changes beyond an optional key, default flips, touching frozen G1/G2 files, latent_power changes.

## Stop Conditions
Stop and return if: allowed scope must be exceeded, a frozen file needs editing, the (f) requirement cannot be satisfied without a manifest schema change beyond an optional module-config key, required evidence cannot be produced, or any non-quali module's behavior would change.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced (verbatim tails), the (f) DESIGN NOTE, assumptions used, stop conditions hit, out-of-scope observations.
