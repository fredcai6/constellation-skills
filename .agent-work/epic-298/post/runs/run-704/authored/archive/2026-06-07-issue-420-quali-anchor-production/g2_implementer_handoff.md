# Implementer Handoff — G2 acceptance reproduction (issue #420)

Repo root: `C:\Programs\f1Brainz\.claude\worktrees\agent-aedb2af1326073fec`.
Branch `constellation/issue-420-quali-anchor-production`. Python `py`.
ALWAYS set `PYTHONIOENCODING=utf-8` in the shell AND in the env of any child
python subprocess you spawn. Read `docs/agents/CREW_CONTEXT.md` + `GLOSSARY.md`.

## Gate
`g2` — the issue's CORE: prove the production anchor reproduces §7.6.3.

## Task
Build a READ-ONLY acceptance harness `scripts/accept_quali_anchor_420.py` that
measures whether the PRODUCTION pace-anchor path reproduces the §7.6.3 measured
improvement, on the IDENTICAL shared non-tie pair population as §7.6.2/§7.6.3,
and reports the delta vs the record-replay prototype.

## Protected Intent
This gate produces the acceptance VERDICT that decides whether #420 ships. It
must measure the REAL production path (production blend fn + production anchor
source + the real trained race_weekend head), not a re-implementation. An honest
"does not reproduce" is a valid verdict — do NOT massage numbers to pass.

## Test Mode
Inspection/measurement harness (test-after for any pure helpers you factor out).
The harness itself is the evidence. Add a tiny unit test only if you factor out a
non-trivial pure helper.

## KEY FACTS you must build on (already established by recon — do not re-litigate)

1. PRODUCTION ANCHOR = `DriverFeatures.qs_best_raw` (raw seconds, lower=faster,
   NaN when missing). This is what the G1 production code blends — confirm by
   reading `src/evo_predictor/sampled_runtime.py` `_anchor_quali_field`. You MUST
   use `qs_best_raw` (NOT `qs_theoretical_best`, NOT the prototype's
   `best_across_fp`). The harness measures the PRODUCTION anchor.

2. The §7.6.3 records CANNOT supply the anchor: a module record stores `pi` +
   the PAIR features (`DRIVER_QUALI_POWER_FEATURE_NAMES` — compound-ADJUSTED
   features; verified it does NOT contain `qs_best_raw`) + entity_ids + outcome.
   So you CANNOT read `qs_best_raw` from a record. You must obtain `qs_best_raw`
   from the PRODUCTION feature build (it lives on `DriverFeatures`).

3. The committed gold bundle is
   `params/gold/runtime_bundles/gold_cycle_260603_173742_2018thru2024` — the
   EXACT bundle §7.6.2/§7.6.3 used. The race_weekend quali module bundle is at
   `.../modules/driver_quali_power_from_race_weekend`. Compound priors are at
   `params/gold/compound_prior/<year>` (needed: race_weekend uses compound
   normalization). DBs (2018-2025) are at `C:/Programs/f1Brainz/data/` (absolute,
   read-only).

4. The §7.6.3 reference numbers (headline 2018-2024 LOSO, shared pairs,
   race_weekend, the numbers your production path must approximately reproduce):
   | alpha | overall | EASY(gap>=9) |
   |---|---|---|
   | 0.0 | 0.6153 | 0.6926 |
   | 0.2 | 0.6947 | 0.8062 |
   | 0.5 | 0.7452 | 0.8691 |
   | 1.0 (=ceiling) | 0.8061 | 0.9365 |
   OOS-2025 §7.6.3: alpha=0.5 -> 0.7097 overall / 0.8451 EASY (baseline 0.5674/
   0.6060, ceiling 0.7643/0.9055). Baseline pair count headline = 23862.

## Recommended harness design (single pass; you may adapt)

For each NORMAL weekend event (has FP1+FP2+FP3 and Q; not a sprint weekend) over
years 2018-2024 (HEADLINE) and 2025 (OOS), per year:

a) Build the per-event production `RaceFeatures` via the production data adapter
   (the SAME path `cmd_backtest_latent_power_module` uses —
   `build_labeled_batches_for_module` in `module_training_orchestration.py`, or
   the feature build under `src/evo_predictor/data_adapter/`). This populates
   `DriverFeatures.qs_best_raw`. Pass the compound prior root so adjusted features
   match production. Mirror the args `cmd_backtest_latent_power_module` builds
   (recent_history_form_encoding/qs_compound_beta_regime defaults; the gold
   bundle's config — read `params/gold/config.json` if needed for the exact knob
   values that bundle trained with).
b) Load the race_weekend quali module bundle
   (`driver_quali_power_from_race_weekend`) and run inference to get this event's
   per-driver `pi` aligned to driver_ids (the same `module.predict` path the
   runtime uses; `evaluate_labeled_batches` with `collect_record=True` gives you
   per-event `pi` + `entity_ids` — OR call the module predict directly).
c) Build the per-driver anchor array = `qs_best_raw` for each driver in the
   event's entity order (NaN if missing), reading from the `RaceFeatures.drivers`
   you built in (a).
d) Apply the PRODUCTION blend: import `blend_quali_pace_anchor` from
   `src.evo_predictor.quali_pace_anchor` and call it per event with each alpha in
   {0.0, 0.2, 0.3, 0.5, 0.7, 1.0}. (alpha=1 here is the production-anchor
   ceiling, NOT necessarily the data ceiling — note the difference.)
