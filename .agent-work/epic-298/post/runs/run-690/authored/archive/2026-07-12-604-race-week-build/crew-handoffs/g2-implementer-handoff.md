# Implementer Handoff

## Gate
`g2-implement`

## Task
Build `scripts/race_week.py`: a thin CLI dispatcher over G1's `scripts/race_week_stages.py`, giving
the `race-week` pipeline its subcommands (`collect-check`, `predict`, `optimize`, `explain`, `run`).

## Protected Intent
Per-year DB routing must never silently fall back to the fixed `data/f1_data.db`. The hard gate
(top-10) must never be blocked by the explainer. The `--lane` flag must reject any value outside the
3 real lanes.

## Test Mode
Test-after allowed (new module, no pre-existing test surface) — but the CLI-level behaviors named in
Close Criteria must all be covered by `tests/unit/scripts/test_race_week_cli.py` before this gate
closes, including the two regression-shaped tests below (they exist because a cold plan critic
flagged their absence as a real gap before any code was written — don't let them slip).

## Close Criteria
- `scripts/race_week.py` exists with subcommands `collect-check`, `predict`, `optimize`, `explain`,
  and `run` (chains all four).
- Global args: `--year` (int, required), `--race` (GP name, required), `--output-root` (default
  `outputs/race_week`), `--force` (bypass hash-skip on all stages it runs).
- `predict`/`run` args: `--manifest` (default `params/gold/sampled_runtime_manifest.json` — the
  promoted GOLD manifest; overridable for testing), `--compound-prior-root` (default
  `params/gold/compound_prior`), `--db-path` (explicit override) / `--db-root` (directory containing
  `f1_data_{year}.db`, default `"data"`). **DB-path resolution order, exact:** `--db-path` if given,
  else `<db-root>/f1_data_{year}.db`, else `Config.db_path_for_year(year)` as the safe default when
  neither is given. **NEVER fall through to `Config.DATABASE_PATH` (the fixed `data/f1_data.db`)** —
  this is the single most important correctness property of this gate (verified footgun:
  `src/data/database/_core.py:125`, `DatabaseCoreMixin.__init__` defaults to `Config.DATABASE_PATH`
  when `db_path=None` — the CLI must never let that path be reached with `None`).
- `optimize`/`run` args: `--lane {mean,risk,balanced}` default `balanced` — exactly 3 choices at the
  argparse level (`choices=("mean","risk","balanced")`), so an invalid value is rejected by argparse
  itself before any stage code runs. (`race_week_stages.optimize_stage` also validates and raises
  `ValueError` for defense in depth — both layers should exist, argparse first.)
- Round-number resolution: `get_calendar(year).index(gp_name) + 1` (src/data/collector.py:232
  pattern) — surface a clear error if `gp_name` is not in the calendar (see the invalid-`--race`
  test below).
- `collect-check` is report-only in v1: calls `race_week_stages.discover_sessions_stage`, writes
  `01_sessions.json`, prints a human-readable summary of expected vs. landed sessions. It does NOT
  invoke `scripts/collect_evo_data.py` or any collector — that's explicitly out of scope this wave
  (Known-Limits item 7 in the design doc; the launch order's own recommended lean).
- `run` aborts loudly (nonzero exit) if `predict` or `optimize` fails, and in that case `explain` is
  NEVER invoked and no `04_explainer.*` file is written or touched — the hard gate must never be
  silently bypassed by an eager explain call. `explain` itself always exits 0 (writes the STUB file
  on failure, per G1's `explain_stage` contract).
- Resumption: each subcommand loads its upstream checkpoint(s) via G1's `should_skip_stage`, and
  skips (prints `skipped: unchanged`) unless `--force` is passed or the upstream's content actually
  changed (hash mismatch) — `--force` and hash-mismatch are two DIFFERENT paths to a rerun; do not
  conflate them in the implementation OR in the tests.
- Automated DB-path threading acceptance test: assert the resolved `db_path` passed into
  `race_week_stages.predict_stage` equals `str(Config.db_path_for_year(year))` when neither
  `--db-path` nor `--db-root` is given — and is NOT `str(Config.DATABASE_PATH)`.
- Automated hard/soft gate ordering test (failure-injection): mock `predict_stage` (or
  `optimize_stage`) to raise, invoke the `run` command path, and assert (a) the process/function
  exits nonzero / raises out to the caller, (b) `explain_stage` is never called (mock it too and
  assert `call_count == 0`), (c) no `04_explainer.*` file appears on disk.
- Automated invalid-`--race` test: an unknown GP name propagates a clear `ValueError` from
  `get_calendar(year).index(gp_name)` (or an equivalently clear error you raise wrapping it) — not
  swallowed, not a silent no-op.
- `tests/unit/scripts/test_race_week_cli.py` covers: argument parsing/defaults, db-path resolution
  order (all three branches), lane validation (argparse-level rejection), resumption skip/rerun
  decisions (both `--force` and hash-mismatch paths, tested separately), the failure-injection test,
  the invalid-race test. No real DB/FastF1/prediction calls in unit tests — mock
  `race_week_stages`'s stage functions.
- `py -m src.utils.simplification_limits --paths scripts/race_week.py` passes.

## Allowed Scope
- Create: `scripts/race_week.py`, `tests/unit/scripts/test_race_week_cli.py`.
- Read/import: `scripts/race_week_stages.py` (G1, already built+reviewed — do not modify it).
- Read-only reference: `src/utils/config.py` (`Config.db_path_for_year`, `Config.DATABASE_PATH`),
  `src/utils/constants.py` (`get_calendar`), `src/data/collector.py` (round-number pattern).

## Specific Exclusions
- Do not modify `scripts/race_week_stages.py` (G1's file — already reviewed and closed).
- No `src/` changes of any kind.
- No actual collector invocation from `collect-check`.

## Constraints
- `Config.db_path_for_year(year) -> Path` returns `data/f1_data_{year}.db` (`src/utils/config.py:36`).
- `Config.DATABASE_PATH` is the fixed `data/f1_data.db` (`src/utils/config.py:32`) — the value this
  gate exists specifically to never silently reach.
- `get_calendar(year) -> List[str]` raises `KeyError` for an unknown year (`src/utils/constants.py`)
  — a separate failure mode from an unknown `gp_name` within a known year (that's a `ValueError` from
  `list.index`); don't conflate the two in your error handling, but both should surface clearly.

## Map Anchors (inbound)
- **Structural:** `struct:scripts` — `scripts/race_week.py`.
- **Capability:** CLI orchestration over G1's stage library.
- **Constraints/assumptions:** db-path threading correctness (never silently fall to
  `Config.DATABASE_PATH`); hard/soft gate by construction (03 durable before 04 attempted).
- **Decision anchors:** balanced lane default, swappable, 3 real choices.
- **Evidence expectations:** `claim: db_path_for_year(2026)` resolves round 8/9 data only in the
  MAIN-CHECKOUT DB (`C:/Programs/f1Brainz/data/f1_data_2026.db`), not the worktree's stale copy — the
  G3 e2e gate (not this one) will use the absolute main-checkout path explicitly via `--db-path`;
  this gate's job is just to make sure that override plumbs through correctly, and that the
  *default* (no override) resolves to `Config.db_path_for_year(year)`, which is the correct
  general-purpose behavior even though it won't literally be exercised as the default in G3's e2e
  run (G3 passes `--db-path` explicitly to point at the main checkout).

## Deliverable Path Check
- **Committed** — `scripts/race_week.py`; verify `git check-ignore scripts/race_week.py` exits 1
  before you finish.
- **Committed** — `tests/unit/scripts/test_race_week_cli.py`; verify `git check-ignore
  tests/unit/scripts/test_race_week_cli.py` exits 1 before you finish.

## Required Evidence
Full pytest output for `tests/unit/scripts/test_race_week_cli.py` (not summarized).
`py -m src.utils.simplification_limits --paths scripts/race_week.py` output. A short note
demonstrating the db-path resolution order test and the failure-injection test actually assert what
they claim (paste the relevant test bodies or their pass output with clear labeling).

## G1's Actual Signatures (verified by reading scripts/race_week_stages.py directly, post-rework — cite these, not a paraphrase)
```python
def read_checkpoint(path: Path | str) -> dict[str, Any] | None
def write_checkpoint(path: Path | str, payload: dict[str, Any]) -> Path
def compute_stage_inputs_hash(upstream_checkpoint: dict[str, Any]) -> str
def should_skip_stage(existing_checkpoint: dict[str, Any] | None, upstream_checkpoint: dict[str, Any]) -> bool
VALID_LANES: tuple[str, ...] = ("mean", "risk", "balanced")

def discover_sessions_stage(year: int, gp_name: str, db: DatabaseManager, *, checkpoint_path: Path | str | None = None) -> dict[str, Any]
    # returns {"year","gp_name","round_num","expected_sessions","landed","status"}; writes if checkpoint_path given

def predict_stage(sessions_checkpoint: dict[str, Any], *, year: int, race: str, db_path: str,
                   sampled_runtime_manifest: str, compound_prior_root: str | None = None,
                   compound_prior_artifact: str | None = None, checkpoint_path: Path | str | None = None) -> dict[str, Any]
    # db_path is REQUIRED (str) -- you resolve it in the CLI per the resolution order above and pass it in

def optimize_stage(prediction_checkpoint_path: Path | str, *, year: int, round_num: int, output_stem: Path | str,
                    lane: str = "balanced", gp_name: str | None = None, source_side: str | None = None,
                    lineup_size: int = 10, beam_width: int = 25, risk_percentile: float = 90.0,
                    balanced_risk_weight: float = 0.25) -> dict[str, Any]
    # raises ValueError immediately if lane not in VALID_LANES; always writes output_stem.with_suffix(".json")
    # itself (with lane_used patched in) -- you don't need to write it again

def explain_stage(lineup_output_stem: Path | str, explainer_path: Path | str) -> dict[str, Any]
    # never raises; returns {"status": "ok"|"stub", "path": ..., "reason"?: ...}
```
Note `optimize_stage` takes `prediction_checkpoint_path` (a PATH, not the loaded dict) — it reads
the checkpoint itself via `read_checkpoint` internally for the hash, and passes the path straight to
`generate_report`'s `sampled_runtime_path`. `predict_stage` takes the loaded `sessions_checkpoint`
DICT (not a path) as its first arg, purely to hash it — it does not read anything from it otherwise.
Do not conflate the two calling conventions.

## Verification Commands
```bash
cd C:/Programs/f1Brainz/.claude/worktrees/604-build
py -m pytest tests/unit/scripts/test_race_week_cli.py -q
py -m pytest tests/unit/scripts/test_race_week_stages.py tests/unit/scripts/test_race_week_cli.py -q
py -m src.utils.simplification_limits --paths scripts/race_week.py
```

## Suggested Model Tier
Sonnet — bounded CLI-composition task over an already-built, already-reviewed library.

## Authority
G1's stage function signatures and checkpoint schema are frozen (already built + reviewed) — call
them as they exist, do not redesign them. The DB-path resolution order and the 3-lane restriction
are already decided (cited above from source).

## Stop Conditions
Stop and return if: a G1 stage function's actual signature doesn't match what this handoff assumes
(re-read `scripts/race_week_stages.py` directly, it's the ground truth, not this handoff's
paraphrase); you believe a `src/` change is genuinely required; `get_calendar`/`Config` behave
differently than described here.

## Return Format
Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced
(full pytest output + simplification_limits output), assumptions used, stop conditions hit,
out-of-scope observations, workflow feedback.
