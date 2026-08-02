# Implementer Handoff

## Gate
`g1-implement`

## Task
Build `scripts/race_week_stages.py`: checkpoint I/O helpers, a content-hash resumption primitive,
and four pure stage functions (session discovery, predict, optimize, explain) for the `race-week`
staged pipeline (issue #604, Candidate C design — `docs/design/race_week_seam.md`).

## Protected Intent
The ranked top-10 (`03_lineup.json`) must be producible and durable on disk independent of the
explainer stage ever succeeding — the hard/soft gate split is a design invariant, not a nice-to-have.
Per-year DB routing must never silently fall back to the wrong database.

## Test Mode
Test-after allowed (no pre-existing test surface for this new module) — but every stage function
must be unit-tested as a pure function over fixture checkpoint dicts before the gate closes.

## Close Criteria
- `scripts/race_week_stages.py` exists with: checkpoint read/write helpers; `compute_stage_inputs_hash(upstream_checkpoint: dict) -> str` (sha256 hex over canonical/sorted-key JSON); `should_skip_stage(existing_checkpoint: dict | None, upstream_checkpoint: dict) -> bool`; four stage functions (see below).
- `discover_sessions_stage(year, gp_name, db) -> dict` — calls `get_practice_session_types(year, gp_name)` (src/utils/constants.py:312, the SOLE session-shape source) and `DatabaseManager.has_session_classification(year, round_num, session_type)` (src/data/database/_metadata_session.py:506) per expected practice session, returning a `01_sessions.json`-shaped dict: `{"expected_sessions": [...], "landed": [...], "status": "complete"|"partial"|"missing", ...}`. `round_num` is resolved via `get_calendar(year).index(gp_name) + 1` (src/data/collector.py:232 pattern) — no dedicated helper exists.
- `predict_stage(...)` — constructs a `types.SimpleNamespace` matching `src.evo_predictor.run.cmd_sampled_predict`'s arg contract (verified `run.py:544` + parser `:792-813`): `year`, `race`, `db_path`, `compound_prior_root` (XOR `compound_prior_artifact`), `sampled_runtime_manifest`, `output=None`. Calls `cmd_sampled_predict` directly in-process (no subprocess). `db_path` is ALWAYS a caller-supplied value — this stage function never defaults it itself (that's the CLI's job in G2); it exists so the CLI cannot forget to thread it. Returns the payload dict `{"manifest_path", "prediction", "breakdown"}` and writes/returns the `02_prediction.json` checkpoint shape (payload + `stage_inputs_hash` of the `01_sessions.json` checkpoint it was called with).
- `optimize_stage(...)` — calls `src.fantasy_scoring.artifacts.generate_report(sampled_runtime_path=<the 02 checkpoint's own path>, year=, round_num=, output_stem=<03 checkpoint stem>, ...)`. **VERIFIED at `artifacts.py:200-228`: `generate_report` ALREADY calls `write_beam_search_report` internally and writes both `<stem>.json` and `<stem>.md` itself — do NOT call `write_beam_search_report` a second time, that double-writes.** After the call, read the returned report dict, select the lineup via a `lane` parameter restricted to `{"mean", "risk", "balanced"}` (default `"balanced"`) — **VERIFIED at `beam_search.py:52-63` (dataclass fields) and `:396-421` (construction): `FantasyBeamSearchResult` exposes ONLY `best_mean`/`best_risk`/`best_balanced`. There is no `best_max` — reject any 4th lane choice at the function boundary (raise `ValueError` on an unknown lane), do not silently accept it.** Inject a top-level `lane_used` field into the on-disk `03_lineup.json` (re-read/patch/re-write after `generate_report` returns, or pass `lane` through so it lands in the single write — implementer's choice, but the FINAL on-disk JSON must carry `lane_used`).
- `explain_stage(...)` — copies the `.md` twin `generate_report` already wrote at the 03 stem (e.g. `<stem>.md`) to `04_explainer.md`. On ANY failure (missing 03 markdown, read/write error, exception of any kind) it MUST NOT raise — catch broadly, write `04_explainer.STUB.md` with a short reason, and return a success indicator so callers never treat explainer failure as a pipeline failure.
- All four stage functions unit-tested in `tests/unit/scripts/test_race_week_stages.py` as pure functions over fixture dicts: mock `DatabaseManager`/`cmd_sampled_predict`/`generate_report` — no real DB, FastF1, or model inference in these tests.
- `py -m src.utils.simplification_limits` run on `scripts/race_week_stages.py` — report the output (pass or a documented split plan if over threshold).

## Allowed Scope
- Create: `scripts/race_week_stages.py`, `tests/unit/scripts/test_race_week_stages.py`.
- Read-only reference: `src/evo_predictor/run.py`, `src/fantasy_scoring/artifacts.py`, `src/fantasy_scoring/beam_search.py`, `src/utils/constants.py`, `src/utils/config.py`, `src/data/database/_metadata_session.py`, `src/data/collector.py` (for the round-number pattern).

## Specific Exclusions
- No `scripts/race_week.py` (that's G2 — do not create it, even a stub, in this gate).
- No `src/` changes of any kind (issue #604's fence is `scripts/`+`tests/` only; the `sampled-predict --db-path` default-fallback bug is a separate, out-of-scope, already-filed triage candidate — do not "fix" it here).
- Do not call `write_beam_search_report` directly — `generate_report` already does it (see Close Criteria).

## Constraints
- `SimpleNamespace` fields for `cmd_sampled_predict`: `year: int`, `race: str`, `db_path: str | None`, `compound_prior_root: str | None`, `compound_prior_artifact: str | None`, `sampled_runtime_manifest: str`, `output: str | None`. Exactly one of `compound_prior_root`/`compound_prior_artifact` must be set (mirrors `_compound_normalizer_for_sampled_predict`'s own XOR check, `run.py:520-538`) — if the caller supplies neither, let `cmd_sampled_predict` raise its own `ValueError` naturally (do not swallow it).
- `generate_report` signature (verified `artifacts.py:200-211`): `generate_report(*, sampled_runtime_path: Path, year: int, round_num: int, output_stem: Path, source_side: str | None = None, gp_name: str | None = None, lineup_size: int = 10, beam_width: int = 25, risk_percentile: float = 90.0, balanced_risk_weight: float = 0.25) -> dict`.
- Checkpoint dir convention: `outputs/race_week/<year>/<round>/{01_sessions,02_prediction,03_lineup}.json`, `04_explainer.md` / `04_explainer.STUB.md`. This gate does not need to create the directory tree itself beyond what its own file-write calls require (`mkdir(parents=True, exist_ok=True)` on write is fine).

## Map Anchors (inbound)
- **Structural:** `struct:scripts` — script-level, not a Cartographer map node; `struct:fantasy_scoring` (artifacts.py, beam_search.py — consumed unmodified); `struct:evo_predictor` (run.py:cmd_sampled_predict — consumed unmodified).
- **Capability:** session-shape discovery, partial-data poll, beam-search report generation.
- **Constraints/assumptions:** DB-only analysis; per-year db-path threading correctness; compound-prior-root is REQUIRED not optional.
- **Decision anchors:** Candidate C staged-checkpoint shape (frozen, Wave 1, PR #612); `--lane` restricted to 3 real choices (resolved decision pressure, MISSION_FRAME.md).
- **Evidence expectations:** `FantasyBeamSearchResult` has no `best_max` (re-verify yourself at the cited line numbers — don't take this handoff's word for it).

## Deliverable Path Check
- **Committed** — `scripts/race_week_stages.py`; `git check-ignore scripts/race_week_stages.py` exit 1 (verified by commander before dispatch).
- **Committed** — `tests/unit/scripts/test_race_week_stages.py`; `git check-ignore tests/unit/scripts/test_race_week_stages.py` exit 1 (verified by commander before dispatch).

## Required Evidence
- Full pytest output for the new test file (not a summary/glance).
- `py -m src.utils.simplification_limits` output for the touched file.
- A short note confirming: (a) no `write_beam_search_report` double-call, (b) `explain_stage` never raises, (c) an unknown `lane` value raises `ValueError` at the `optimize_stage` boundary (with a quick manual/test check pasted).

## Verification Commands
```bash
cd C:/Programs/f1Brainz/.claude/worktrees/604-build
py -m pytest tests/unit/scripts/test_race_week_stages.py -q
py -m src.utils.simplification_limits scripts/race_week_stages.py
```

## Suggested Model Tier
Sonnet — bounded compose-over-existing-seams task, moderate ambiguity in checkpoint schema shape (resolved by this handoff), low architectural risk (scripts/-level, no src/ changes).

## Authority
The stage-shape (4 stages, checkpoint files, hash-based resumption), the `--lane` 3-choice
restriction, and the `generate_report`-writes-both-files fact are already decided (cited above from
source) — do not relitigate them. Checkpoint field naming beyond what's specified above (e.g. extra
diagnostic fields) is the implementer's call.

## Stop Conditions
Stop and return if: a cited seam signature does not match what you find in source (say which one
and what you found instead); `generate_report` or `cmd_sampled_predict` behaves in a way that makes
the stage split described above impossible; you believe a `src/` change is genuinely required.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced
(full pytest output + simplification_limits output), assumptions used, stop conditions hit,
out-of-scope observations, workflow feedback.
