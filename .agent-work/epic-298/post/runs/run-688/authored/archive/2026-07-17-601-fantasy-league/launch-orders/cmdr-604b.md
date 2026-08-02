# Launch Order: cmdr-604b — #604 race-week command BUILD (Wave 2)

## Mission
Issue #604 (epic #601, Track 1), **build phase**. Build the `race-week` command against the RATIFIED seam (Candidate C, ratified by owner Tommy 2026-07-12). It chains: collect FP/sprint sessions → sampled-runtime predict → beam-search lineup → emit (a) a single submittable ranked top-10 (HARD deliverable) and (b) a race-preview explainer (SOFT). This is the co-pilot loop the whole epic is built around; Belgium R10 (~2026-07-18 quali) is its live plumbing shakedown.

## Prior-Wave Verdicts (pasted)
**Wave 1 seam design (cmdr-604d, PR #612 MERGED to main as `docs/design/race_week_seam.md` — READ IT, it's in your worktree).** Recommended + owner-ratified: **Candidate C — staged pipeline with checkpoint files, at `scripts/` level (NOT a new `src/` package/region).** Four stages, each reads the prior stage's checkpoint from `outputs/race_week/<year>/<round>/` and writes its own:
- `01_sessions.json` — `get_practice_session_types(year, gp_name)` cross-referenced vs `has_session_classification` per session (status complete|partial|missing, landed list).
- `02_prediction.json` — the sampled-predict payload.
- `03_lineup.json` — the beam-search lineup report + a top-level `"lane_used"`.
- `04_explainer.md` (or `04_explainer.STUB.md` on skip/failure).
Resumption via checkpoint presence + an embedded `stage_inputs_hash` (skip fresh stages, rerun when upstream inputs changed).

## Owner ratification — build parameters (LOCKED, from Tommy 2026-07-12)
1. **Candidate C in full** (checkpoints/resume) — the multi-look pattern is real: Monday-morning lookahead after the previous race, refresh after Friday activities, refresh before quali. Do NOT ship the minimal-A single-shot variant.
2. **DB: per-year `data/f1_data_2026.db`, threaded EXPLICITLY.** (Correctness-critical footgun below.)
3. **Manifest: default to promoted GOLD for real predicts; `--manifest` override for testing.** Gold manifest = `params/gold/sampled_runtime_manifest.json`.
4. **Explainer v1 = REUSE the existing beam-search markdown** (`generate_report` / `write_beam_search_report`) — zero net-new prose code. A net-new race-preview narrative is deferred (out of scope this wave).

## Pre-Rulings
Each overridable if evidence from source contradicts — say so when overriding.
- **DB-path footgun (correctness requirement, CONFIRMED from source):** `sampled-predict`'s `--db-path` defaults to `None` → resolves to the single fixed `Config.DATABASE_PATH = data/f1_data.db` (src/utils/config.py:32), **not** the year-routed `data/f1_data_2026.db` that `collect_evo_data.py` writes. Every predict call MUST pass `--db-path` (or `--db-root`) so it reads the per-year DB. Add an explicit acceptance check for this. **Do NOT "fix" the src default** — that is a separate pre-existing bug (file it as triage); the command works around it by threading the path.
- **Sprint-aware, one canonical source:** the session-shape decision comes ONLY from `get_practice_session_types(year, gp_name)` (src/utils/constants.py:312 — returns FP1/FP2/FP3 normal, FP1/SQ/S modern-sprint). Nothing downstream re-derives session names or hard-codes FP1/FP2/FP3.
- **Hard/soft gate by construction:** `03_lineup.json` (the top-10) MUST be written to disk BEFORE the `explain` stage runs. `explain` failure produces `04_explainer.STUB.md` + exit 0 and never blocks the top-10.
- **Balanced lane is the default, named, swappable:** `--lane {mean,risk,balanced,max}` default `balanced`, mapping to `FantasyBeamSearchResult.best_{mean,risk,balanced,max}`; `03_lineup.json` records `"lane_used"`.
- **Compose over existing seams; no `src/` changes.** Everything new lives under `scripts/` + `tests/`. If you believe a genuine `src/` change is unavoidable, STOP and float — don't cross into src/ silently.
- **Verify the exact producer/consumer contract from source before wiring** (lesson:handoff-cite-exact-seam-signature). In particular: `generate_report(*, sampled_runtime_path, ...)` already composes sampled-runtime → futures → `beam_search_lineups` → report dict. Confirm whether it CONSUMES a prediction payload or RE-RUNS prediction from the manifest — this determines whether your `predict` and `optimize` stages are distinct or whether `optimize` subsumes predict. The design doc fixed the STAGE SHAPE, not every field; adjust stage boundaries to match the real seam contract and note what you changed and why.

## Honest-Null Clause
If a build-time truth contradicts the ratified design (e.g. the gold manifest cannot predict a 2026 race, or generate_report's contract forces a different stage split), that is a real finding — implement the honest correct thing and report the deviation with evidence, don't force the design over a contradicting seam.

## Inherited Latitude
You MAY: build within your fence, self-review via crews, run predictions/collection against the canonical DBs (read-only for data; collection only if a session is missing — but R8/R9 are already present), open a PR (push+PR pre-cleared). You MUST FLOAT to the Admiral: any `src/` change, any scope beyond the ratified 4 params, merging (surfaced — human), closing #604 (surfaced), filing issues (log-and-defer to me). You cannot reach the human; float to me.

## File Ownership
Sole writer this wave of: `scripts/race_week.py`, `scripts/race_week_stages.py` (or your chosen lib module name under scripts/), and `tests/` files for them. Checkpoints write to `outputs/race_week/<year>/<round>/` (gitignored — must NOT be committed). Report: `.agent-work/601-fantasy-league/cmdr-604b-report.md` (main checkout, not committed on branch).

## Workspace
Worktree: `C:/Programs/f1Brainz/.claude/worktrees/604-build` — branch `feat/604-race-week-build`, base `1962e7cc` (current origin/main, includes both Wave-1 merges). Created via `git worktree add .claude/worktrees/604-build -b feat/604-race-week-build origin/main`.
First step, before any git op: `py scripts/verify_worktree_isolation.py --here C:/Programs/f1Brainz/.claude/worktrees/604-build` — must exit 0; paste output into your report. NOTE that script lives at the bundled constellation-commander/scripts/ path if `<repo>/scripts/` doesn't vendor it (cmdr-602 hit this).
PR integration = server-side merge.

## Verified Seams (from the design doc — RE-verify each from source before relying on it)
- **Collection CLI** (only if a session is missing; R8/R9 already collected): `scripts/collect_evo_data.py` — `--seasons`, `--sessions {FP1 FP2 FP3 SQ Q S R}`, `--gp <single GP>`, `--dry-run` (now requires `--worklist`), no `--rounds`. Rate-limit aware.
- **Prediction CLI:** `py -m src.evo_predictor.run sampled-predict --sampled-runtime-manifest <path> --year <int> --race <name> [--db-path <per-year.db> | --db-root data] [--output <path>]`; handler `cmd_sampled_predict` (src/evo_predictor/run.py:544, parser :792) returns/writes `{"manifest_path", "prediction": serialize_final_order_sample_set(result), "breakdown": {...}}`.
- **Lineup:** `beam_search_lineups(futures: list[list[str]], *, scored_slots=10, beam_width=25, risk_percentile=90.0, balanced_risk_weight=0.25, ...) -> FantasyBeamSearchResult` (src/fantasy_scoring/beam_search.py:331); result has `.best_mean/.best_risk/.best_balanced/.best_max`.
- **Report/explainer (v1 explainer source):** `generate_report(*, sampled_runtime_path, year, round_num, output_stem, gp_name=None, lineup_size=10, beam_width=25, risk_percentile=90.0, balanced_risk_weight=0.25) -> dict` + `write_beam_search_report(report, output_stem) -> (json_path, md_path)` (src/fantasy_scoring/artifacts.py:200, :189).
- **Sprint-aware sessions:** `get_practice_session_types(year, gp_name)` (src/utils/constants.py:312).
- **Partial-data poll:** `DatabaseManager.has_session_classification(year, round_num, session_type) -> bool` (src/data/database/_metadata_session.py:506).
- **Per-year DB path:** `Config.db_path_for_year(year) -> data/f1_data_{year}.db` (src/utils/config.py:36).
- **Round resolution:** `get_calendar(year).index(gp_name) + 1` (no dedicated helper).
- **Gold manifest:** `params/gold/sampled_runtime_manifest.json` (default for real predicts).

## Acceptance (build is DONE when)
1. `race-week` emits a **submittable ranked top-10** for a real 2026 race, produced from the per-year DB via the gold manifest, balanced lane, with `03_lineup.json` durable before the explainer runs.
2. **End-to-end proof on real data: run the full pipeline on 2026 R9 Great Britain** (data already present) — produce the top-10 + beam-search markdown. This validates the plumbing on real 2026 data BEFORE Belgium. Paste the emitted top-10 into your report.
3. DB-path threading acceptance check present (predict reads f1_data_2026.db, not the empty merged DB).
4. Sprint-aware: verify R9 (sprint) resolves its session shape via `get_practice_session_types`, not a hard-coded FP set.
5. Resumption works: re-running a stage with unchanged inputs skips; changed inputs rerun.
6. Unit tests for each stage (pure function over checkpoint dict) + the e2e check. Repo evidence bar: logic change is test-led; run `py -m src.utils.simplification_limits` on touched paths.

## Inherited Context
- **Python is `py`, never `python`.** DB is single source of truth for analysis; the ONLY live-FastF1 path is collection.
- **Never commit `.agent-work/LESSONS.md`/`AGENT_FEEDBACK.md`/`CONSTELLATION_FEEDBACK.md`, your work area, or `outputs/` checkpoints on the branch.** PR = scripts/race_week*.py + tests only.
- **Windows PR bodies:** `gh pr create -F <file>`.
- Dispatch implementer/reviewer crews via `run_crew.py` (foreground, durable registry); run `recover_crews.py` before each; no `claude` CLI binary in this harness — use the Agent tool per that path. Crews that background their own long task tend to idle with the result unwritten — mandate poll-to-completion (lesson:crew-idle-strands-deliverable).
- Known-Limits from the design doc still open as YOUR build decisions (resolve + document): partial-FP semantics into predict (does sampled-predict care what landed, or run over whatever's in session_classifications?), single-writer concurrency (document the assumption, don't enforce), exact checkpoint schema field names/versioning, and whether `collect-check` auto-invokes the collector or only reports the gap (recommend: report-only for v1, operator/#603-path does collection).

## Budget
- **Model tier:** Sonnet (commander + crews). This is a meaty compose-over-seams integration; if the seam contract proves materially harder than scoped (e.g. generate_report forces a redesign of the stage split), FLOAT early rather than grinding.
- Compute/time: single-to-few sessions; predictions run in the foreground (not multi-hour) — if any run is long, state-note + detach.

## Stop Conditions
Stop and return when: the command is built, the R9 e2e proof passes, tests green, PR open. Stop earlier and FLOAT if: you need a `src/` change; the gold manifest cannot predict a 2026 race; the seam contract forces a stage-shape change beyond "adjust field boundaries"; or you need context this order doesn't cover.

## Return Shape
Final report (`.agent-work/601-fantasy-league/cmdr-604b-report.md`; post verdict before idle): verdict (DONE/BLOCKED), PR URL, the **emitted R9 top-10** (proof), how you threaded the DB-path, how the stage split maps to the real generate_report/sampled-predict contract (+ any deviation from the design doc's shape and why), resumption evidence, test results + simplification_limits output, `verify_worktree_isolation.py --here` output, triage candidates (incl. the sampled-predict --db-path default bug as a standalone issue), workflow feedback, proposed lessons-delta (do NOT apply — LESSONS.md is at cap; return for Admiral curation). Deliver the artifact before going idle.
