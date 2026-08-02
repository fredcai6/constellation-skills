# Cartographer Handoff — reconcile #420 into the architecture map

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch `constellation/issue-420-quali-anchor-production`. Python `py`.
`PYTHONIOENCODING=utf-8`. Invoke the constellation-cartographer skill and fold the
#420 changes into the recorded architecture, then validate.

## Scope of this reconcile
Issue #420 productionized the quali-head cross-channel pace anchor. The diff is the
single commit `22329c5` (`git show --stat 22329c5`). Changes:

NEW production module:
- `src/evo_predictor/quali_pace_anchor.py` — pure stdlib+numpy function
  `blend_quali_pace_anchor(pi, anchor, alpha)`: within-event z-blend of the quali
  head's latent field with a practice min-sector pace anchor. No domain imports
  beyond numpy. Module-leaf under `struct:evo`.

EDITS (no new nodes/edges):
- `src/evo_predictor/sampled_runtime.py` — `_run_stage` gained an inference-time
  anchor blend applied to the race_weekend quali head's PER-MODULE `pi` BEFORE
  fusion (new helpers `_anchor_quali_field`, `_nanmin2`); reads existing
  `DriverFeatures.qs_best_raw`/`lr_best_raw` (anchor = NaN/None-safe min across the
  quali-sim + long-run practice buckets). Imports the new `quali_pace_anchor` +
  `DRIVER_QUALI_POWER_FROM_RACE_WEEKEND` constant.
- `src/evo_predictor/pipeline_manifest_v4.py` — new optional `QualiPaceAnchorConfig`
  frozen dataclass on `RuntimeStageConfig` (parsed from the manifest quali stage;
  absent key -> disabled).
- `src/evo_predictor/sampled_runtime_manifest_assembly.py` — echoes the
  `quali_pace_anchor` block into the quali stage of the assembled manifest.
- `src/evo_predictor/gold_cycle/config.py`, `gold_cycle/runner.py`, `run.py` —
  thread two runtime config keys `quali_pace_anchor_enabled` / `quali_pace_anchor_alpha`.
- `configs/evo/gold_defaults.toml` — the two keys (default OFF, alpha 0.5).

NEW read-only harness (scripts are NOT map nodes — packet prose only):
- `scripts/accept_quali_anchor_420.py` — acceptance measurement; imports the
  production blend + the §7.6.2 `diagnose_quali_same_pairs` primitives; inference
  only on the committed gold bundle.

Findings doc: new §7.6.4 in `docs/evo/prediction_ceiling_and_priorities.md`
(Commander wrote it; cartographer does NOT edit it).

## What to assess (apply your skill)
- This is a module-leaf addition under existing `struct:evo` + an additive,
  default-OFF runtime config knob (same shape as the #371 emit_module_record and
  #380 qs_compound_beta_regime reconciliations already in the index header).
- NO new cross-region import: `quali_pace_anchor.py` is pure numpy; the runtime
  reads existing `DriverFeatures` fields and the existing `evo->latent_power` /
  `evo->data` edges are unchanged in direction. NO new container/component node.
  NO overlay change (DB-only + latent_power-boundary constraints already cover it).
- Update `packets/evo_predictor.md` to describe `quali_pace_anchor.py`, the
  `_run_stage` inference-time anchor seam (race_weekend quali head, pre-fusion,
  flag-gated), the `QualiPaceAnchorConfig` on `RuntimeStageConfig`, and the new
  `[runtime] quali_pace_anchor_*` gold config knobs (packet prose for the harness).
- Add a reconciliation line to the `docs/architecture/index.md` header (dated
  2026-06-07, #420), in the same style as the existing reconciliation entries.
- The G3 reviewer flagged the index may want this mention — that is exactly this
  reconcile.

## Constraints
- Do NOT edit `docs/evo/prediction_ceiling_and_priorities.md`,
  `docs/evo/fusion_rework_findings.md`, `fusion.py`, `fusion_training/`, or any
  src/ code. Architecture docs + packets only.
- Current-truth only; no archaeology.

## Validate
```bash
py scripts/check_arch_map.py
```
Must pass (no duplicate ids / missing parents / unmapped src modules / dangling
overlays). Note: the new `quali_pace_anchor.py` is under `src/evo_predictor/`
which is covered by the existing `struct:evo` container — confirm the checker is
satisfied (module-leaf additions under an existing container should not need a new
node, but verify the checker does not flag it as unmapped; if it does, that tells
you whether a node is required).

## Return Format
Return a CONCISE summary: what packet/index text you added/changed, whether any
new node/edge/overlay was needed (expected: none), and the `check_arch_map.py`
result.
