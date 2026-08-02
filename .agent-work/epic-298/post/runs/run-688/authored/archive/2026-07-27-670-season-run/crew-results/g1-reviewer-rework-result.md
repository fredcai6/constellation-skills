# Review Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned Gate
`g1` (rework 1) — season runner per-round fault isolation (#670 season-scale run, attempt-2 independent review)

## Result
`APPROVE`

## Handoff compliance
Confirmed by direct read of `scripts/run_season_670.py` (untracked; inspected directly per the
handoff's own note, not via git diff). `run_season`'s loop (lines 191-236) now wraps
`run_circuit_fn(...)` + `check_round_vocabulary(...)` for the current slate entry in a
`try/except Exception`. On any exception: `rounds[circuit] = {round_idx, status:"parked",
reason: f"round failed at run_circuit: {type(exc).__name__}: {exc}"}` (matches the handoff's
literal example f-string), `circuit` appended to `parked` (→ `parked_rounds` in the returned
dict), then `continue`. The empty-driver-grid park path (lines 192-204) is byte-for-byte
unchanged — separate branch, taken before `run_circuit_fn` is ever called, its own unmodified
reason text. Both new tests in `tests/unit/physics/pilot/test_season_runner.py` exist exactly as
the Close Criteria describe. All required evidence commands independently reproduced (below).
Stop conditions did not trigger — no change to `run_circuit`/E was needed.

## Scope drift
None. `git status --porcelain`: only `M src/physics/pilot/pipeline.py` (tracked) plus untracked
`scripts/run_season_670.py`, `scripts/verify_season_artifacts_670.py` (unchanged by this rework),
`tests/unit/physics/pilot/test_season_runner.py`, and `.agent-work/670-season-run/`.
`git diff -- src/physics/pilot/pipeline.py` shows **only** the pre-existing, already-approved
original-G1 hunk (`budget_s`/`refutil_db` forwarding into `run_stage_e`) — this rework added
nothing to `pipeline.py`. `src/physics/pilot/pipeline.py`'s fault-isolation-adjacent logic,
frozen sets, `run_circuit`, and E are untouched. `docs/architecture/*` untouched (grepped, no
hits). Allowed Scope honored exactly.

## Evidence verdict
Independently re-ran, from the worktree, with the pinned `python.exe`
(`C:/Users/fredc/AppData/Local/Python/pythoncore-3.14-64/python.exe`), never bare `py`:
- `-m pytest tests/unit/physics/pilot/test_season_runner.py -q` → **17 passed in 1.08s**
  (matches claim: 15 pre-existing + 2 new)
- `-m pytest tests/unit/physics/pilot -q` → **46 passed in 10.12s** (matches claim: 44
  pre-existing + 2 new, zero regressions)
- `-m pyright scripts/run_season_670.py tests/unit/physics/pilot/test_season_runner.py` →
  **0 errors, 0 warnings, 0 informations** (matches claim)

The two new tests are behavior-real, not vacuous:
- `test_run_season_parks_round_that_raises_and_continues` — a `flaky_run_circuit` raises
  `ValueError` only for Bahrain (round 1), and genuinely captures/executes for the other two
  circuits into an ordered `captured` list. Asserts `status=="parked"`, `round_idx==1`, and
  **substring** checks (`"ValueError" in reason`, `"no severity classes" in reason`) — real
  exception content, not a hardcoded stub — plus proves the loop kept iterating past the raise
  (`captured == [...]` in order for the two subsequent rounds).
- `test_run_season_run_failure_park_distinguishable_from_empty_grid_park` — one round takes the
  pre-existing empty-grid path, the other genuinely raises `RuntimeError("boom")`; both park, but
  the test asserts on the two **different** reason substrings, which would fail if the two park
  paths were ever accidentally merged.

Neither test hardcodes a full-string equality on the reason (both use substring checks against
the real f-string), so a genuinely non-diagnostic reason would fail these tests.

## Code/doc quality
Minimal, localized change: a single `try/except` added around the existing per-round body, one
indentation level added, no other logic touched. `except Exception` is broad but matches the
handoff's explicit "on ANY exception" instruction, spans the two discovered failure modes
(`ValueError`, and E's own data-shape error), and mirrors the pre-existing `noqa: BLE001` style
already used on `check_round_vocabulary`'s own except in the same file. The per-round try/except
is scoped **inside** the `for` loop body (confirmed by indentation: both `try:` and
`except Exception` sit one level deeper than the `for` statement), not around the whole loop —
`continue` returns control to the `for` to advance to the next slate entry, which would be
unreachable if the except instead wrapped the entire loop. The 3-round synthetic test (round 1
raises, rounds 2-3 succeed and are captured in order) directly proves this.

## Map impact verdict
- **Evidence supports claimed change:** yes — every Map Impact claim (two distinct park paths,
  capability:season-scale-run gains fault isolation, decision:round1-2-genuinely-park implemented
  without inventing synthetic prior-session data) was independently checked against source and
  tests, not accepted on the report's word.
- **Constraints not violated:** yes — offline-only, no-tracked-db-write, frozen-consumed-not-minted
  are all unaffected by this rework (no DB-path or frozen-constant logic touched); the one
  constraint this rework directly targets ("a per-round failure PARKS, never crashes the season")
  is now honored and independently proven by test.
- **Notes match the diff:** yes — the implementer's notes exactly match what changed; no
  overstatement.
- **Decision candidates surfaced:** n/a — no authority beyond this gate's scope was required; the
  round1/2-genuinely-park design was already decided in the handoff itself.
- **Durable context routed:** yes — no new durable-context gap found beyond the two non-blocking
  Fowler observations, flagged as `tc1` in the review survey.

## Reconciliation check
No divergence from recorded architecture requiring Commander reconciliation. This is additive
robustness at the `run_season` loop boundary only, directly satisfying the original G1 handoff's
already-recorded Map Anchor ("a per-round failure PARKS, never crashes the season").

## Fowler pass (r6)
Recorded to `.agent-work/670-season-run/g1-review-rework/fowler_pass.json`;
`verify_fowler_pass.py` exits 0. Verdicts: 10 `absent`, 2 `flagged` (both non-blocking), 0
`overridden` (the pre-existing `speculative-generality` override and the `data-clumps`/
`long-parameter-list` observations from the original g1-review pass are unchanged/unworsened by
this diff and marked `absent` here rather than re-adjudicated).
- **flagged — long-method:** `run_season`'s loop body now handles empty-grid park,
  `run_circuit_fn` invocation, vocabulary-check, success-recording, and run-failure park in one
  ~46-line for-body (~90-line function total). A future `_run_one_round(...)` extraction would
  shrink the loop to slate-iteration only. Non-blocking.
- **flagged — duplicated-code:** the two park-dict literals (`{round_idx, status:"parked",
  reason}`) share shape without a shared constructor. A `_park(round_idx, reason)` helper would
  remove the duplication; the two reason computations differ enough that inlining stays readable.
  Non-blocking.

## Blockers
- none

## Out-of-scope observations
- `long-method` and `duplicated-code` Fowler observations above (non-blocking, future cleanup) —
  flagged as triage candidate `tc1` in `.agent-work/670-season-run/g1-review-rework/review.json`.
- (Carried forward, unaffected by this rework) G2/G3 must still consume
  `vocabulary_divergent`/`vocabulary_guard.flagged_rounds` — already flagged `tc1` in the
  original `g1-review/review.json`.

## Workflow Feedback

- **Handoff gaps:** none blocking. The rework handoff's literal example diagnosis f-string
  (`f"round failed at run_circuit: {type(exc).__name__}: {exc}"`) matched the implementation
  verbatim, which made the r1-handoff check unambiguous.
- **Context rediscovered:** the note "`run_season_670.py` is UNTRACKED (new file) — inspect it
  directly, not via git diff" in the dispatch was essential and correctly pre-empted the natural
  first move (git diff), which would have shown nothing useful for that file. Worth carrying that
  same phrasing into the handoff template itself for any gate touching a not-yet-committed new
  file, rather than relying on the dispatcher to add it ad hoc.
- **Instructions improvised around:** none — the survey/Fowler-pass flow matched this rework's
  shape cleanly (a small bounded diff plus a targeted set of custom checks for the four
  close-criteria bullets).
- **What would have made this easier:** none — the rework handoff and implementer result were
  both precise enough (exact line ranges, exact reason-text example, exact test names) that no
  additional digging was needed beyond reading the two changed files directly.

## Return status
`complete`
