# Implementer Handoff — issue-414 G1

You are a fresh crew member. Implement exactly this bounded task. Do not read any transcript; everything you need is here. Invoke the `constellation-implementer` skill and drive it.

Repo root (run all commands from here): `C:\Programs\f1Brainz\.claude\worktrees\agent-a82dd9d22cd9863fc`
Set `PYTHONIOENCODING=utf-8` in every shell that runs python. Python is `py` (never `python`).

## Gate
g1

## Task
Establish the apples-to-apples MEASUREMENT BASELINE for a scoping study of the race_weekend qualifying head.

(1) Regenerate per-event quali `pi` records by INFERENCE on the committed gold bundle (NO retrain), for BOTH quali channels and ALL years 2018-2025:
- module `driver_quali_power_from_race_weekend` (needs `--compound-prior-root`)
- module `driver_quali_power_from_recent_history` (no compound prior)

(2) Run the existing diagnostic `scripts/diagnose_quali_same_pairs.py` against the REGENERATED records and confirm it reproduces the published §7.6.2 numbers.

## Protected Intent
INFERENCE ONLY on committed gold weights. Zero production behaviour change. No retrain, no checkpoint/param/manifest edit, no change to any production scoring path. The records are throwaway run-package artifacts. The only source change permitted is a small, backward-compatible env-var override so the diagnostic can read records from a non-default directory (see Allowed Scope) — its DEFAULT behaviour must be unchanged.

## Exact commands for record regen
For race_weekend, for each YEAR in 2018 2019 2020 2021 2022 2023 2024 2025:
```
py -m src.evo_predictor.run backtest-latent-power-module \
  --bundle "C:/Programs/f1Brainz/params/gold/runtime_bundles/gold_cycle_260603_173742_2018thru2024/modules/driver_quali_power_from_race_weekend" \
  --module driver_quali_power_from_race_weekend \
  --year YEAR \
  --compound-prior-root "C:/Programs/f1Brainz/params/gold/compound_prior" \
  --db-path "C:/Programs/f1Brainz/data/f1_data_YEAR.db" \
  --emit-module-record \
  --output ".agent-work/issue-414-quali-head-scoping/records/rw_YEAR.json"
```
For recent_history, for each YEAR (NOTE: module dir is .../driver_quali_power_from_recent_history; NO --compound-prior-root):
```
py -m src.evo_predictor.run backtest-latent-power-module \
  --bundle "C:/Programs/f1Brainz/params/gold/runtime_bundles/gold_cycle_260603_173742_2018thru2024/modules/driver_quali_power_from_recent_history" \
  --module driver_quali_power_from_recent_history \
  --year YEAR \
  --db-path "C:/Programs/f1Brainz/data/f1_data_YEAR.db" \
  --emit-module-record \
  --output ".agent-work/issue-414-quali-head-scoping/records/rh_YEAR.json"
```
This produces `{rw,rh}_YEAR.record.json` + `.record.npz` sidecars (the `.json` payload is a backtest dump; the diagnostic reads the `.record.json`/`.record.npz` pair via `load_module_record`). One year ≈ 70s; the full 16 passes ≈ 20 min. If ANY single pass exceeds ~10 min, STOP and report.

## Pointing the diagnostic at the 414 records
`scripts/diagnose_quali_same_pairs.py` currently hardcodes:
```
RECORDS_DIR = _REPO_ROOT / ".agent-work" / "issue-381-same-pairs" / "records"
```
Make this overridable by an environment variable WITHOUT changing the default. Replace the assignment with (exact intent):
```
RECORDS_DIR = Path(os.environ.get("QUALI_SAME_PAIRS_RECORDS_DIR", str(_REPO_ROOT / ".agent-work" / "issue-381-same-pairs" / "records")))
```
(add `import os` if missing). EVIDENCE_DIR may stay as-is OR be made overridable the same way with `QUALI_SAME_PAIRS_EVIDENCE_DIR` — your choice, but EVIDENCE_DIR must still default to the 381 path. Do not change any other behaviour, math, or output of the script.

