# Implementer Handoff — G1 (issue #451, cmdr-451)

You are a constellation-implementer crew (Sonnet) for Commander cmdr-451. Work ONLY in the worktree `C:/Programs/f1Brainz-worktrees/cmdr-451`. Python is `py`, never `python`. Set `PYTHONIOENCODING=utf-8` (bash: prefix `PYTHONIOENCODING=utf-8 py ...`) on every captured python call. Run all commands from the worktree root.

## Gate
g1 — reproduce the §7.6.2 same-pairs scoreboard + a read-only representation probe. **NO retrain, NO param/src change.**

## Task
Three deliverables, all written into `.agent-work/451/evidence/g1_numbers.json`:

### (1) Regenerate inference records (committed bundle, inference only)
For BOTH modules `driver_quali_power_from_race_weekend` (stem `rw`) and `driver_quali_power_from_recent_history` (stem `rh`), for years 2018,2019,2020,2021,2022,2023,2024,2025, emit per-event record sidecars named EXACTLY `{stem}_{year}.record.json` into `.agent-work/451/records/`.

The harness expects those exact stems. The emit CLI writes `{output}.record.json`, so set `--output .agent-work/451/records/{stem}_{year}`.

Per-year command template (verified working; ~seconds/year):
```bash
PYTHONIOENCODING=utf-8 py src/evo_predictor/run.py backtest-latent-power-module \
  --module driver_quali_power_from_race_weekend \
  --bundle params/gold/runtime_bundles/modules/driver_quali_power_from_race_weekend \
  --year 2024 \
  --output .agent-work/451/records/rw_2024 \
  --emit-module-record \
  --compound-prior-root params/gold/compound_prior \
  --retro-root C:/Programs/f1Brainz/params/retro_truth \
  --db-root C:/Programs/f1Brainz/data \
  --db-path C:/Programs/f1Brainz/data/f1_data.db
```
Repeat for each year and for the `rh` module (`--module driver_quali_power_from_recent_history`, `--bundle params/gold/runtime_bundles/modules/driver_quali_power_from_recent_history`, `--output .agent-work/451/records/rh_{year}`). For the rh module, ALSO pass `--recent-history-form-encoding quali_pace_gap` (the promoted encoding). If a year errors on missing data, record which and continue.