e) Score sign-acc on the IDENTICAL shared non-tie pair set: IMPORT (never fork)
   `scripts/diagnose_quali_same_pairs` primitives (`_shared_nontie_pairs`,
   `_acc_on_pairs`, `_stratified_pairwise`, `_restrict`, `_model_source`,
   `_parse_event_id`) and `scripts/diagnose_quali_evidence` (`classification_order`,
   `best_across_fp_source`, `agg_theoretical_best`, `open_db`, `events_for_year`,
   `is_sprint_weekend`). Build the shared set EXACTLY as
   `scripts/scope_quali_anchor_414.py` `_score_event_candidates` does (read it as
   the reference): common drivers across model, baf, blr, target; the shared
   non-tie pair list; the same far(gap>=9) stratum. This guarantees the pair
   population matches §7.6.2/§7.6.3.
   - ALSO compute the data ceiling (`best_across_fp`) on the same shared pairs so
     you can report recovered-fraction `(acc(a)-baseline)/(ceiling-baseline)`.

f) Pool over events per regime (headline / OOS). Report a table per regime:
   alpha, overall acc, EASY(gap>=9) acc, recovered-fraction (overall + EASY),
   pair counts. Also print baseline (alpha=0) overall+EASY+pairs and the
   data ceiling.

g) Print a comparison vs §7.6.3 (the table in KEY FACT 4): per alpha, the
   production overall/EASY MINUS the §7.6.3 overall/EASY, and a one-line verdict.

## The verdict + delta explanation (REQUIRED in your return)
State explicitly:
- Does the production path reproduce §7.6.3 within reasonable tolerance? (Give a
  tolerance judgment — e.g. alpha=0.5 overall/EASY within a few pp, recovered
  fraction comparable.)
- EXPLAIN the delta vs the record-replay prototype. The expected source of any
  delta: the prototype anchor `best_across_fp` = min-sectors over ALL clean FP
  laps across FP1/2/3; the production anchor `qs_best_raw` = min-sectors over
  SHORT-STINT (quali-sim-classified) clean laps. SAME signal family (FP
  min-sector pace), different lap population. If alpha=0 does NOT reproduce the
  baseline 0.6153, that is a RED FLAG that the pi source differs (e.g. a
  different bundle/config) — investigate, do not hand-wave.
- If the production path does NOT reproduce: that is a VERDICT (per admiral ruling
  5: STOP and report — it is not a failure). Report it clearly with the numbers
  and the most likely cause.

## Close Criteria
- `scripts/accept_quali_anchor_420.py` runs end-to-end, read-only, deterministic.
- alpha=0 reproduces (approximately) the §7.6.3 baseline overall/EASY on the
  shared pairs (or the discrepancy is explained).
- Production alpha=0.5 reproduction numbers + recovered-fraction reported for
  headline AND OOS, with the delta-vs-§7.6.3 table.
- A clear written VERDICT (reproduces / does not, with explanation).
- Full numeric output captured to
  `.agent-work/issue-420-quali-anchor-production/g2_accept_output.txt` (the
  harness can write a JSON next to it too).

## Allowed Scope
- NEW: `scripts/accept_quali_anchor_420.py` (+ optional small pure helper test).
- You MAY regenerate records under `.agent-work/issue-420-quali-anchor-production/`
  if your design needs them, but the anchor MUST still come from the production
  feature build, not the record.
- READ-ONLY everywhere else.

## Specific Exclusions
- Do NOT modify `src/` production code (G1 is done & approved). If you find a G1
  bug, STOP and report it — do not fix it here.
- Do NOT fork `diagnose_quali_same_pairs` / `diagnose_quali_evidence` /
  `scope_quali_anchor_414` — import them.
- Do NOT touch fusion files, `prediction_ceiling_and_priorities.md`, or any
  committed params/manifest artifact. NO gold retrain.

## Constraints
- Inference-only on the committed bundle; no training; no param mutation.
- DB-only; DBs read-only at the absolute path above.
- Deterministic; same pair population as §7.6.2/§7.6.3 (import the primitives).
- PYTHONIOENCODING=utf-8 in shell + child subprocess envs.

## Required Evidence
- The harness stdout (full tables + verdict) captured to the output file above.
- The alpha=0 baseline reproduction check (overall/EASY/pairs vs 0.6153/0.6926/
  23862) — pass or explained.
- A short note: how you obtained `qs_best_raw` (which feature-build call), how you
  got per-event `pi` (which inference call), and the exact bundle/config used.

## Verification Commands
```bash
# (set PYTHONIOENCODING=utf-8 first)
py scripts/accept_quali_anchor_420.py
```
If the run is long, you MAY run per-year and aggregate, but do NOT background it
in a way that detaches — the Commander needs the captured output. Keep total
runtime reasonable (inference-only; if it exceeds ~10 min, run headline years in
chunks and aggregate, capturing each chunk's output).

## Suggested Model Tier
Stronger — drives the production feature+inference path, correctness-critical
verdict, must reuse (not fork) existing primitives.

## Authority
Decided: anchor = production `qs_best_raw`; use production `blend_quali_pace_anchor`;
identical shared-pair population via imported primitives; gold bundle
`gold_cycle_260603_173742_2018thru2024`. You decide: exact feature-build +
inference entry points (there are several valid ones), chunking, JSON shape.

## Stop Conditions
Stop and return if: the production feature build does not populate `qs_best_raw`;
the gold bundle/module/compound-prior is unusable; alpha=0 cannot reproduce the
baseline and the cause is a G1/production bug (report it, don't fix); or the DBs
are unavailable.

## Return Format
IMPLEMENTER_RESULT: the harness, the FULL reproduction tables (headline + OOS),
the alpha=0 baseline check, the alpha=0.5 production numbers + recovered fraction,
the delta-vs-§7.6.3 table, the written VERDICT + delta explanation, how you got
qs_best_raw and pi, assumptions, stop conditions hit, out-of-scope observations.
