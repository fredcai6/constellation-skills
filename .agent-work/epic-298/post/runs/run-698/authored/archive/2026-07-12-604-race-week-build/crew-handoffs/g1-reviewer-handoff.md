# Reviewer Handoff

## Gate
`g1-review`

## Survey State Location
`.agent-work/604-race-week-build/g1-review/review.json`

## What Was Implemented
`scripts/race_week_stages.py` — checkpoint I/O helpers, `compute_stage_inputs_hash`,
`should_skip_stage`, and four pure stage functions (`discover_sessions_stage`, `predict_stage`,
`optimize_stage`, `explain_stage`) for the `race-week` staged pipeline (issue #604, Candidate C).
Plus `tests/unit/scripts/test_race_week_stages.py` (31 tests).

## How to Inspect the Diff
Worktree `C:/Programs/f1Brainz/.claude/worktrees/604-build`, branch `feat/604-race-week-build`.
Review the UNCOMMITTED working tree (this gate has not committed yet): `git status --porcelain`
then `git diff` (not `--name-only`, which hides untracked new files — both new files here are
currently untracked additions, so `git status --porcelain` is how you'll actually see them; `git
diff` alone shows nothing for brand-new untracked files, use `git diff --no-index /dev/null <path>`
or just `Read` the files directly).

## Task Statement
Build the checkpoint I/O + stage-function library that the future `scripts/race_week.py` CLI (G2,
not yet built) will drive. Full original task in
`.agent-work/604-race-week-build/crew-handoffs/g1-implementer-handoff.md` — read it in full.

## Close Criteria
- Four stage functions exist, each callable as a pure function over already-loaded dicts/params (no
  hidden global state, no implicit path resolution beyond what the handoff sanctioned).
- `predict_stage` never defaults `db_path` itself — it must be a caller-supplied value threaded
  straight into the `cmd_sampled_predict` call (verify by reading the function body, not just the
  test name).
- `optimize_stage` calls `generate_report` exactly once and never imports/calls
  `write_beam_search_report` directly (re-verify: `generate_report` at
  `src/fantasy_scoring/artifacts.py:200-228` already writes both `.json`/`.md` itself — a second
  write call would be a real bug, not a style nit).
- `optimize_stage`'s `lane` parameter rejects anything outside `{"mean", "risk", "balanced"}` with a
  `ValueError` raised BEFORE `generate_report` is invoked (re-verify `FantasyBeamSearchResult` truly
  has no `best_max` at `src/fantasy_scoring/beam_search.py:52-63` — don't take the implementer's
  citation on faith, read the dataclass yourself).
- `explain_stage` cannot raise under any input, including an exception thrown mid-copy — trace the
  exception-handling path yourself, don't just trust the test names.
- `tests/unit/scripts/test_race_week_stages.py` passes; re-run it yourself, don't just read the
  pasted output.
- `py -m src.utils.simplification_limits --paths scripts/race_week_stages.py` passes.

## Allowed Scope
Implementer was scoped to: create `scripts/race_week_stages.py` and
`tests/unit/scripts/test_race_week_stages.py` only; read-only reference to `src/evo_predictor/run.py`,
`src/fantasy_scoring/artifacts.py`, `src/fantasy_scoring/beam_search.py`, `src/utils/constants.py`,
`src/utils/config.py`, `src/data/database/_metadata_session.py`, `src/data/collector.py`.

## Specific Exclusions
No `scripts/race_week.py` (that's G2 — flag as a BLOCK if present, even as a stub). No `src/`
changes of any kind (flag as a BLOCK if any `src/` file appears in the diff). No direct
`write_beam_search_report` call from `race_week_stages.py`.

## Constraints the Implementation Must Respect
- `SimpleNamespace` fields for `cmd_sampled_predict` must match its real argparse contract
  (`run.py:792-814`): `year`, `race`, `db_path`, `compound_prior_root`/`compound_prior_artifact`,
  `sampled_runtime_manifest`, `output`.
- Exactly one of `compound_prior_root`/`compound_prior_artifact` — if the caller supplies neither,
  the underlying `ValueError` from `_compound_normalizer_for_sampled_predict` must propagate
  unswallowed (not caught-and-hidden by `predict_stage`).
- No `src/` changes; DB-only analysis discipline (no live FastF1 calls in this module).

## Map Anchors (inbound)
Inherits `g1-implement`'s anchors block in `execute.json` verbatim — structural (`struct:scripts`,
`struct:fantasy_scoring`, `struct:evo_predictor`), capability (session discovery, partial-data
poll, report generation), constraint (DB-only, per-year db-path threading, compound-prior-root
required), decision (Candidate C shape, 3-lane restriction), evidence (`FantasyBeamSearchResult` has
no `best_max`).

## Evidence Produced
IMPLEMENTER_RESULT at `.agent-work/604-race-week-build/crew-handoffs/g1-implementer-result.md`:
31/31 tests pass (full output pasted in the result), `simplification_limits` PASS, three
required-note checks (no double-write, explain never raises, unknown-lane ValueError)
demonstrated both by test and by a pasted live REPL check. Target postcondition:
`g1-integrate.c1` (test command) and `g1-integrate.c2` (this REVIEW_RESULT, APPROVE-matched).

## Suggested Model Tier
Sonnet — bounded review of a single new library module against a detailed, seam-cited handoff.

## Stop Conditions
Return BLOCK if: the diff cannot be accessed, any cited seam signature does not actually match
source when you re-check it, `src/` was touched, `scripts/race_week.py` exists, or the 31 tests do
not actually pass when you re-run them.

## Return Format
Return REVIEW_RESULT: verdict (APPROVE or BLOCK), per-check findings, blockers, out-of-scope
observations, workflow feedback.
