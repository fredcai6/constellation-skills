# Implementer Handoff — G4 pipeline-fix (run-enabling repair)

## Gate
`g4` (run-enabling) — fix the SubprocessPipeline downstream so the walk-forward run uses each PERIOD's
trained model, not the global promoted gold. Found by Commander preflight before the multi-hour run.

## The defect (diagnosed — do not re-derive from scratch, but confirm)
`src/evo_predictor/walkforward/pipeline.py` `_run_downstream` runs fusion → materialize → comparison, but:
- `scripts/run_sampled_runtime_comparison.py` AUTO-DISCOVERS the gold/trained manifests by globbing the
  GLOBAL `reports/evo/gold_cycle_*_{descriptor}...` and `reports/evo/fusion_*_{descriptor}...` (lines ~93-103),
  keyed by descriptor `{min(train_years)}thru{max(train_years)}` = `2018thru2024` for EVERY period.
  The period's own manifests live in the ISOLATED `outputs/walkforward_2025/pN/reports/`, NOT `reports/evo/`.
  So the comparison silently uses the PROMOTED-GOLD manifests → the walk-forward would score the baseline
  model for all of P1-P3, making the result meaningless. The script DOES accept explicit
  `--default-manifest` and `--trained-manifest` (lines ~595-596) — the fix is to pass them.
- `scripts/materialize_runtime_bundles.py` writes the trained manifest to GLOBAL
  `reports/evo/{fusion_slug-swapped}.sampled_runtime_manifest.json` (lines ~119-120) via a
  `gold_cycle_`→`fusion_` slug swap that requires gold+fusion to share a timestamp (they won't), and
  materializes bundles into the global `params/gold/runtime_bundles`. This does not fit the isolated layout.

## Task
Make the per-period downstream operate on the period's ISOLATED artifacts only, so comparison uses the
period-trained (cutoff) model:
1. Pass EXPLICIT manifests to `run_sampled_runtime_comparison.py`: `--default-manifest <period gold
   sampled_runtime_manifest>` and `--trained-manifest <period fusion sampled_runtime_manifest>` (discovered
   from the period's isolated `reports/` dir, as `_only` already does for the gold slug). Do NOT rely on
   global `reports/evo` auto-discovery.
2. Resolve `materialize`: determine whether `run_sampled_runtime_comparison.py` actually NEEDS materialized
   (portable) bundles, or whether it can load modules directly from the fusion/trained manifest's (absolute,
   period-local) module paths. If materialize is unnecessary for a local backtest, SKIP it for the period
   pipeline (document why). If it IS needed, make it target the period's isolated dirs / repoint the trained
   manifest within the period tree — never the global `reports/evo` or `params/gold`.
3. Ensure the trained manifest the comparison consumes points at modules that exist on disk (period-local).
   No global `reports/evo`/`params/gold` writes; no dependence on gold+fusion sharing a timestamp.

## Protected Intent
The walk-forward MUST score each period's own cutoff-trained+fused model. Silently using the promoted gold
(or any cross-period bleed) invalidates #439. Stay fully isolated under the period work area.

## Test Mode
`test-after allowed` for the wiring (assert the exact comparison/materialize argv on a mocked subprocess),
PLUS one REAL cheap end-to-end validation of the fixed downstream (see Required Evidence).

## Close Criteria
- The period comparison invocation includes explicit `--default-manifest`/`--trained-manifest` pointing at
  the period's isolated manifests; a unit test asserts this argv (mocked subprocess).
- materialize is either correctly period-isolated or justified-and-skipped; no global `reports/evo` /
  `params/gold` writes occur during a period run; no reliance on gold+fusion timestamp equality.
- A REAL downstream validation proves comparison consumes the PERIOD manifest and emits per-race predictions
  for the requested rounds (see evidence) — NOT the promoted gold.
- Existing walkforward unit suite still green; `simplification_limits` passes on touched paths.

## Allowed Scope
- `src/evo_predictor/walkforward/pipeline.py` (downstream wiring), its tests under
  `tests/unit/evo_predictor/walkforward/`. Touch `scripts/*` ONLY if a script genuinely cannot be driven via
  existing flags (prefer passing explicit args over editing scripts; if you must, keep gold workflow intact).

## Specific Exclusions
- Do NOT change the gold cycle, fusion, or comparison SCRIPTS' core logic; drive them via flags.
- Do NOT touch G1/G2 code, scoring, gold defaults, or promoted `params/gold` artifacts.
- Do NOT run the full multi-hour walk-forward (that is the Commander's next step).

## Constraints
- DB-only; `py` not `python`; run from repo root; period-isolated paths; one canonical path.

## Required Evidence
- Unit test output asserting the fixed comparison argv (explicit period manifests).
- ONE real cheap end-to-end downstream validation. PREFERRED cheap approach (no training): drive the FIXED
  `_run_downstream` (or a thin harness) using the EXISTING promoted-gold gold-cycle artifacts in `reports/evo/`
  as the stand-in "period" inputs (copy/point a temp period dir at them), restricted to 1-2 races via
  `--race-name`, and show comparison produces a `*.trained.json` with `per_race` predictions for those races
  using the EXPLICIT manifests. If that is infeasible, run ONE real research-mode micro gold-cycle
  (epochs=1, n_samples small, the cheapest config that still yields LOSO fusion rows) for a single period and
  run the full fixed downstream — but prefer the no-training path to keep it fast.
- `py -m pytest tests/unit/evo_predictor/walkforward -q` green; `py -m src.utils.simplification_limits` on touched paths.
- A short note: did you keep or skip materialize, and why; the exact downstream argv now used.

## Verification Commands
```bash
py -m pytest tests/unit/evo_predictor/walkforward -q
py -m src.utils.simplification_limits
```

## Suggested Model Tier
`stronger` — this gates the multi-hour run; correctness of which model gets scored is the whole point.

## Authority
Decided (Commander): comparison must use explicit period manifests; everything stays period-isolated. You
decide whether materialize is needed vs skipped (justify), and the exact validation path (prefer no-training).
Do NOT alter gold-workflow scripts' logic or run the full backtest.

## Stop Conditions
Stop and return if: comparison genuinely cannot consume explicit period manifests without a script logic
change (return the specific blocker); or the downstream needs materialized bundles in a way that can't be
period-isolated (return a design question).

## Return Format
Return IMPLEMENTER_RESULT: fix made, files changed, the exact new downstream argv, materialize decision,
test mode satisfied, evidence (paste the unit argv test + the real downstream validation output), assumptions,
stop conditions, out-of-scope observations.
