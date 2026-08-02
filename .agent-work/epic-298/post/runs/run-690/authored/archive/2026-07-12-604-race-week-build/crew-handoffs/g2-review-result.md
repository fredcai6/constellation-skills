# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g2-review`

## Result
`APPROVE`

## Handoff compliance
Assigned scope was `scripts/race_week.py` + `tests/unit/scripts/test_race_week_cli.py` only. Read the
g2-implementer-handoff.md Close Criteria item-for-item against the actual code (not the implementer's
prose summary of it): all 5 subcommands present (`collect-check`/`predict`/`optimize`/`explain`/`run`),
global args (`--year`/`--race`/`--output-root`/`--force`) match, predict/run args
(`--manifest`/`--compound-prior-root`/`--db-path`/`--db-root`) match, the DB-path resolution order is
exact, `--lane` is argparse-restricted to 3 choices, round-number resolution mirrors
`src/data/collector.py:232`'s pattern, `collect-check` is report-only with no collector invocation,
`run`'s hard/soft gate ordering holds, and hash-based resumption is implemented for `predict`/`optimize`.
All stop conditions in the reviewer handoff were checked and none were hit.

## Scope drift
None. `git status --porcelain` in the worktree shows only `scripts/race_week.py` and
`tests/unit/scripts/test_race_week_cli.py` as new files belonging to this gate (plus an unrelated `M
data/f1_data_2026.db` and G1's own untracked `race_week_stages.py`/`test_race_week_stages.py`, neither of
which G2 owns). No `src/` file appears in the diff. `scripts/race_week_stages.py` (G1, already approved)
was not modified: its mtime (2:19 PM) predates both G2 files' creation (2:32-2:33 PM), and its own 33-test
suite still passes 33/33 unmodified when re-run standalone in isolation. `collect-check` does not import
or subprocess-call `collect_evo_data` or any collector (grepped source directly; also covered by a
dedicated test).

## Evidence verdict
All required evidence reproduced independently, not accepted from the report:
- `py -m pytest tests/unit/scripts/test_race_week_cli.py -v` → **41 passed** (matches claim exactly).
- `py -m pytest tests/unit/scripts/test_race_week_stages.py tests/unit/scripts/test_race_week_cli.py` →
  **74 passed** (33 G1 + 41 G2, no failures, G1 unaffected).
- `py -m src.utils.simplification_limits --paths scripts/race_week.py
  tests/unit/scripts/test_race_week_cli.py` → **PASS (2 files checked)**.
- Test mode was test-after (sanctioned by the handoff for a new module); the two regression-shaped tests
  required by the handoff exist and their red/green claim was independently reproduced (see below) rather
  than accepted at face value.

## Code/doc quality
Checked against inherited crew doctrine and `docs/agents/CREW_CONTEXT.md`: `DatabaseManager` is
constructed per-call (`_do_collect_check`), not a module-level singleton/cache; no module-level mutable
state; `print()` is confined to the CLI script (the library-logging rule targets `src/`, not `scripts/`);
`resolve_round_num`'s `ValueError` names the field and the calendar it was checked against, matching the
project's validation-exception convention; no hidden fallback anywhere in the db-path resolution (it
fails visibly rather than defaulting silently); the file follows the established `scripts/` sys.path
bootstrap convention cited from `accept_quali_anchor_420.py`. No project-rule violations found.

## Map impact verdict

- **Evidence supports claimed change:** Yes. The implementer's Map Impact claims (struct:scripts anchor,
  new CLI capability, db-path/gate-ordering constraint compliance) are all backed by re-run test output
  and direct code reading, not just asserted.
- **Constraints not violated:** Yes. The db-path/compound-prior/lane constraints inherited from G1 are
  honored — `predict_stage`'s XOR check on `compound_prior_root`/`compound_prior_artifact` is left to
  propagate its own `ValueError` (not swallowed), and the CLI always threads a concrete `db_path` (never
  `None`) into stage calls.
- **Notes match the diff:** Yes. `struct:scripts` is the only anchor genuinely touched; no `src/` claim is
  made or needed since none was touched.
- **Decision candidates surfaced:** The one live decision — `--db-root`'s literal argparse default
  changed from the handoff's stated `"data"` to `None` — was surfaced transparently in the implementer's
  Assumptions and Workflow Feedback sections, not silently made. Independently re-verified below (see
  "Independent re-verification" for the counterfactual computation); the implementer's reasoning holds.
