# Reviewer Handoff — G1 RE-REVIEW after anchor fix (issue #420)

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch `constellation/issue-420-quali-anchor-production`. Python `py`.
`PYTHONIOENCODING=utf-8`. Read `docs/agents/CREW_CONTEXT.md` + `GLOSSARY.md`.
Independent reviewer — verify by reading the diff and re-running.

## Gate
`g1` (re-review after a targeted anchor-field correction)

## Context
G1 was previously APPROVED. Then the G2 acceptance probe showed the anchor field
`qs_best_raw` (short-stint only) was too narrow. The implementer changed the
anchor to the NaN-safe per-driver min of `qs_best_raw` and `lr_best_raw` (both
practice buckets) — reconstructing the §7.6.3 `best_across_fp` all-FP min-sector
signal in-machinery. Your job: verify THIS change is correct and nothing else
regressed.

## How to Inspect
```bash
git diff src/evo_predictor/sampled_runtime.py
git diff src/evo_predictor/quali_pace_anchor.py
git diff tests/unit/evo_predictor/test_sampled_runtime.py
git status --short
```

## Close Criteria (each a check)
1. **Anchor = min of both buckets:** `_anchor_quali_field` builds the per-driver
   anchor as the NaN-safe min of `qs_best_raw` AND `lr_best_raw` (via the
   `_nanmin2` helper). Confirm both fields are read from `DriverFeatures`.
2. **`_nanmin2` correctness — CONFIRMED RISK, verify the fix:** both finite ->
   min; exactly one finite -> that one; neither finite -> NaN. CRITICAL: the
   Commander has confirmed `DriverFeatures.qs_best_raw`/`lr_best_raw` CAN be
   `None` at inference — `data_adapter/_assemble.py` (~lines 189/192) populates
   them via `getattr(pf, "..._theoretical_best_raw", np.nan)` where that source
   attr is `Optional[float] = None` (`practice_preprocessor/_types.py:159,162`).
   When the attr EXISTS and is None, getattr returns None (NOT the np.nan
   fallback). So `None` reaches `_anchor_quali_field` -> `_nanmin2`. If `_nanmin2`
   calls `math.isfinite(None)` it raises TypeError -> production crash whenever a
   driver lacks a raw theoretical-best.
   REQUIRED: `_nanmin2` (or the per-driver min) MUST treat `None` as missing
   (coerce None->nan, or guard `x is None`). If the current code does NOT handle
   None, this is a BLOCK — the fix is to coerce None to nan before
   `math.isfinite` (e.g. `def _coerce(x): return float(x) if x is not None and
   math.isfinite... ` or check `x is None` first). Verify a test covers the
   None case (synthetic DriverFeatures with qs_best_raw=None and/or
   lr_best_raw=None must not crash and must behave as missing).
3. **ATTACH POINT UNCHANGED:** still applied to the per-module race_weekend
   `ModuleFieldResult.pi` INSIDE `_run_stage`, BEFORE `fuse_module_fields_ordered`,
   gated on `task=="quali"` AND enabled AND
   `module_name==DRIVER_QUALI_POWER_FROM_RACE_WEEKEND`. No post-fusion blend.
4. **Blend fn unchanged:** `quali_pace_anchor.py` math/sign/missingness identical
   to the approved version (only docstring may have changed). alpha=0 exact no-op.
5. **sigma_pi unchanged** (dataclasses.replace pi only).
6. **Tests:** the `_nanmin2` (or per-driver-min) helper has a unit test (both
   present/one/none); the `sampled_runtime` attach-point test reflects the
   min-of-two-buckets anchor and still asserts pre-fusion per-module attach +
   gating; all blend-function tests still green. Tests synthetic-only.
7. **Boundary:** no edits to fusion files, `prediction_ceiling_and_priorities.md`,
   `scope_quali_anchor_414.py`, `accept_quali_anchor_420.py`, race/race_start, or
   config keys/threading. Default still OFF.
8. **simplification_limits** clean on touched paths except the pre-existing
   `predict_from_features` 153-line violation.

## Evidence to reproduce
```bash
py -m pytest tests/unit/evo_predictor/test_quali_pace_anchor.py tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/evo_predictor/test_pipeline_manifest_v4.py -q
py -m pytest tests/unit/evo_predictor/ -q
py -m src.utils.simplification_limits src/evo_predictor/sampled_runtime.py src/evo_predictor/quali_pace_anchor.py
```

## Suggested Model Tier
Simple bounded — focused delta review; the None-vs-float edge is the one thing to
probe carefully.

## Stop Conditions
BLOCK if: anchor is not the min of both buckets, `_nanmin2` can receive None and
crash, the attach point regressed, the blend math changed, a forbidden file was
touched, or tests fail.

## Return Format
REVIEW_RESULT: verdict (APPROVE/BLOCK), per-check findings, the None-vs-float
edge determination, blockers, out-of-scope observations.
