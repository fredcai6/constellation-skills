# Gold Lifecycle: potential → gold → archive

- **Date:** 2026-06-10
- **Status:** Design (pending review)
- **Related:** #439 (walk-forward harness), #440 (post-dev-cycle gold+backtest gate), PR #442 (leaked `per_race_predictions` scrub), `docs/evo/analysis_refresh.md` (runbook)

## 1. Motivation

The June latent-power gold promotion (#335) updated the runtime model but left March's `per_race_predictions/` in place — files trained *on the 2025 eval year*. Downstream reused them with no provenance check, producing a leaked "707" fantasy score that appeared to beat the best human (711). The cause was **structural, not a one-off mistake**:

- Promotion is **implicit** — `gold-cycle` + `materialize` write straight into `params/gold/`; nothing removes superseded artifacts, so stale files survive a promotion.
- Committed gold mixes **two generations** (June v4 latent-power + March schema-v3) with **no single provenance record**.
- Backtests can read `params/gold/` directly, so candidate evaluation isn't isolated from the live model.
- The multi-season fantasy backtest that would have surfaced the regression is a one-off script, not a standing gate.

This design makes gold a **stable, single-provenance interface** with an **intentional, physical promotion lifecycle**, and mechanizes the multi-season backtest as the promotion evidence gate.

## 2. Goals / non-goals

**Goals**
- Committed gold uses **constant filenames** (no slugs); best-known truth is swapped underneath them.
- Every gold carries **in-file provenance** (top-level `gold_provenance.json` + existing manifest provenance).
- Promotion is an **intentional physical move**: `potential → gold → archive`, atomic and reversible.
- Candidate **evaluation never reads `params/gold/`**.
- Multi-season fantasy backtest is a **committed, repeatable evidence tool** feeding promotion.
- The stale-artifact leak class becomes **structurally impossible** (single provenance + atomic swap).

**Non-goals**
- No change to model architecture, training, or the runtime prediction API.
- No change to compound-prior internals (its location is already constant).
- Not reworking the candidate/build slug scheme — slugs stay on the build + archive side.

## 3. Three physical locations

```
params/gold/            LIVE      committed; constant names only; single provenance
params/gold_candidate/  POTENTIAL gitignored; a freshly built candidate, full gold layout
params/gold_archive/    ARCHIVE   gitignored; superseded golds under <slug>/, time-bounded
```

Only `params/gold/` is committed; **its git history is the lineage**. `gold_candidate/` and `gold_archive/` are added to `.gitignore`. Archive retention is time-bounded (default: keep the last 3 promotions, configurable; pruned by `promote_gold.py` or a separate prune step).

## 4. The gold artifact set (constant names)

Exactly these constitute gold. Anything else under `params/gold/` is migrated, archived, or removed.

```
params/gold/
  gold_provenance.json                   NEW — single source of provenance (§5)
  sampled_runtime_manifest.json          stable name; internal module paths become slug-free
  runtime_bundles/<module>/…             the <slug>/ level removed; 12 module dirs directly here
  fusion/fusion.json                     was fusion_<slug>.json
  uncertainty_calibration/unc_cal.json   was unc_cal_<slug>.json
  compound_prior/<year>/…                already constant
  weights_best.json                      already committed (legacy weight copy)
```

The **slug stays on the build/candidate/archive side** (`outputs/evo_runs/<slug>/`, `reports/evo/*_<slug>.*`, `gold_archive/<slug>/`) where multiple runs coexist. The live gold is slug-free.

Legacy schema-v3 March files still read by tooling — `per_race_metrics.json` (pipeline_validation), `command_meta.json` (summarize_training_history), `config.json` — are **load-bearing**. Resolution in §8: regenerate them in the candidate build so they share the live provenance, or migrate the consumers off them. Truly-orphaned March files (`metrics_*`, `baseline_*`, `race_*_latents`, `pipeline_manifest.json`) move to `gold_archive/legacy-schema-v3/`.

## 5. Provenance schema — `gold_provenance.json`

```json
{
  "slug": "gold_cycle_260608_043414_2018thru2024",
  "schema_version": 1,
  "model_arch": "latent_power_v4",
  "train_years": [2018, 2019, 2020, 2021, 2022, 2023, 2024],
  "eval_year": 2025,
  "created_at": "2026-06-08T04:34:14Z",
  "promoted_at": "2026-06-10T00:00:00Z",
  "promoted_by": "fredcai6",
  "git_sha_at_promotion": "…",
  "supersedes_slug": "gold_cycle_…",
  "manifest": "sampled_runtime_manifest.json",
  "fusion": "fusion/fusion.json",
  "backtest_evidence": {
    "multiseason_fantasy": {"2022": 831, "2023": 963, "2024": 835, "2025": 849},
    "human_reference":     {"2022": 739, "2023": 632, "2024": 615, "2025": 711},
    "report": "reports/walkforward/multiseason_fantasy.json"
  },
  "leakage_attestation": {"eval_year_excluded_from_train": true}
}
```

**Hard invariant** asserted at build, promote, and validation: `eval_year ∉ train_years`.

## 6. Lifecycle & `scripts/promote_gold.py`

Build → evaluate → promote → commit:

1. **Build candidate** into `params/gold_candidate/` (constant layout). The gold-cycle + fusion + materialize target the candidate dir, writing constant names + a draft `gold_provenance.json`.
2. **Evaluate the candidate** — `pipeline_validation` + the multi-season fantasy backtest (§7) — pointed at `gold_candidate/`, **never** `params/gold/` (§9 guard). Evidence is written into the candidate's provenance.
3. **Promote** — `scripts/promote_gold.py --candidate params/gold_candidate` (replaces "implicit promotion"):
   - Re-assert: provenance present + `eval ∉ train` + required evidence present + validation green.
   - Physically move current `params/gold/` → `params/gold_archive/<old_slug>/`.
   - Physically move `params/gold_candidate/` → `params/gold/`.
   - Finalize `gold_provenance.json` (`promoted_at`, `git_sha_at_promotion`, `supersedes_slug`).
   - **Atomicity:** stage into a temp sibling, then `os.replace` into place; on any failure, roll back from temp/archive. `--dry-run` prints the plan with no moves.
4. **Commit** the new `params/gold/` (you commit; the script does not auto-commit). Archive/candidate stay out of git.

## 7. Mechanized multi-season fantasy backtest

Promote `.agent-work/multiseason-fantasy/` into committed tooling:

- `scripts/run_multiseason_fantasy_backtest.py` (+ a small `src/fantasy_scoring/multiseason.py` for the season-loop/scoring glue, reusing `season.py` + `scoring_rules.py`).
- **Input:** a candidate's **LOSO fold** manifests (`outputs/evo_runs/gold_module_training_cycle/loso_folds/heldout_<Y>/`) for 2022–2024 + the held-out eval year (full gold) for 2025 — each provably excluding its own eval season.
- **Output:** committed evidence table (model vs human, per season) → `reports/walkforward/multiseason_fantasy.{json,md}`, plus a compact summary embedded in `gold_provenance.backtest_evidence`.
- Human reference numbers committed as a constant (`2022=739, 2023=632, 2024=615, 2025=711`).
- **Pre-quali only** (`sampled_state`); the existing leakage guard (refuse oracle / non-`sampled_state`) is retained.

This is the promotion **evidence gate**: a candidate is promotable only with a current multi-season evidence run, and the numbers travel in provenance for trend-tracking across promotions.

## 8. Migration (one-time, the live June gold)

The current `params/gold/` is slugged. Migration (implementation phase P1) keeps pipeline_validation green throughout:

- Rename `runtime_bundles/<slug>/` → `runtime_bundles/` (drop slug level); rewrite `sampled_runtime_manifest.json` internal module paths to slug-free.
- Rename `fusion/fusion_<slug>.json` → `fusion/fusion.json`; `unc_cal_<slug>.json` → `unc_cal.json`.
- Write the first `gold_provenance.json` for the live June gold (evidence already computed: 831/963/835/849).
- Update consumers that assume slugged layout:
  - `scripts/run_pipeline_validation.py` globs `fusion_*.json` / `unc_cal_*.json` → match the constant names.
  - `scripts/assemble_trained_sampled_runtime_manifest.py` `fusion_*` glob.
  - The three "newest `gold_cycle_*` dir in `params/gold/runtime_bundles/`" auto-discoverers (`export_pairwise_predictive_vs_retro.py`, `plot_predictive_vs_retro.py`, `report_predictive_retro_alignment.py`) → read the constant gold path.
  - `scripts/accept_quali_anchor_420.py` hardcoded `BUNDLE_NAME` slug → constant path.
  - `scripts/materialize_runtime_bundles.py` → emit the constant layout into the candidate dir.
- Move orphaned schema-v3 March files → `gold_archive/legacy-schema-v3/`; keep load-bearing ones until their consumers migrate (tracked follow-up).
- Add `params/gold_candidate/`, `params/gold_archive/` to `.gitignore`.

## 9. Backtest isolation guard ("doesn't use gold")

Candidate evaluation must target the candidate, not the live model. The multi-season / candidate-eval entrypoints take an explicit `--gold-root` (default `params/gold_candidate`) and **raise** if it resolves to `params/gold/` in candidate-eval mode. (Forward prediction against the live gold stays allowed — the rule is specific to pre-promotion evaluation.)

## 10. pipeline_validation provenance gate

Extend `run_pipeline_validation.py` with a `provenance` section: `gold_provenance.json` present + well-formed; `eval_year ∉ train_years`; the manifest + fusion provenance agree with it; and `params/gold/` contains **exactly** the §4 artifact set with **no extra files** (a stray `per_race_predictions/` would fail here). This is the automated catch the March leak slipped past.

## 11. Testing

- **Unit:** `promote_gold.py` move/archive/atomicity (temp+rename, rollback on failure, dry-run); provenance schema validation; the `eval ∉ train` invariant; the §9 guard.
- **Unit:** multi-season scorer (port the `score_season` `sampled_state`/oracle-refusal guard tests).
- **Integration:** a synthetic candidate promoted end-to-end (dry-run + real) in a tmp area; pipeline_validation provenance section green/red cases.

## 12. Implementation phases

- **P1 — Layout + provenance + validation gate + migration** of the live June gold (constant names, first `gold_provenance.json`, consumer fixups, gitignore). Repo stays green.
- **P2 — `promote_gold.py`** (physical potential→gold→archive, atomic, dry-run) + the §9 backtest-isolation guard.
- **P3 — Mechanized multi-season backtest** (committed tooling + evidence into provenance).
- **P4 — Runbook**: rewrite the `docs/evo/analysis_refresh.md` promotion section around the lifecycle; comment the post-mortem + design on #440.

Each phase is independently shippable and leaves the repo green.

## 13. Risks / open questions

- **Load-bearing March files** (`per_race_metrics.json`, `command_meta.json`, `config.json`): regenerate-in-build vs migrate-consumers — resolved case-by-case in P1; may spill a small follow-up.
- **Binary bundle moves + git**: renaming bundle dirs is a large but one-time diff; archive/candidate are gitignored, so no ongoing churn.
- **Concurrency**: promote assumes a single operator (no concurrent gold writer); documented, not locked.
