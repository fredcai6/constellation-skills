# Reviewer Handoff

## Gate
`g2-review`

## Survey State Location
`.agent-work/604-race-week-build/g2-review/review.json`

## What Was Implemented
`scripts/race_week.py` — a thin CLI dispatcher over G1's `scripts/race_week_stages.py`, with
`collect-check`/`predict`/`optimize`/`explain`/`run` subcommands. Plus
`tests/unit/scripts/test_race_week_cli.py` (41 tests). Full task in
`.agent-work/604-race-week-build/crew-handoffs/g2-implementer-handoff.md`.

## How to Inspect the Diff
Worktree `C:/Programs/f1Brainz/.claude/worktrees/604-build`, branch `feat/604-race-week-build`.
UNCOMMITTED working tree — `git status --porcelain` then read the new files directly (both are
untracked additions, `git diff` alone shows nothing useful for them).

## Task Statement
Build the CLI that gives the `race-week` pipeline its actual command-line surface, correctly
threading the per-year DB path (never silently falling back to the fixed DB), restricting `--lane`
to the 3 real lanes, enforcing hard-gate-before-soft-gate ordering in `run`, and supporting
hash-based resumption for `predict`/`optimize`.

## Close Criteria
- **DB-path threading, the single most important property of this gate:** trace `resolve_db_path`
  (or whatever it's actually named — read the file) yourself. Confirm the resolution order is
  exactly `--db-path` > `--db-root`-derived > `Config.db_path_for_year(year)`, and that there is NO
  code path reachable with no override that resolves to `Config.DATABASE_PATH` (the fixed
  `data/f1_data.db`). Re-verify `Config.DATABASE_PATH` vs `Config.db_path_for_year` yourself at
  `src/utils/config.py:32,36` — don't take the implementer's citation on faith.
- **`--lane`** has exactly 3 choices at the argparse level (`mean`, `risk`, `balanced`) — confirm
  `choices=` is set to something that actually rejects a 4th value (e.g. `max`) BEFORE any stage
  function runs.
- **Hard/soft gate ordering in `run`:** confirm by reading the code (not just trusting test names)
  that a `predict`/`optimize` failure structurally cannot reach the `explain` call — no broad
  `try/except` around the whole chain that could swallow a failure and continue to `explain`.
- **Resumption:** `--force` and a real upstream-content hash mismatch are two DISTINCT code paths to
  a rerun — confirm the implementation doesn't conflate them (e.g. `--force` shouldn't be required to
  trigger a hash-mismatch rerun, and vice versa).
- The implementer's result documents one judgment call worth independently assessing: `--db-root`'s
  literal argparse default was changed from the handoff's stated `"data"` to `None`, because a
  literal `"data"` default would make the third resolution branch (`Config.db_path_for_year`)
  unreachable and would break the acceptance test. Read the actual code and confirm this reasoning
  holds — is it correct that a literal `"data"` default would break the stated acceptance property?
  If you disagree, say so as a specific, reproducible finding, not a vague preference.
- `tests/unit/scripts/test_race_week_cli.py` passes; re-run it yourself. Also re-run the COMBINED
  suite (`test_race_week_stages.py` + `test_race_week_cli.py`) to confirm G1 wasn't touched/broken.
- The implementer's result claims a genuine red-green regression proof for the two protected-intent
  bugs (temporarily reintroducing each, observing the exact tests fail, then reverting). Independently
  reproduce AT LEAST the db-path footgun reintroduction yourself (temporarily change the resolution
  function's default branch to return `Config.DATABASE_PATH`, confirm the acceptance test fails,
  revert, confirm it passes again) — this is the load-bearing regression test in the whole gate.
- `py -m src.utils.simplification_limits --paths scripts/race_week.py
  tests/unit/scripts/test_race_week_cli.py` passes.

## Allowed Scope
Implementer was scoped to: create `scripts/race_week.py` and
`tests/unit/scripts/test_race_week_cli.py` only; read-only reference to G1's
`scripts/race_week_stages.py` plus `src/utils/config.py`, `src/utils/constants.py`,
`src/data/collector.py`.

## Specific Exclusions
No modification to `scripts/race_week_stages.py` (G1's file — flag as BLOCK if changed). No `src/`
changes (flag as BLOCK if any `src/` file appears in the diff). No real collector invocation from
`collect-check` (flag as BLOCK if `collect_evo_data` is imported/subprocess-called).

## Constraints the Implementation Must Respect
Same DB-path/compound-prior/lane constraints as G1 (unaffected by this gate but the CLI must not
undermine them by, e.g., letting a caller pass `compound_prior_root=None,
compound_prior_artifact=None` through to `predict_stage` silently).

## Map Anchors (inbound)
Inherits `g2-implement`'s anchors block in `execute.json` verbatim.

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/604-race-week-build/crew-handoffs/g2-implementer-result.md`:
41/41 new tests pass, 74/74 combined, genuine red-green regression proof for both protected-intent
bugs, `simplification_limits` PASS. Target postcondition: `g2-integrate.c1` (combined test command)
and `g2-integrate.c2` (this REVIEW_RESULT, APPROVE-matched).

## Suggested Model Tier
Sonnet — bounded review of one new CLI module against a detailed, seam-cited handoff, with one
specific judgment call to independently assess.

## Stop Conditions
Return BLOCK if: the diff cannot be accessed, `src/` was touched, `scripts/race_week_stages.py` was
modified, the DB-path resolution has any path reaching `Config.DATABASE_PATH` without an explicit
override, `--lane` accepts a 4th value, `run` can reach `explain` after a predict/optimize failure,
or the tests do not actually pass when you re-run them.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.