Then run:
```
set PYTHONIOENCODING=utf-8
set QUALI_SAME_PAIRS_RECORDS_DIR=C:\Programs\f1Brainz\.claude\worktrees\agent-a82dd9d22cd9863fc\.agent-work\issue-414-quali-head-scoping\records
py scripts/diagnose_quali_same_pairs.py
```
(In bash: `QUALI_SAME_PAIRS_RECORDS_DIR=<abs path> PYTHONIOENCODING=utf-8 py scripts/diagnose_quali_same_pairs.py`.)

## Close Criteria (prove each with captured output)
- All 16 record pairs present: `{rw,rh}_{2018..2025}.record.json` + `.record.npz` under `.agent-work/issue-414-quali-head-scoping/records/`.
- The diagnostic run on the regenerated records reproduces §7.6.2 (HEADLINE 2018-2024, NORMAL weekends, shared pairs) within rounding:
  - race_weekend model ≈ 0.6149 (accept 0.610–0.620)
  - recent_history model ≈ 0.7803 (accept 0.775–0.785)
  - best_across_fp ceiling ≈ 0.8061 (accept 0.804–0.808); blend_rank ≈ 0.8078
  - EASY/far-apart band (gap≥9): race_weekend model ≈ 0.687 (accept 0.680–0.695) vs best_across_fp ≈ 0.9365 (accept 0.934–0.939)
  - OOS 2025: race_weekend ≈ 0.5656, recent_history ≈ 0.7515, ceiling ≈ 0.7643 (looser tolerance ok; report actuals)
- Event counts per year match real F1 calendars and rw==rh per year (the diagnostic prints accounting lines).
- Capture the FULL diagnostic stdout to `.agent-work/issue-414-quali-head-scoping/evidence/g1_baseline_repro.txt`.

## Allowed Scope
- WRITE: `.agent-work/issue-414-quali-head-scoping/records/*` (regenerated records), `.agent-work/issue-414-quali-head-scoping/evidence/*` (captured output).
- EDIT (minimal, backward-compatible only): `scripts/diagnose_quali_same_pairs.py` — ONLY the RECORDS_DIR (and optionally EVIDENCE_DIR) env-var override described above. No other change.
- READ-ONLY: the gold bundle, the DBs, `scripts/diagnose_quali_evidence.py`, `src/evo_predictor/module_record.py`.

## Specific Exclusions
- NO retrain, NO param/checkpoint/manifest edit, NO change to any production scoring path or adapter.
- Do NOT commit records or evidence to params/ or outputs/.
- Do NOT touch `src/evo_predictor/fusion.py`, `src/evo_predictor/fusion_training/`, or `docs/evo/fusion_rework_findings.md`.
- Do NOT change the diagnostic's math, ceiling builders, or default paths.

## Constraints
- DB-only; py; PYTHONIOENCODING=utf-8; ABSOLUTE db paths; DBs read-only.
- Deterministic. If the env-var edit touches `scripts/` only (not `src/`), no simplification-limits run is required; if you somehow touch `src/`, run `py -m src.utils.simplification_limits <path>`.

## Required Evidence
- The captured diagnostic stdout file path + the key reproduced numbers (rw/rh/ceiling headline + EASY-band) quoted in your result.
- `git status --short` showing ONLY the env-var edit to the diagnostic (records/evidence are under .agent-work and may be gitignored — note if so).
- Confirmation no params/ or src/ behaviour file changed.

## Verification Commands
```
git status --short
QUALI_SAME_PAIRS_RECORDS_DIR=<abs 414 records path> PYTHONIOENCODING=utf-8 py scripts/diagnose_quali_same_pairs.py
```

## Suggested Model Tier
simple bounded — mechanical regen + reproduction; the only judgment is confirming the numbers land in tolerance.

## Authority
The fix-attaches-at-pi-layer and inference-only decisions are already made by the Commander. You must not retrain, change defaults, or alter the ceiling math. If reproduction is OUT of tolerance, STOP and report the actual numbers (do not "fix" the diagnostic to force a match).

## Stop Conditions
Stop and return if: a record regen pass exceeds ~10 min; reproduction is materially out of tolerance; the env-var override would require changing more than the RECORDS_DIR/EVIDENCE_DIR lines; any required evidence cannot be produced; a retrain or default change seems necessary.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, the reproduced numbers (headline rw/rh/ceiling + EASY band + OOS), the evidence file path, git status summary, assumptions, stop conditions hit, out-of-scope observations.
