# Reviewer Handoff

## Gate
`g5` — Promotion of Arm B (quali_pace_gap) to the canonical gold bundle

## What Was Implemented (commander-run, uncommitted in working tree)
Promoted Arm B `gold_cycle_260608_043414_2018thru2024` to `params/gold/`:
- Materialized 12 bundles → `params/gold/runtime_bundles/gold_cycle_260608_043414_2018thru2024/`
- Canonical `params/gold/sampled_runtime_manifest.json` rewritten (params/gold-relative paths + provenance) = the trained (anchored, v2) manifest
- Fusion config → `params/gold/fusion/fusion_260608_084626_2018thru2024.json`; unc_cal kept; gold/fusion/rt-comparison/unc_diag reports → `reports/evo/`
- `configs/evo/gold_defaults.toml`: default `recent_history_form_encoding` flipped → `quali_pace_gap`
- `scripts/accept_quali_anchor_420.py`: default `BUNDLE_NAME` repointed → 260608
- RT-comparison regenerated (trained 24/24, MAE 3.70 / Brier 0.2007)
- Pruned old 260517/260530/260603 (`--keep 1`)

## How to Inspect
```bash
cd C:/Programs/f1Brainz
git status --porcelain | awk '{print $1}' | sort | uniq -c   # 7 M, 153 D (prune), ~18 ?? (new 260608 + .agent-work)
git --no-pager diff -- configs/evo/gold_defaults.toml scripts/accept_quali_anchor_420.py
ls params/gold/runtime_bundles/                              # only 260608 should remain
py scripts/run_pipeline_validation.py --profile compact      # must exit 0, all 7 sections pass
```

## Close Criteria (independently verify — re-run)
- **Right arm promoted**: `params/gold/sampled_runtime_manifest.json` references the 260608 bundle; the promoted quali recent-history module bundles are **`.v2`** (quali_pace_gap, the user-chosen winner), NOT `.v1`. Anchor enabled in the quali stage (alpha 0.5). All 12 module `manifest_path`s resolve to existing files under `params/gold/runtime_bundles/gold_cycle_260608_043414…/`.
- **Manifest format**: params/gold-relative module paths (`runtime_bundles\…`, like the prior canonical), `provenance.static_fusion_config_path` = `params/gold/fusion/fusion_260608_084626_2018thru2024.json`.
- **Encoding default flipped**: `gold_defaults.toml` `recent_history_form_encoding = "quali_pace_gap"`.
- **Old pruned**: only `gold_cycle_260608_043414_2018thru2024` remains in `runtime_bundles/`.
- **pipeline_validation `--profile compact` → exit 0, all 7 sections pass** (gold, sampled_runtime, static_fusion, report_alignment, manifest_portability, artifact_policy, strategy).
- **Change scope sane**: the 7 modified tracked files are exactly {gold_defaults.toml, sampled_runtime_manifest.json, accept_quali_anchor_420.py, the 2 sampled_runtime_backtests comparison JSONs, the 2 validation summary files}; deletions are all pruned old artifacts; new untracked files are the 260608 set + `.agent-work/` (work area, NOT to be committed).

## Allowed Scope / Exclusions
Read-only verification + running pipeline_validation. The working tree is uncommitted; the commander commits at integrate after your APPROVE. Known triage items tc2 (oracle), tc3 (NPU), tc4 (limits) — note, don't block.

## Suggested Model Tier
sonnet — verification of a canonical artifact swap + validation re-run.

## Stop Conditions
BLOCK if: the promoted bundle is NOT Arm B/v2; any module path doesn't resolve; the anchor isn't active; the encoding default isn't flipped; old bundles weren't pruned; pipeline_validation isn't all-green; or the change scope includes unintended modifications.

## Return Format
REVIEW_RESULT: verdict APPROVE/BLOCK, per-criterion findings with commands/results, explicit confirmation that (1) the promoted bundle is Arm B/v2 with anchor active, (2) pipeline_validation is all-green, (3) old bundles pruned and change scope is clean. Blockers, out-of-scope observations.
