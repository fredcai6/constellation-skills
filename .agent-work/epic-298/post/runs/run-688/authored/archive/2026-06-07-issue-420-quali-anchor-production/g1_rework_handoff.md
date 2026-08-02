# Implementer Handoff — G1 REWORK (issue #420)

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch `constellation/issue-420-quali-anchor-production` (checked out). Python `py`.
`PYTHONIOENCODING=utf-8`. The previous G1 pass is otherwise GOOD — this is a
TARGETED FIX of ONE thing: the attach point is in the wrong place.

## What is wrong (the only blocker)

Your previous pass wired the anchor onto the **FUSED** quali field in
`SampledEvoRuntime.predict_from_features`:

```python
quali_fused = _apply_quali_pace_anchor(quali_fused, features=..., anchor_config=...)
```

`quali_fused` is the OUTPUT of `_run_stage("quali")`, i.e.
`fuse_module_fields_ordered(...)` — it already combines the race_weekend head,
the recent_history head, and the constructor head. The admiral pre-ruled
(ruling 1, NON-NEGOTIABLE) that the anchor must attach **inside the race_weekend
quali head's output path — where its per-module latent field `pi` is produced —
NOT at the fusion layer.**

Why this is not cosmetic: the measured basis (§7.6.3) is the anchor applied to
the STANDALONE `race_weekend` head's `pi` (the head that lacks a general-pace
anchor, sign-acc 0.6153). The fused field already contains `recent_history`
(near-ceiling, 0.78) and the constructor head; anchoring the fused output is a
DIFFERENT, un-measured operation and will NOT reproduce §7.6.3 in the G2
acceptance gate. It also entangles the anchor with fusion precision-weighting.

## The fix (move the attach point)

1. REMOVE the post-fusion call + the `_apply_quali_pace_anchor` helper from
   `predict_from_features` / module scope in `sampled_runtime.py`.

2. ATTACH INSIDE `_run_stage` (sampled_runtime.py ~ lines 331-365). The loop:

   ```python
   for module_name in enabled_stage_module_names(stage):
       loaded = self.modules[module_name]
       ...
       pair_batch = build_pair_batch_for_module(module_name, features=features, ...)
       fields.append(run_module_field(loaded, pair_batch))      # <-- line ~358
   fields = _canonicalize_stage_event_ids(task=task, features=features, fields=fields)
   return fuse_module_fields_ordered(fields, ...)
   ```

   Replace the append so that, ONLY when ALL of:
   - `task == "quali"`, AND
   - the stage's `quali_pace_anchor` config is present AND `.enabled`, AND
   - `module_name == DRIVER_QUALI_POWER_FROM_RACE_WEEKEND`
     (import the constant from `src.latent_power.modules`; do not hardcode the
     bare string),

   you blend that module's `ModuleFieldResult.pi` BEFORE appending:

   ```python
   result = run_module_field(loaded, pair_batch)
   if (task == "quali" and anchor_cfg is not None and anchor_cfg.enabled
           and module_name == DRIVER_QUALI_POWER_FROM_RACE_WEEKEND):
       result = self._anchor_quali_field(result, features=features, anchor_cfg=anchor_cfg)
   fields.append(result)
   ```

   where the helper builds the per-driver anchor aligned to
   `result.entity_ids` (NOT the fused driver_ids) from
   `{d.driver_id: d.qs_best_raw for d in features.drivers}`, calls
   `blend_quali_pace_anchor(result.pi, anchor, anchor_cfg.alpha)`, and returns
   `dataclasses.replace(result, pi=blended_pi)`. Keep `sigma_pi` unchanged
   (document via comment: ordering is the measured lever; downstream
   magnitude/precision implications are assessed in G3).

   `anchor_cfg` = `stage.quali_pace_anchor` (the stage is already
   `self.stage_configs[task]` inside `_run_stage`).

3. KEEP everything else from the previous pass: `quali_pace_anchor.py`, the
   config keys + threading, `QualiPaceAnchorConfig` on `RuntimeStageConfig`, all
   tests. The blend function and config plumbing were correct.

## Anchor field note (accepted, keep)
You chose `qs_best_raw` (raw seconds, NaN when missing) over the normalized
`qs_theoretical_best`. The Commander ACCEPTS this — NaN-missingness is cleaner
than the normalized field's default 1.0. Keep `qs_best_raw`.

## Add a test for the corrected attach point
Add/adjust a `sampled_runtime` test that proves: with the anchor ENABLED, the
PER-MODULE race_weekend quali field is blended BEFORE fusion (not the fused
output), and the race/race_start stages are untouched. A focused unit test with
a small synthetic stage is fine; if full-runtime wiring is heavy to fixture,
test `_run_stage`'s gating logic by asserting the blend is applied to the
race_weekend module's `pi` and NOT to recent_history's `pi`. Do NOT depend on
generated records or DBs.

## Close Criteria
- Blend applied to the race_weekend head's per-module `pi` INSIDE `_run_stage`,
  before `fuse_module_fields_ordered`; the post-fusion call is gone.
- Gated on quali + DRIVER_QUALI_POWER_FROM_RACE_WEEKEND + enabled; race/race_start
  untouched; no-op when disabled (default OFF).
- recent_history quali head is NOT anchored (only the race_weekend head).
- All previous tests still green + the new attach-point test green.
- `py -m src.utils.simplification_limits` clean on touched paths EXCEPT the
  pre-existing `predict_from_features` 154-line violation (which your fix should
  now REDUCE since you remove the post-fusion call from it — verify it does not
  get worse; if `_run_stage` approaches the limit, that is acceptable to flag).

## Allowed Scope
Same as before: `sampled_runtime.py` (move the attach), and any test files.
Do NOT expand to new files beyond what exists.

## Specific Exclusions
`fusion.py`, `fusion_training/**`, `scripts/fusion_replay/**`,
`docs/evo/fusion_rework_findings.md`, `scripts/scope_quali_anchor_414.py`,
`docs/evo/prediction_ceiling_and_priorities.md`. Race/race_start behavior.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/test_quali_pace_anchor.py tests/unit/evo_predictor/test_sampled_runtime.py tests/unit/evo_predictor/test_pipeline_manifest_v4.py -q
py -m pytest tests/unit/evo_predictor/ -q
py -m src.utils.simplification_limits src/evo_predictor/sampled_runtime.py src/evo_predictor/quali_pace_anchor.py
```

## Suggested Model Tier
Stronger — correctness-critical attach-point relocation.

## Authority
Attach point is FIXED by admiral ruling: per-module race_weekend head pi inside
`_run_stage`, pre-fusion. Not negotiable. Everything else as previously decided.

## Stop Conditions
Stop and return if the per-module attach inside `_run_stage` is genuinely
infeasible (e.g. module_name not available in the loop, or entity_ids not on the
ModuleFieldResult) — but recon confirmed both ARE available, so this should not
trigger.

## Return Format
IMPLEMENTER_RESULT: what moved, files changed, the new attach-point test, full
test + simplification evidence, confirmation the post-fusion call is removed.