### (2) Run the §7.6.2 harness UNMODIFIED
```bash
QUALI_SAME_PAIRS_RECORDS_DIR=.agent-work/451/records \
QUALI_SAME_PAIRS_EVIDENCE_DIR=.agent-work/451/evidence/same_pairs \
PYTHONIOENCODING=utf-8 py scripts/diagnose_quali_same_pairs.py
```
Capture the headline `race_weekend` model acc, `recent_history` model acc, `best_across_fp` ceiling, and pair count. Compare to §7.6.2: rw 0.6149 / rh 0.7803 / ceiling 0.8061 / 23862 pairs. **If they reproduce within ~±0.01, report "reproduced". If they deviate (the committed bundle `gold_cycle_260608_043414` was trained with the #420 anchor active, so the head `pi` may differ), report the reproduced numbers and FLAG the deviation — the reproduced rw number becomes the working baseline for downstream gates.**

### (3) Read-only LINEAR representation probe (walk-forward, same shared pairs)
This tests whether the pace-ordering the ceiling exploits is even LINEARLY present in the head's own input feature vector.
- The records carry `features` = the per-pair antisymmetric feature DIFFERENCES the head ingests (shape (n_pairs, 23)), plus `outcome` (1.0 if left beat right in Q) and `pair_index`/`entity_ids`.
- Build a pooled training set of (features_diff -> outcome) over the HEADLINE TRAIN years, fit a simple logistic regression (no per-pair leakage: standardize on train only), then SCORE sign accuracy on the SAME shared non-tie pairs the harness uses, in a WALK-FORWARD manner: for the headline regime, use leave-one-year-out or train-on-earlier/score-later so no scored pair is in the fit. Report the linear-probe pooled sign accuracy on the shared pairs.
- Also report, for calibration, the min-sector `best_across_fp` ceiling on those same pairs (already in the harness output) and the head (0.615 / reproduced).
- INTERPRETATION to state (not decide the verdict — that's the Commander's): if the linear readout of the head's OWN features lands near the head (~0.62) and well below ceiling (~0.81), the pace signal is NOT linearly present in the feature vector (representation-lossy). If it lands near the ceiling, the info IS present and the head fails to extract it.

Keep the probe self-contained in a scratch script under `.agent-work/451/` (do NOT add to `scripts/` or `src/`). Reuse the harness's `_shared_nontie_pairs` / pair primitives by importing `scripts.diagnose_quali_same_pairs` and `scripts.diagnose_quali_evidence` — do NOT fork the pair logic.

## Protected Intent
Re-establish the exact §7.6.2 scoreboard as the run's measurement anchor, and produce a first read-only signal on (a) representation — all on the shared-pairs harness, with zero leakage and zero production change.

## Test Mode
inspection-only (diagnostic probe; no production code changes). No new tests required, but the probe must reuse the committed harness primitives unmodified.

## Close Criteria
- `rw_{year}.record.json` and `rh_{year}.record.json` present for 2018-2025 (note any year that genuinely lacks data).
- Harness ran unmodified; baseline reproduced-or-flagged with numbers.
- Linear-probe sign accuracy on shared pairs reported, walk-forward (no fit-on-scored-pairs).
- `.agent-work/451/evidence/g1_numbers.json` written with top-level keys `baseline` (dict: rw, rh, ceiling, pairs, reproduced|flagged) and `linear_probe` (dict: acc, method, leakage_control).

## Allowed Scope
`.agent-work/451/**` only (records, evidence, scratch probe script). READ-only access to `params/gold/**`, `src/**`, `scripts/**`, and the main checkout data at `C:/Programs/f1Brainz/data` + `C:/Programs/f1Brainz/params/retro_truth`.

## Specific Exclusions
NO retrain. NO edits to `src/**`, `scripts/**`, `params/**`. NO gold cycle. NO fusion/Piece-2. Do not modify `diagnose_quali_same_pairs.py`.

## Constraints
- DB-only analysis; `py` not `python`; `PYTHONIOENCODING=utf-8` on captured calls.
- Walk-forward / as-of for the linear probe — no scored pair may appear in its fit.
- Reuse harness primitives; do not fork the shared-pairs math.

## Map Anchors (inbound)
- Structural: `src/evo_predictor/quali_power_adapter.py` (23-feature vector); `scripts/diagnose_quali_same_pairs.py` (harness); committed runtime bundle `params/gold/runtime_bundles`.
- Capability: race_weekend quali head inference.
- Constraints: no leakage into scoring pairs; no param change.
- Decision: §7.6.3 C3 — sign-accuracy moves only with a new ordering signal.
- Evidence to re-confirm: rw 0.6149 / rh 0.7803 / ceiling 0.8061 / 23862 pairs.
- Confidence flag: records regenerated from anchor-active bundle — verify reproduction or flag deviation.

## Required Evidence
`g1_numbers.json` (baseline + linear_probe), the harness stdout (saved), the record file listing, and the scratch probe script path. Quote the key numbers in your IMPLEMENTER_RESULT.

## Verification Commands
```bash
ls .agent-work/451/records/ | grep -E "r[wh]_20(1[89]|2[0-5])\.record\.json" | wc -l   # expect ~16
PYTHONIOENCODING=utf-8 py -c "import json; d=json.load(open('.agent-work/451/evidence/g1_numbers.json')); print('baseline' in d, 'linear_probe' in d)"
```

## Suggested Model Tier
simple bounded — mechanical record-gen + a small probe; reason: low ambiguity, clear commands.

## Authority
The probe DESIGN and interpretation framing are fixed by this handoff. You do NOT decide the localization verdict. If reproduction deviates materially (>~0.03 from 0.6149) you do NOT halt — record it, flag it, adopt the reproduced number as baseline, and continue.

## Stop Conditions
Stop and return if: the emit path errors irrecoverably for ALL years; the harness cannot run unmodified; you cannot build the linear probe without leaking scored pairs into the fit; or producing the evidence requires touching `src/`/`scripts/`/`params/`.

## Return Format
Return IMPLEMENTER_RESULT: deliverables completed, files changed (should be only `.agent-work/451/**`), evidence produced (quote rw/rh/ceiling/pairs + linear-probe acc), reproduction reproduced-or-flagged, assumptions, stop conditions hit, out-of-scope observations, and workflow feedback (what made this harder than needed).
