# Reviewer Handoff — G1 (issue #420)

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch `constellation/issue-420-quali-anchor-production`. Python `py`.
`PYTHONIOENCODING=utf-8`. Read `docs/agents/CREW_CONTEXT.md` + `GLOSSARY.md`.
You are an INDEPENDENT reviewer — verify by reading the diff and re-deriving, do
NOT trust the implementer's narrative.

## Gate
`g1`

## What Was Implemented
A production cross-channel pace anchor for the race_weekend quali head: at
inference, blend the head's per-module latent field `pi` with a within-event
z-standardized practice min-sector pace (`qs_best_raw`), behind a config key
(default OFF). Pure blend fn + config threading + attach in the runtime stage
loop.

## How to Inspect the Diff
```bash
git status --short
git diff src/evo_predictor/sampled_runtime.py
git diff src/evo_predictor/pipeline_manifest_v4.py
git diff src/evo_predictor/sampled_runtime_manifest_assembly.py
git diff src/evo_predictor/gold_cycle/config.py src/evo_predictor/gold_cycle/runner.py src/evo_predictor/run.py
git diff configs/evo/gold_defaults.toml
git diff tests/unit/evo_predictor/test_pipeline_manifest_v4.py
```
New files: `src/evo_predictor/quali_pace_anchor.py`,
`tests/unit/evo_predictor/test_quali_pace_anchor.py` (read directly).

## Task Statement (what it was supposed to build)
See the measured basis: §7.6.3 of `docs/evo/prediction_ceiling_and_priorities.md`
(do NOT edit that doc). Per event, pi-space (higher pi = faster):
`pi' = (1-alpha)*z(pi) + alpha*z(-anchor)`, anchor = practice min-sector pace
(lower seconds=faster). Attach must be INSIDE the race_weekend quali head's
per-module output path (pre-fusion), gated to that ONE module + quali task,
default OFF, no-op when disabled, alpha=0 an exact no-op.

## Close Criteria (each a review check)
1. **ATTACH POINT (critical — already failed once):** the blend is applied to
   the PER-MODULE race_weekend head's `ModuleFieldResult.pi` INSIDE `_run_stage`,
   BEFORE `fuse_module_fields_ordered`. There must be NO blend on the FUSED quali
   field (no anchor call in `predict_from_features` on `quali_fused`). Confirm by
   reading `sampled_runtime.py`. BLOCK if the attach is post-fusion.
2. **Gating exact:** applied only when `task=="quali"` AND config enabled AND
   `module_name == DRIVER_QUALI_POWER_FROM_RACE_WEEKEND` (constant imported from
   `src.latent_power.modules`, not a loose string). recent_history quali head and
   constructor head are NOT anchored. race/race_start stages untouched.
3. **Blend math + sign:** read `quali_pace_anchor.py`. Verify
   `pi' = (1-a)z(pi) + a z(-anchor)`; anchor negated so lower-seconds→higher-pi
   (a sign error would WORSEN ordering — this is the correctness crux). alpha=0
   returns pi unchanged (exact). alpha=1 = z(-anchor) ordering. Re-derive on a
   tiny example: 3 drivers, pi=[0.0,1.0,2.0] (driver C fastest by head), anchor
   seconds=[80.0, 79.0, 85.0] (driver B fastest by pace). At alpha=1 the blended
   order must rank B fastest (highest pi'). Confirm the test suite asserts an
   ordering-flip of this kind.
4. **Missingness explicit:** NaN/non-finite anchor drivers excluded from anchor
   z-stats AND kept in output (shape N), no silent impute/zero. <2 valid anchors
   → pi unchanged. std==0 guarded for both terms.
5. **Input validation:** mismatched lengths and bad alpha raise ValueError naming
   field/expectation/actual.
6. **Config chain complete + OFF by default:** `quali_pace_anchor_enabled`
   (default false) + `quali_pace_anchor_alpha` (default 0.5) in
   `gold_defaults.toml`; validated in `gold_cycle/config.py`; echoed into the
   QUALI stage of the assembled manifest (`sampled_runtime_manifest_assembly.py`);
   parsed in `pipeline_manifest_v4.py` (`QualiPaceAnchorConfig`) with ABSENT key
   → disabled (back-compat for old committed manifests — must be tested).
   Names use the `quali_pace_anchor_` prefix (no collision with fusion keys).
7. **Boundary:** NO edits to `fusion.py`, `fusion_training/**`,
   `scripts/fusion_replay/**`, `docs/evo/fusion_rework_findings.md`,
   `scripts/scope_quali_anchor_414.py`, or
   `docs/evo/prediction_ceiling_and_priorities.md`. The new config dataclass is
   NOT in fusion.py.
8. **sigma_pi:** left unchanged in this gate, documented in a comment.
9. **Tests synthetic-only:** the new tests must NOT depend on generated records
   or DBs. Run them.
10. **simplification_limits:** clean on touched paths EXCEPT the pre-existing
    `predict_from_features` 153-line violation (acceptable; it predates this work
    and the fix did not worsen it). `quali_pace_anchor.py` and `_run_stage` clean.

## Allowed Scope (what impl was permitted to touch)
`quali_pace_anchor.py` (new), `sampled_runtime.py`, `pipeline_manifest_v4.py`,
`sampled_runtime_manifest_assembly.py`, `gold_cycle/config.py`,
`gold_cycle/runner.py`, `run.py`, `gold_defaults.toml`, and test files.

## Specific Exclusions (flag if touched)
fusion.py, fusion_training/**, scripts/fusion_replay/**, fusion_rework_findings.md,
scope_quali_anchor_414.py, prediction_ceiling_and_priorities.md, race/race_start
behavior.

## Constraints (each a review check)
- DB-only canon: anchor from an existing in-`RaceFeatures` feature; no new DB
  read; no FastF1.
- Missingness explicit; one canonical path; tunable alpha in config not inlined.

## Evidence Produced (verify by re-running)
```bash
py -m pytest tests/unit/evo_predictor/test_quali_pace_anchor.py tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/evo_predictor/test_pipeline_manifest_v4.py -q
py -m pytest tests/unit/evo_predictor/ -q
py -m src.utils.simplification_limits src/evo_predictor/quali_pace_anchor.py src/evo_predictor/sampled_runtime.py src/evo_predictor/pipeline_manifest_v4.py src/evo_predictor/sampled_runtime_manifest_assembly.py src/evo_predictor/gold_cycle/config.py
```
Implementer claims: 1553 passed / 19 skipped; simplification clean except the
pre-existing 153-line `predict_from_features`. CONFIRM independently.

## Suggested Model Tier
Stronger — correctness-critical (sign + attach-point), the attach already failed
once.

## Stop Conditions
BLOCK if: the diff cannot be accessed, evidence cannot be reproduced, the attach
is post-fusion, the sign is inverted, missingness is silently imputed, a forbidden
file was touched, or default is not OFF.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings (numbered to
the 10 close criteria), the re-derived alpha=1 ordering-flip result, blockers,
out-of-scope observations.
