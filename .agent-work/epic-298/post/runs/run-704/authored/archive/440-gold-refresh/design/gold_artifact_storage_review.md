# Gold-cycle artifact storage — retrospective review (issue #370)

Last verified: 2026-06-07

A **step-back review**, not an implementation spec. The question is *are we storing
gold-cycle artifacts well?* — in a shape that makes phase-by-phase backtesting and
experimentation cheap, without re-deriving what the cycle already computed and without
cluttering the tree. The concrete near-term emit that unlocks the fusion experiments
(#371, the per-event module record) has already landed as a first slice; this doc takes
the wider view and recommends what to do next.

---

## Verdict (one line)

**The metric/report side is over-engineered and the heavy-data side is under-engineered.**
Reports carry a hand-maintained 624-line schema that churns on every field add, while the
per-event arrays that experiments actually need (`pi`, full `sigma_pi`, input features) are
recomputed from the DB on every run. The #371 record is the right primitive and should be
generalized into a **per-event "collect-once" sidecar + a thin JSON table-of-contents**,
default-on for gold. Recommendation: **invest in the restructure, but incrementally** — the
record format already exists and has a working consumer; the remaining work is promotion,
a TOC, retention, and trimming the report schema. Do *not* do a big-bang `details.json`
rewrite.

---

## 1. Current artifact map

The gold cycle runs **train → backtest (eval) → sampled-runtime backtest → fusion-train /
LOSO calibration → report**. What each stage writes and reads today:

| Stage | Writes | Path | Format | Read back by |
|---|---|---|---|---|
| Train (per module) | `latent_power_manifest.json`, `model_checkpoint.pt`, `module_diagnostics.json`, `training_batches.json` | `output_dir/modules/{module}/` | JSON + torch binary | Backtest, manifest assembly |
| Backtest (eval) | `{module}.json` (aggregate + per-event **scalars**) | `output_dir/backtests/` | JSON | Report assembly, fusion-train, calibration |
| Backtest (eval) | `{module}.record.npz` + `.record.json` **(only if `emit_module_record`)** | `output_dir/backtests/` | npz + JSON index | `scripts/fusion_replay/` (#373) |
| Sampled-runtime | `sampled_runtime_manifest.json` | `output_dir/` | JSON | Sampled backtest, report copy |
| Fusion-train / LOSO | LOSO rows, calibration entries (in-memory) | — | — | Folded into report + calibration artifact |
| Report | `{slug}.summary.json`, `{slug}.details.json`, `{slug}.md`, `{slug}.sampled_runtime_manifest.json` | `report_dir` (`reports/evo/`) | JSON + MD | `html_reports/`, validation, rt-comparison, fusion-train |
| Report | `unc_cal_{slug}.json` | **`params/gold/uncertainty_calibration/`** (hardcoded) | JSON | Runtime fusion, next cycle's calibration |
| Report | `{slug}.json` / `.md` uncertainty diagnostics, regenerated schema doc | `report_dir`, `docs/evo/` | JSON + MD | Post-cycle review |

Three tiers, three retention stories: **transient** (`outputs/evo_runs/…`, user-managed),
**committed reports** (`reports/evo/`), **committed params** (`params/gold/`).

### Measured sizes (committed full-gold artifacts, 2026-06)

| Artifact | Size | Ratio to summary |
|---|---|---|
| `{slug}.summary.json` | 5–59 KB | 1× |
| `{slug}.details.json` | **0.8–3.7 MB** | ~50–700× |
| `unc_cal_{slug}.json` | 13–27 KB | — |
| `.record.npz` (est., 12 modules × ~20 events) | ~2–3 MB compressed | — |

`details.json` is the monolith the issue names: 0.8–3.7 MB of mostly per-event scalar
metric rows (`modules[*].event_level_metrics[*]`) plus `fusion_train_rows[*]`. It is
~50–700× its own summary, and it is the artifact every consumer opens for drilldown.

### Reproductions of the named line references

- **Discard site** — `module_training_orchestration.py:617-648`: each event computes
  `pred.latent_power` (π) and `pred.sigma_pi`, uses π once for rank metrics, and keeps
  **only scalars** (`field_std`, `sigma_pi_trace`, NLL, rank metrics). The π vector and the
  full σ_π matrix are dropped unless `collect_record=True`. (The issue cited `:541-550`; the
  #371 work shifted these into `_build_event_record` at `:538-580`.)
- **Calibration path** — `gold_cycle/runner.py:343-345`: `calibration` is hardcoded to
  `params/gold/uncertainty_calibration/{slug}.json` while `md`/`summary`/`details`/`manifest`
  all derive from `report_dir`.
- **#371 record** — `module_record.py`: `write_module_record` spills `{stem}.record.npz`
  (arrays keyed `ev{:04d}__{suffix}`) + `{stem}.record.json` (stdlib index). Gated by
  `emit_module_record` (config) / `--emit-module-record` (CLI), default off, gold mode rejects
  the override.

---

## 2. Where data is duplicated or lost

### Lost: per-event outputs (the fusion blocker)

`pi` and the full `sigma_pi` covariance are computed in the backtest and thrown away. Any
fusion variant (correlated covariance #373, partial pooling, residual re-targeting,
interaction headroom #374) needs them, so without the record every experiment re-runs
inference over all 12 modules × all eval events. The #371 record fixes exactly this — and
`scripts/fusion_replay/records.py` already consumes it — but it is **default-off**, so the
canonical gold run does not produce it.

### Lost: per-event inputs (the re-target blocker)

The pair batches (`features`, `dqi`, `pair_index`, `entity_ids`) are rebuilt from the DB +
practice preprocessor on every run and never persisted outside the record. Retraining one
module on a new target (e.g. a learned `s_e` head) means a full preprocessor re-run to
regenerate inputs the cycle already built. The #371 record captures these too — same gating
caveat.

### Duplicated: metrics live in three places

The same per-event scalar metric (e.g. `pairwise_nll`) is written into the backtest
`{module}.json` `per_event[]`, then copied into `details.json`
`modules[*].event_level_metrics[*]`, then re-aggregated into `summary.json`
`modules[*].performance`. `details.json` is essentially a re-serialization of the backtest
JSONs plus the in-memory fusion/calibration rows — a second copy of data already on disk.

### Lost-then-recovered: covariance trace only

`sigma_pi_trace` (a scalar) survives into reports, but the matrix it summarizes is gone.
Calibration fits α/β against the trace; correlated-covariance fusion needs the off-diagonal
structure the trace discarded.

---

## 3. Schema churn

`gold_report_schema.py` is a **624-line hand-maintained `ReportField` registry**
(`SUMMARY_FIELDS` + `DETAIL_FIELDS`), currently **v6**. Every nested field — down to
`modules[].event_level_metrics[].pairwise_nll` — is enumerated with nine attributes, and
`validate_documented_fields` fails the run if an emitted key is undocumented. So **adding one
metric touches the producer, the registry, the regenerated markdown doc, and often the
version constant**. The version-note history is the evidence: v3 (split summary/details), v5
(#303 field removal), v6 (#323/#324/#326 metric rename + adds). The schema churns because the
*stable metric index* and the *evolving per-event payload* are governed by one monolithic
contract.

There is also a parallel/duplicate schema doc problem already logged as an open structural
question: field shapes appear in both `docs/evo/gold_module_training_cycle_report_schema.md`
and `docs/report_schemas/gold_module_training_cycle.md`.

---

## 4. Path and retention defects

- **Calibration promotion ignores config** (`runner.py:343-345`). Every run — including
  smoke/research/evidence runs fully isolated to an `.agent-work` dir — writes the
  uncertainty-calibration artifact into the canonical `params/gold/` tree. Caught in the #371
  G4 evidence run.

  **Key constraint (traced 2026-06-07): the calibration artifact is a *parameter*, not a
  report.** It is consumed as a fusion-training *input* (`fusion_training/_train.py:104,117`,
  passed explicitly by the caller), discovered by pipeline validation via a hardcoded glob of
  `params/gold/uncertainty_calibration/unc_cal_*.json` (`run_pipeline_validation.py:52`), and
  pruned as a `params/` family (`prune_gold_artifacts.py:59`). It lives in `params/gold/`
  alongside `compound_prior` / `fusion` / `runtime_bundles`. Runtime/manifest assembly do **not**
  read it. So routing it through `report_dir` (which for gold is `reports/evo`) would *relocate a
  canonical param into the reports tree* and break the validation glob + prune family + the
  operational runbook (`docs/evo/analysis_refresh.md:258`).

  The bug is narrower than "ignores config": **non-gold/isolated runs should not write into
  `params/gold/`, but gold runs should.** Fix: make the calibration directory **config-driven**,
  defaulting to `params/gold/uncertainty_calibration` for the gold profile, with isolated
  research/smoke/evidence profiles pointing it at their own output/report dir. Gold's canonical
  location is unchanged (zero churn to validation/prune/runbook); isolation falls out because the
  isolated profile already overrides its output dirs. This is the "respect config like the other
  artifacts" spirit without mis-classifying a param as a report. (Equivalent to mode-gate (b) but
  expressed as a config default rather than a hardcoded `if mode == "gold"`.)

  **Landed (2026-06-07):** `GoldCycleOutputsConfig.uncertainty_calibration_dir` (default
  `params/gold/uncertainty_calibration`), threaded into `_build_artifact_paths`; `smoke_defaults`
  and `fusion_calibration_loso` now override it into their own output trees. Gold's location is
  unchanged, so validation/prune/runbook are untouched and gold reports stay byte-identical
  (the dir is not added to `run_config`).

- **Retention is manual and incomplete.** `scripts/prune_gold_artifacts.py` (#359) exists,
  dry-run by default, keeps newest **N=2** per family. But: it is not run as part of the
  cycle, it only covers the new timestamped slug convention (legacy
  `gold_module_training_cycle_*` / `static_hierarchical_fusion_*` are left untouched), and the
  committed tree currently holds **8+ accumulated detail sets** (0.5–3.7 MB each) plus 7
  `unc_cal` files. The owner's stated goal — "only one gold set at a time" — is not enforced.

  The retention goal is **two-tier**, not "keep N": the **heavy** artifacts (details.json,
  records, bundles, working DBs) are regenerable — the DB *and* the producing commit are both
  in the repo — so only the **newest 1** need be retained. But **performance history must be
  kept forever**: a lean, append-only record of each run's headline stats tied to the commit
  that produced them. That history is the trend line ("did skill move after commit X?") and is
  tiny. See §5.6.

---

## 5. Proposed per-stage layout

The shape the owner sketched — **a JSON table-of-contents + denser numpy save files, one
gold set retained** — generalizes the #371 record. Concretely:

### 5.1 Collect-once per-event record (generalize #371)

Promote `emit_module_record` to **default-on for gold**. The record already holds the minimal
per-event tuple that serves every known consumer:

- **inputs**: `features`, `dqi`, `pair_index`, `entity_ids`, `feature_names`/`schema_version`
- **labels**: `target_mu`, `outcome`, `actual_positions`
- **outputs**: `pi`, full `sigma_pi`

That set covers fusion replay, module re-target, metrics, and reports — nothing downstream
needs to re-derive. Keep `format_version` as the record's own contract, decoupled from the
report schema version.

**Scope: full run, local-only (decided 2026-06-07).** The emit is already threaded into all
three backtest builders (main eval, the 7 LOSO folds, and the calibration-fit backtests), so
default-on for gold captures the *whole* set — ~170 races (2018–25), not just the eval year.
This is the right scope because the motivating experiments operate on all years (#373 scored
**173 races**); eval-year-only (~24 races) is too thin to estimate cross-module correlation or
train a new head, and a "dedicated profile" reintroduces the #370 smell by paying to re-run
backtests later. Records are **gitignored** (local-only, ~20–30 MB compressed/run) — the cost
is noise next to training 12 modules × 7 folds, and they are a byproduct of work the cycle
already does. (Alternatives weighed: eval-year-only needs new code to *restrict* what already
works; dedicated profile keeps gold pristine but re-derives.)

**Landed (2026-06-07):** `gold_defaults.toml` `emit_module_record = true`; records spill under
`output_dir` (gitignored). Committed gold reports stay byte-identical (the flag is not echoed
into `run_config`).

### 5.2 First-order data in JSON, heavier detail in npz

Stop making `details.json` a second copy of the backtest JSONs. Keep **first-order data in the
JSON** (headline + per-event metrics, indices, provenance, run identity) and push the **heavier
per-event arrays** (`pi`, full `sigma_pi`, features) into associated **npz** sidecars — which is
already the #371 record's job. The split does not need to be perfect: this is an internal data
file and the bar is **traceable, not tidy**. A little data living in both the JSON and a sidecar
is acceptable if it keeps the JSON honest and self-describing. Format is settled: **npz** —
numpy-native, compressed, no new dependency; we use numpy everywhere and these are internal
files, so columnar/cross-language stores (arrow/parquet) are not worth the dependency.

### 5.3 The JSON is its own table-of-contents

No separate `toc.json`. Keep it all in one honest JSON: the report JSON carries the run identity
(slug, train/eval years, git commit), the schema/format versions in play, and **inline pointers
to its own npz sidecars** (per-module → record path, by `event_id`). One file is the entry point
and the index; "honest" means those pointers always resolve and the JSON never silently diverges
from the sidecars it names. This keeps the greppable-without-numpy property without a second
artifact to drift.

### 5.4 Stable index vs evolving payload (schema)

Split the report contract: a **small stable index schema** (run identity, module list,
artifact pointers, headline metrics — changes rarely) versus the **evolving per-event payload**
(versioned by the record's `format_version`, not the report `schema_version`). New metrics land
in the payload without bumping the index or churning the 624-line registry.

### 5.5 Single-set-in-repo, generous-locally retention

The "one gold set" rule is about **what is committed to the repo**, not about local files.

- **Committed (git):** don't carry two heavy gold sets at once. When a new gold set is
  committed, the previous heavy artifacts come *out of git* (kept out via gitignore, or
  replaced in the commit) — but the lean performance history (§5.6) stays committed forever.
- **Local:** keep the newest full set **always available**, including the interim
  hypothesis-testing artifacts produced between full training runs. **Not aggressively pruned**,
  and **no auto-delete of the prior run when the next run completes** — interim work must stay
  fully on hand. Pruning local heavy data is an explicit, manual act, never a cycle side-effect.

Heavy artifacts are regenerable from the committed DB + the producing commit, so the in-repo
dedup loses nothing permanent. The prune script needs to (a) distinguish committed-vs-local
intent, (b) cover all slug conventions including legacy, and (c) never fire automatically on
run completion.

### 5.6 Performance-history ledger (keep forever)

Separate from heavy-artifact pruning, keep a **lean, append-only, committed** history so a
trend never gets pruned away. The raw material already exists: every `summary.json` carries
the per-module `performance` block and `run_config.git_commit` (5–59 KB). Two realizations:

- **Distilled ledger** — an append-only file (JSONL, one row per run: `git_commit`,
  `train_years`/`eval_year`, per-module `pairwise_nll_skill` / `rank_mae` / `pairwise_sign_accuracy`,
  calibration α/β, `data_coverage` headline). Leanest, directly graphable, but a new artifact
  whose column set is chosen up front.
- **Keep-all-summaries** — exempt `summary.json` from the heavy-artifact prune so summaries
  accumulate while everything else is pruned to newest 1. Zero new code, full fidelity, grows
  ~tens-of-KB per run; a trend is reconstructed by reading across files.

These are not exclusive — defaulting to keep-all-summaries *and* appending a ledger row gives
both a durable trend file and full per-run fidelity. The ledger is keyed by commit so
performance is always attributable to the code that produced it.

**Decided 2026-06-07: both, staged.** Do **keep-all-summaries first** — near-zero code (narrow
the prune families to exempt `summary.json`), immediately stops history loss at full fidelity.
Add the **distilled ledger** when trend plots are wanted; it is a pure projection of the
summaries it distills (no second source of truth). Size is a non-issue either way (~50 KB/run →
a few MB over the project's life). The ledger pins a *stable minimal* column set so the trend
survives summary-schema churn (currently v6).

Retention + history (§5.5–5.6) is carved out as a separable slice in **#426**.

**Landed (2026-06-07, #426):** `scripts/prune_gold_artifacts.py` is now two-tier — heavy files
(`.details.json`, manifests, params, bundles) prune to newest **1** while `.summary.json` (+ the
lean `.md`) are exempt and kept forever; legacy `gold_module_training_cycle_*` /
`static_hierarchical_fusion_*` families are covered (heavy pruned, summaries retained). It stays
explicit/manual (dry-run default, `--apply` to delete) — never an automatic cycle side-effect.
The distilled ledger is `scripts/build_performance_ledger.py` → committed
`reports/evo/performance_ledger.jsonl`, a pure idempotent projection of the summaries keyed by
`git_commit`, tolerant of per-module metric churn across schema versions.

---

## 6. Weaknesses of the proposed layout & alternatives (open — to discuss)

Recorded so the trade-offs are explicit; the final call is deferred to the review conversation.

- **Default-on full-run records cost disk + write time** (~20–30 MB compressed/run across eval
  + 7 LOSO folds, plus tensor→numpy per event). Accepted (§5.1): local-only/gitignored, and
  trivial next to the training the cycle already does. Residual risk is local-disk growth if the
  newest-1 retention (§5.5) isn't kept current.
- **JSON ↔ npz can desync** — the report JSON names sidecars that might not match (half-failed
  write, stale file). This is the cost of "keep it honest": the inline pointers (§5.3) must
  always resolve. Mitigated by the existing atomic-write + all-or-nothing emit guard; a
  read-time check that every named sidecar exists makes dishonesty loud rather than silent.
- **Splitting first-order/detail across JSON+npz is deliberately imperfect** (§5.2) — some data
  may live in both, and where the line falls is judgement, not rule. Accepted: internal file,
  traceable-over-tidy. Risk is only that "first-order" creep slowly re-fattens the JSON; worth a
  periodic size check, not a hard schema.
- **Slimming details.json breaks current consumers** (`html_reports/`, validation, rt-comparison)
  that read the fat file. Needs a migration shim (§7), and the JSON must still satisfy whatever
  the dashboards read today.
- **In-repo dedup vs local diffing** — keeping one heavy set *in git* doesn't block local
  diffing, because locally the newest full set (and interim work) is retained un-pruned (§5.5);
  and the committed performance-history ledger (§5.6) preserves the cross-run trend regardless.

Alternatives to the whole approach worth weighing: (a) **keep patching** — leave reports as-is,
just default-on the record and add retention (smallest change, unblocks experiments); (b) **DB
as artifact store** — write per-event records into a SQLite sidecar instead of files
(queryable, single file, but cuts against "greppable" and adds write coupling); (c) **full
restructure** — lean index + sidecars + TOC + retention as one coherent layout (most work,
cleanest end state).

---

## 7. Recommendation & migration path

**Invest, incrementally — option (a) now, growing toward (c); avoid a big-bang rewrite.**

The record primitive already exists and has a real consumer, so the highest-value, lowest-risk
moves are:

1. ✅ **Fix the calibration path** (§4) — config-driven calibration dir (gold default
   `params/gold/uncertainty_calibration`; isolated profiles override). *Landed 2026-06-07.*
2. ✅ **Default-on the record for the canonical gold run** (§5.1) — `emit_module_record = true`
   for gold; records spill under the gitignored `output_dir`. *Landed 2026-06-07.*
3. ✅ **Retention + performance history** (§5.5–5.6, #426) — two-tier prune (heavy → newest 1,
   summaries kept forever, legacy covered) + the commit-keyed `performance_ledger.jsonl`
   projection; explicit/manual, never an automatic side-effect. *Landed 2026-06-07.*
4. **Make the report JSON self-indexing** (§5.3) — inline pointers to its npz sidecars; thin,
   additive, no consumer migration needed (no separate TOC file).
5. **Split first-order/detail and slim `details.json`** (§5.2/5.4) — the largest change; do it
   last, behind a shim: keep emitting the fat `details.json` until `html_reports/` + validation +
   rt-comparison read the slimmed JSON + sidecars, then flip. Default off, then default on, then
   remove.

Back-compat: every step is additive or gated; existing consumers keep working until they are
migrated. The migration cost concentrates entirely in step 5, which is why it is sequenced last
and shimmed.

---

## Open questions to settle in review

- (none outstanding — see settled block)

**Settled in review (2026-06-07):**
- Format: **npz** for heavy arrays — internal numpy data file; no arrow/parquet.
- Index: **no separate TOC** — one honest JSON that points at its own npz sidecars (§5.3).
- Split: **first-order data in JSON, heavier detail in npz**; imperfect is fine, traceable
  over tidy (§5.2).
- Records scope: **full run (eval + LOSO + calib-fit), default-on for gold, local-only/
  gitignored** (§5.1).
- History: **both, staged** — keep-all-summaries first, distilled ledger when wanted (§5.6).
- Calibration path: **config-driven dir, gold default `params/gold/uncertainty_calibration`**,
  isolated profiles override — it's a param, not a report, so it stays in `params/gold/` for
  gold (§4).
- Retention: **one heavy set in the repo**, but locally **keep newest 1 always + interim work,
  un-pruned, no auto-delete on run completion**; lean history committed forever (§5.5–5.6).