- **Durable context routed:** Yes. No out-of-scope discoveries beyond what was already scoped out
  (`collect-check`'s non-invocation of a real collector, explicitly Known-Limits item 7).

Architecture-significant work here is limited to adding one new CLI entry point; no BLOCK-level
graph-impact gap found.

## Independent re-verification (per the handoff's explicit re-verify list)

- **DB-path resolution (the single most important property of this gate):** Read `resolve_db_path`
  (`scripts/race_week.py:75-93`) directly — order is exactly `db_path` → `db_root`-derived →
  `Config.db_path_for_year(year)`, no other branch. Independently re-checked `src/utils/config.py`
  myself: line 32 is `DATABASE_PATH = PROJECT_ROOT / "data" / "f1_data.db"` (the fixed path); lines 36-38
  are the `db_path_for_year` classmethod returning `PROJECT_ROOT / "data" / f"f1_data_{year}.db"`. Ran
  `resolve_db_path` live for all three branches: the no-override branch equals
  `str(Config.db_path_for_year(2026))` and is **not** equal to `str(Config.DATABASE_PATH)`. No override-free
  path reaches the fixed database.
- **`--lane` choices:** Live CLI run — `py scripts/race_week.py optimize --year 2023 --race Bahrain --lane
  max` → argparse error `invalid choice: 'max' (choose from mean, risk, balanced)`, exit code 2, before any
  stage function is reached.
- **Hard/soft gate ordering:** Read `cmd_run` directly (`race_week.py:227-249`) — four sequential
  statements, no `try/except` anywhere in the function. If `_do_predict` or `_do_optimize` raises, the
  exception propagates immediately and `_do_explain` structurally never executes (a Python control-flow
  guarantee, not a convention). `main()`'s only `try/except` is at the CLI boundary and does not call
  `explain` on failure.
- **Resumption (`--force` vs. hash-mismatch):** Traced the boolean logic
  (`if not args.force and stages.should_skip_stage(...)`) as a truth table — `--force=True` always
  reruns regardless of hash state; `--force=False` with a hash mismatch also reruns, independent of
  `--force`. Genuinely two distinct triggers to the same outcome, not conflated.
- **`--db-root` default `None` judgment call:** Ran the counterfactual myself — if `--db-root` literally
  defaulted to `"data"`, `str(Path("data") / "f1_data_2026.db")` = `"data\f1_data_2026.db"` (relative),
  which is **not** equal to `Config.db_path_for_year(2026)` (an absolute, `PROJECT_ROOT`-based path). A
  literal `"data"` default would make the third resolution branch unreachable and break the acceptance
  test. The implementer's reasoning holds; `default=None` was the correct call, not just a defensible one.
- **The load-bearing regression proof (db-path footgun):** Independently reintroduced the bug —
  changed `resolve_db_path`'s default-branch return from `str(Config.db_path_for_year(year))` to
  `str(Config.DATABASE_PATH)  # DELIBERATE BUG`. Ran
  `py -m pytest tests/unit/scripts/test_race_week_cli.py -k db_path -v` → **RED, 4 failed / 3 passed**,
  the exact same 4 test names the implementer's report claimed
  (`test_resolve_db_path_default_branch_uses_config_db_path_for_year`,
  `test_resolve_db_path_default_branch_is_never_the_fixed_database_path`,
  `test_db_path_threading_acceptance_predict_stage_receives_per_year_default`,
  `test_run_threads_resolved_db_path_and_lane_through_to_stages`). Reverted the exact edit, confirmed no
  leftover `DELIBERATE BUG` marker (grep clean), and re-ran the full suite → **GREEN, 41 passed**. This is
  genuine, independently-reproduced red-green evidence.

## Reconciliation check
No architecture baseline concerns. `scripts/race_week.py` is a purely additive new CLI module under
`struct:scripts`, referencing G1's `race_week_stages.py` and read-only `src/data/database`,
`src/utils/config`, `src/utils/constants` — nothing needing Cartographer reconciliation beyond the
Map Impact notes the implementer already recorded.

## Blockers
- none

## Out-of-scope observations
- none — the one thing that could have been flagged (`collect-check` not invoking a real collector) is
  already correctly scoped out per the handoff and Known-Limits item 7, not a gap this gate should have
  covered.

## Workflow Feedback
Mandatory section. A `none` answer requires a run-specific reason: `none — confirmed after review: <what
you checked>`; a bare `none` is treated as an unfilled field. This is workflow signal, not project
signal: you are the only one who saw this friction — if you do not report it here, it is lost.

- **Handoff gaps:** The reviewer handoff itself was precise and left nothing ambiguous. The one real
  ambiguity lives upstream in the g2-implementer-handoff.md (`--db-root ... default "data"` reads as a
  literal argparse default but contradicts the immediately-following exact resolution order and the
  acceptance test) — the reviewer handoff correctly anticipated this and explicitly told me to
  independently assess it rather than trust the citation, which is exactly the right instruction; I have
  nothing to add beyond confirming the implementer's resolution was correct via direct computation.
- **Context rediscovered:** none beyond what the reviewer handoff already pointed at — the handoff named
  the exact config.py line numbers, the exact file list, and the exact regression scenario to reproduce, so
  no rediscovery was needed.
- **Instructions improvised around:** Encountered a transient/stale directory listing for
  `.agent-work/604-race-week-build/g2-review/` at the very start (an `ls` showed a pre-existing
  `review.json`/`review.json.journal` pair, but a follow-up `ls -la` and `cat` immediately after showed the
  directory empty). Treated this as a listing artifact rather than a real prior-session file (a
  `wc`/`cat` on the same path failed with "No such file or directory" seconds later), and proceeded to
  instantiate the survey fresh from the template — no evidence a concurrent session was mid-flight on the
  same file, and the engine's `claim` verb would have refused a conflicting lease if one existed.
- **What would have made this easier:** none — this handoff named the exact re-verification list, the
  exact regression-reproduction recipe, and the exact stop conditions; nothing to improve for next time.

## Return status
`complete`
