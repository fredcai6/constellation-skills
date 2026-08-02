# Mission Frame — #604 race-week command (BUILD, Wave 2)

## Intent
Build `scripts/race_week.py` + `scripts/race_week_stages.py`: a staged, resumable pipeline
(collect-check -> predict -> optimize -> explain) that turns landed FP/sprint session data for
one race weekend into a submittable ranked top-10 (hard) plus a beam-search markdown explainer
(soft), per the owner-ratified Candidate C design (`docs/design/race_week_seam.md`). Prove it
end-to-end on real 2026 R9 Great Britain data. `scripts/` level only — no `src/` changes.

## Affected Capabilities
- **evo_predictor sampled-predict** (`src/evo_predictor/run.py:cmd_sampled_predict`) — this run's
  `predict` stage is a subprocess/in-process caller, not a modifier. Consumed as-is.
- **fantasy_scoring beam search + report** (`src/fantasy_scoring/beam_search.py`,
  `src/fantasy_scoring/artifacts.py`) — this run's `optimize` stage calls `generate_report` /
  `write_beam_search_report` unmodified; `--lane` selects which of the exposed best-candidates to
  surface as the top-10.
- **session-shape discovery** (`src/utils/constants.py:get_practice_session_types`) — sole source
  for the `collect-check` stage's expected-session list; no re-derivation.
- **partial-data poll** (`DatabaseManager.has_session_classification`) — drives `collect-check`'s
  landed/missing diff.

## Structural Anchors
- `struct:scripts` (script-level, not a map node per `docs/architecture/index.md` convention —
  confirmed: `collect_evo_data.py`, `run_sampled_runtime_comparison.py` are existing precedent)
- `struct:evo_predictor` (container) — consumed via `run.py` CLI surface only
- `struct:fantasy_scoring` (container) — consumed via `artifacts.py`/`beam_search.py` in-process
  imports (already-sanctioned `evo -> fantasy_scoring` composition per #439 walkforward)

## Governing Constraints / Assumptions
- DB-only analysis: no live FastF1 calls outside `collect_evo_data.py` (the `collect-check` stage
  only ever shells to it; never re-implements collection).
- Per-year DB routing is correctness-critical: `sampled-predict --db-path` defaults to the single
  fixed `Config.DATABASE_PATH` (`data/f1_data.db`), NOT `Config.db_path_for_year(year)`. Every
  `predict` invocation this run authors MUST pass `--db-path` explicitly (verified at
  `src/data/database/_core.py:125`, `DatabaseCoreMixin.__init__`).
- `sampled-predict` additionally REQUIRES one of `--compound-prior-root` /
  `--compound-prior-artifact` (raises `ValueError` if neither given, `run.py:544`
  `_compound_normalizer_for_sampled_predict`) — the design doc's bracket notation
  `[--compound-prior-root | --compound-prior-artifact]` reads as optional; it is not. Canonical
  repo-wide default value is `params/gold/compound_prior` (grep-confirmed across
  `run_sampled_runtime_comparison.py`, `run_residual_backtest.py`, `report_predictive_retro_alignment.py`).
- `lesson:worktree-untracked-data` — the worktree's `data/f1_data_2026.db` is a stale, base-commit
  copy (rounds 1-7 only); the MAIN CHECKOUT'S `data/f1_data_2026.db`
  (`C:/Programs/f1Brainz/data/f1_data_2026.db`) carries round 8/9 (cmdr-603's collection run). The
  e2e proof for this build MUST target the main-checkout absolute path.
- `--lane {mean,risk,balanced}` NOT `{mean,risk,balanced,max}` — see Decision Pressure below.

## Decision Anchors & Decision Pressure
- `decision: Candidate C ratified` (owner Tommy, 2026-07-12, cited in launch order) — fixes the
  4-stage checkpoint shape and `scripts/`-level placement. Not reopened this run.
- **Decision pressure (resolved, documented, not floated):** the launch order and design doc both
  assert `FantasyBeamSearchResult` exposes 4 best-lanes (`.best_mean/.best_risk/.best_balanced/.best_max`).
  Source (`src/fantasy_scoring/beam_search.py:52-63`, dataclass fields; `:396-421`,
  `beam_search_lineups` construction) shows only 3: `best_mean`, `best_risk`, `best_balanced`.
  `"max"` is solely an internal beam-diversity pool label (`_keep_beam` lane_counts) with no
  exposed candidate. This is a genuine seam-contract contradiction, not a plan choice — resolved
  per the Honest-Null Clause and the pre-ruling's own "overridable if evidence contradicts" text:
  `--lane` ships with 3 choices, default `balanced`. Documented in the closeout report, not floated
  (within latitude: "adjust stage boundaries to match reality and document what changed and why").
- **Decision pressure (resolved):** `generate_report` CONSUMES a written sampled-runtime JSON
  (`load_json_object(sampled_runtime_path)`) — it does NOT re-run prediction. Confirms `predict`
  and `optimize` are DISTINCT stages exactly as the design doc's stage shape assumed (02 -> 03).
- **Decision pressure (resolved, per launch order Known-Limits item 7 recommendation):**
  `collect-check` is report-only in v1 — it diffs expected-vs-landed and reports the gap; it does
  NOT auto-invoke the collector. Matches the launch order's own stated lean and keeps the R9 proof
  (data already collected) from accidentally triggering a live FastF1 call.

## Claims / Evidence Surfaces
- `claim: 2026 R9 Great Britain is a sprint weekend` — verified via
  `is_sprint_weekend(2026, "Great Britain") == True`,
  `get_practice_session_types(2026, "Great Britain") == ["FP1", "SQ", "S"]`.
- `claim: R9 data present in main-checkout DB` — verified via direct sqlite3 query against
  `C:/Programs/f1Brainz/data/f1_data_2026.db`: round 9 has FP1/Q/R/S/SQ rows. The WORKTREE copy
  does NOT (rounds 1-7 only) — re-confirm at the e2e gate, don't trust this snapshot silently.
- `claim: gold manifest + compound prior root present in worktree` — verified:
  `params/gold/sampled_runtime_manifest.json` and `params/gold/compound_prior/` both exist
  (tracked artifacts, unlike the DB).

## Map Confidence / Staleness / Disputes
- `scripts/` is deliberately NOT a Cartographer map node (design doc + repo convention); no
  reconcile-step map edit is expected for this run's new files themselves. Reconcile still checks
  whether the *seam usage* (evo -> fantasy_scoring composition point) needs a map note.
- The design doc's "4 lanes" claim is stale/wrong per Decision Pressure above — this is now fixed
  by direct source read, not deferred.

## Out of Scope
- Any `src/` change (including the `sampled-predict --db-path` default-fallback footgun — filed as
  a triage candidate, not fixed here, per explicit Pre-Ruling).
- A net-new race-preview narrative explainer (explicitly deferred; v1 explainer = reused beam-search
  markdown, zero new prose code).
- Auto-invoking the collector from `collect-check` (report-only v1, per Known-Limits item 7).
- Concurrent-invocation locking (single-writer assumption, documented not enforced, per Known-Limits
  item 6).
