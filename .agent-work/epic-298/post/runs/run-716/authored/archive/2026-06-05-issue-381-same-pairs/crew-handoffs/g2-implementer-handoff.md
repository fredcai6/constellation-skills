# Implementer Handoff

## Gate
g2-implement

## Task
Build `scripts/diagnose_quali_same_pairs.py` (DB-only; stdlib + numpy): score the trained
quali latent-power model (`pi` from the g1 records) against the DUAL data-only evidence
ceiling (`best_across_fp` and `blend_rank`, both min-sectors/theoretical-best agg over
FP1/FP2/FP3) on the IDENTICAL common-driver pair set per event, pooled separately for
HEADLINE 2018-2024 and OOS 2025. Emit the numbers table + 3-axis attribution. Add a
targeted pytest that pins the shared-pairs invariant.

## Protected Intent
Apples-to-apples truth: for every event, model and ceiling are scored on the SAME common
drivers (same pairs), against the SAME target (DB Q classification); the ceiling is
recomputed on each regime's exact event set — never the global 0.7968/0.8029 reused blindly.
Zero production behaviour change (scripts/ + tests/ only).

## Test Mode
test-after allowed (diagnostic script + an invariant-pinning unit test). The script is the
deliverable; the test pins the shared-pairs invariant and the ceiling-reuse.

## Close Criteria
- `scripts/diagnose_quali_same_pairs.py` runs deterministically, exits 0, prints:
  - numbers table: model vs `best_across_fp` vs `blend_rank`, per regime (headline 2018-2024,
    OOS 2025), each with events n and undirected-pairs n, on the shared pair set.
  - axis (i) recent-history drag: standalone `race_weekend` vs `recent_history` model sign
    accuracy on the shared per-channel pairs (PRIMARY). Fusion delta only if a committed
    fusion artifact supports it without retrain; else state explicitly it is omitted.
  - axis (ii) close-gap / midfield concentration: model & ceiling sign accuracy stratified by
    target Q-position gap (|pos_i - pos_j|) bands AND by midfield band (both drivers in a
    mid grid range), with per-bucket n.
  - axis (iii) evidence-weighting: the model-vs-ceiling residual (ceiling_acc - model_acc) per
    regime per ceiling, framed as the localized model-side gap.
- Writes a machine-readable numbers dump (JSON) under
  `.agent-work/issue-381-same-pairs/evidence/same_pairs_numbers.json` for g3 to quote verbatim.
- `tests/unit/evo_predictor/test_diagnose_quali_same_pairs.py` passes and pins: (a) for a
  synthetic/real event the model and each ceiling are scored on identical common-driver sets
  (same pair count); (b) the ceiling math is the imported harness primitive
  (`pairwise_accuracy_event` + the FP source builders), not a re-implementation.

## Allowed Scope
- NEW: `scripts/diagnose_quali_same_pairs.py`
- NEW: `tests/unit/evo_predictor/test_diagnose_quali_same_pairs.py`
- READ-ONLY reuse (import, do not fork): `scripts/diagnose_quali_evidence.py`
  (`open_db`, `events_for_year`, `classification_order`, `best_across_fp_source`,
  `session_blend_rank_source`, `is_sprint_weekend`, `pairwise_accuracy_event`, `AGGS`,
  `agg_theoretical_best`).
- READ-ONLY: `src/evo_predictor/module_record.py::load_module_record`; the g1 records under
  `.agent-work/issue-381-same-pairs/records/`.

## Specific Exclusions
- NO src/ behaviour change. NO retrain, NO param/checkpoint/manifest edit.
- DO NOT re-implement the ceiling math (best_across_fp / blend_rank / pairwise accuracy) —
  import the harness functions.
- DO NOT approximate a fusion delta. constructor_quali only if cheap (records not emitted for
  it, so almost certainly OMIT — driver_quali is primary per Q4).
- DO NOT pool across the 2018-2024 and 2025 regimes.

## Constraints (binding)
- SHARED-PAIRS INVARIANT (Admiral Q1): per event, intersect drivers across {model entity_ids,
  best_across_fp source, blend_rank source, DB Q target}; restrict EVERY source (model `-pi`,
  both ceilings) to that single common set before scoring, so all three share identical pairs.
- Model as source for the harness primitive: `source = {driver: -pi}` (negate `pi` so
  lower=better, matching the harness convention); target = `classification_order(con, year,
  round, "Q")` (DB Q result). VERIFIED EQUIVALENT to the record's native `mu>0 vs outcome`
  path (both give 0.6737 on rw_2024 r1) — use the harness primitive for everything so model
  and ceiling go through identical code.
- NORMAL weekends only for the ceiling comparison (match the ceiling definition):
  `not is_sprint_weekend(stypes)` AND `{FP1,FP2,FP3} <= stypes` AND `"Q" in stypes`. Model
  events on sprint weekends are excluded from the shared-pairs table (note their count).
- Records use DIRECTED pairs (N*(N-1)); the harness primitive uses UNDIRECTED (C(N,2)). Report
  undirected pair counts (the harness convention). Do not double-count.
- Ceiling agg = `agg_theoretical_best` (min-sectors) — the §7.6 recipe that yields the
  ≈0.7968 / ≈0.8029 figures.
- Event join: record `event_id` = `"<year>:<round>:<gp>:<tag>"`; parse year+round (split ":").
- `py` not `python`; DB-only (`data/f1_data_<year>.db`); deterministic; numbers reproducible.
- Pyright-clean on any touched file.

## Required Evidence
- Full stdout of `py scripts/diagnose_quali_same_pairs.py` (the numbers table + 3 axes).
- `same_pairs_numbers.json` written to the evidence dir.
- `py -m pytest tests/unit/evo_predictor/test_diagnose_quali_same_pairs.py -q` green.

## Verification Commands
```bash
py scripts/diagnose_quali_same_pairs.py
py -m pytest tests/unit/evo_predictor/test_diagnose_quali_same_pairs.py -q
py -m src.utils.simplification_limits scripts/diagnose_quali_same_pairs.py tests/unit/evo_predictor/test_diagnose_quali_same_pairs.py
```

## Suggested Model Tier
stronger — the shared-pairs invariant is the central correctness risk; subtle off-by-one in
the intersection silently breaks the apples-to-apples claim.

## Authority
Admiral rulings Q1-Q5 are binding (dual ceiling, shared pairs, standalone-primary drag,
driver_quali primary, headline LOSO 2018-2024 + OOS 2025). The implementer must not change the
ceiling definition, the regime split, or the shared-pairs rule.

## Stop Conditions
Stop and return if: the shared-pairs invariant cannot be honoured for a regime, the harness
import path breaks, a fusion delta would require retrain, or model entity_ids fail to join the
DB driver_ids for a material fraction of events.

## Return Format
Return IMPLEMENTER_RESULT: slice completed, files changed, evidence (the numbers), test mode
satisfied, assumptions used, stop conditions hit, out-of-scope observations.
