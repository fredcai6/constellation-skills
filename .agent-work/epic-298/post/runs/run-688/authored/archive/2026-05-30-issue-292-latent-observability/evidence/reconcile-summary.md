# Architecture reconcile — issue-292 latent observability

**Date:** 2026-05-30  
**Work ID:** `issue-292-latent-observability/reconcile`  
**Role:** Constellation Cartographer

## Scope

Reconcile architecture map against issue-292 observability/baseline gates (stateless gold-cycle pipeline). No `src/` changes — architecture docs only.

## Evidence reviewed

| Source | What verified |
|---|---|
| `src/evo_predictor/module_uncertainty_diagnostics.py` | `empty_usable_event_set`, `fully_skipped_usable_event_set` flags; summary counters |
| `scripts/run_pipeline_validation.py` | Compact profile; `CANONICAL_TRAIN_YEARS` 2018–2024; gold/static/sampled-runtime sections |
| `scripts/run_sampled_runtime_comparison.py` | `rt_comparison_*` slug via `make_artifact_slug` |
| `configs/evo/gold_defaults.toml` | `train_years = [2018..2024]` matches validator |
| `docs/report_schemas/validation_reports.md` | Issue-292 gate ownership table |
| `docs/artifact_policy.md` | Validation integration section |
| `.agent-work/issue-292-latent-observability/evidence/g4-final-verification.md` | Artifact regen notes, rt_comparison metric reuse caveat |

## Packets updated

### `docs/architecture/packets/evo_predictor.md`

- Added **`module_uncertainty_diagnostics.py`** component (sidecar producer, diagnostic flags, validation consumer).
- Added **pipeline validation scripts** table (`run_gold_module_training_cycle`, `run_static_hierarchical_fusion_training`, `run_sampled_runtime_comparison`, `run_pipeline_validation`).
- Expanded **artifact paths** for `unc_diag_*`, `fusion_*`, `rt_comparison_*`, and `reports/validation/`.

### Not updated

- **`latent_power.md`** — no issue-292 code changes; diagnostics wrap gold-cycle module results on the evo side.
- **`strategy.md`** — already references `validation_reports.md` and `sampled_runtime_comparison.md`.

## Index and overlays

### `docs/architecture/index.md`

- Verification stamp → 2026-05-30 (issue-292 reconcile).
- New component node: `struct:evo.module_uncertainty_diagnostics`.
- Open triage notes for rt_comparison metric freshness, `CANONICAL_TRAIN_YEARS` duplication, parallel gold schema docs.

### `docs/architecture/overlays/purposes.yml`

- Added `docs/report_schemas/validation_reports.md` to `struct:evo` → `purpose:race_prediction` evidence.

## Triage candidates

| ID | Statement | Authority |
|---|---|---|
| T1 | Regenerate `rt_comparison_*` with live backtests once gold runtime bundles no longer hit singular matrix; current committed metrics may reuse prior 2021–2024 comparison payloads | Human / implementer |
| T2 | Consolidate `CANONICAL_TRAIN_YEARS` in `run_pipeline_validation.py` with `configs/evo/gold_defaults.toml` (single import or shared constant module) to prevent drift | Triage |
| T3 | Retire or merge `docs/evo/gold_module_training_cycle_report_schema.md` vs `docs/report_schemas/gold_module_training_cycle.md` — parallel canonical docs | Triage |
| T4 | Full gold module retrain not rerun in g4; sidecars refreshed on May-26 gold cycle artifacts — confirm acceptable baseline or schedule retrain | Human |

## Blockers

None for architecture reconcile. Map compliance verified against current code and g3 schema docs.

## Checklist engine

Drove `reconcile.json` gates: context → packets → index-overlays → map-compliance (all advanced).
