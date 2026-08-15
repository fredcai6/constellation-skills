# Reviewer Handoff

## Gate
`g1`

## Survey State Location
Create your review survey checklist at
`.agent-work/crew-verdict-and-door/g1-review/review.json`.

## What Was Implemented
`finalize_from_exit_code` in `scripts/run_crew.py` (~lines 954-1046) no longer inverts the archive verdict.
When a dispatch is given both `--spine` and `--result`, and the result artifact is missing/stale, the
verdict now falls back to `spine_terminal`: a terminal spine rescues it into `completed`; a non-terminal
spine (or none) leaves it `failed`, unchanged. `blocked_gate` is still checked first and unconditionally
wins. A new field `entry["verdict_source"]` records which of `"blocked_gate"` | `"result"` |
`"spine_terminal"` | `"none"` decided the verdict. Three new tests were added to
`tests/test_crew_launcher.py::FinalizeFromExitCodeTests`.

## How to Inspect the Diff
UNCOMMITTED working tree in this worktree:
`/home/tommy/projects/constellation-skills/.worktrees/crew-verdict-and-door` (branch
`fix/crew-verdict-and-door`). Inspect with:
```bash
git status --porcelain
git diff scripts/run_crew.py
git diff tests/test_crew_launcher.py
```
Do not use `git diff main...HEAD` — that would show unrelated prior commits, not this gate's change.

## Task Statement
Fix the structural bug where every successful `archive` reports `failed`: `run_crew.py` judges completion
by the `--result` artifact whenever one is given, but the `archive` gate always relocates the whole work
area (including the result document) as part of a successful close. When `result` is missing/stale AND a
bound `spine` is terminal, the crew must read `completed`. A genuinely failed crew (spine not terminal, no
result) must still read `failed`. `blocked_gate` must keep winning over both other paths, unchanged.

## Close Criteria
- Both-flags case: `result` given+missing/stale, `spine` given+terminal → `status="completed"`, `final=0`,
  `verdict_source="spine_terminal"`.
- Genuine-failure case: `result` given+missing, `spine` given+NOT terminal → `status="failed"`, unchanged.
- Blocked-wins case: `blocked_gate` set → `status="blocked"`, `verdict_source="blocked_gate"`, regardless of
  a fresh result or terminal spine also being present.
- The three named tests (`test_finalize_terminal_spine_rescues_missing_result`,
  `test_finalize_still_fails_when_spine_not_terminal`,
  `test_finalize_blocked_wins_regardless_of_result_or_spine`) exist, pass, and call
  `finalize_from_exit_code(` directly — no mock/monkeypatch of that function.
- Full `FinalizeFromExitCodeTests` class (8 tests total: 5 pre-existing + 3 new) passes with no regressions.
- `result_exists`, `result_fresh`, `spine_terminal`, `spine_blocked_id` are byte-for-byte unchanged.

## Allowed Scope
`scripts/run_crew.py` (`finalize_from_exit_code` function body + docstring only) and
`tests/test_crew_launcher.py` (new test methods in `FinalizeFromExitCodeTests`; other test-file edits only
if an existing test's scenario is directly invalidated — check whether any were, and whether that was
named).

## Specific Exclusions
- `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`, `.mcp.json` — must be untouched (verify via
  `git status --porcelain` showing only the two allowed files).
- `.worktrees/epic-568-441/`, `.worktrees/tc1-worktree-identity/` — outside this worktree, Commander-verified
  not reviewer-verified; do not BLOCK on inability to inspect them.

## Constraints the Implementation Must Respect
- `blocked_gate` decided first, ahead of both other paths, unchanged (independently verify by reading the
  diff's control flow, not just trusting the claim).
- Must not make a genuinely failed crew read as completed — re-run
  `test_finalize_still_fails_when_spine_not_terminal` yourself and confirm it asserts `status == "failed"`.
- The three new test functions must call `finalize_from_exit_code(` directly (grep the test file yourself
  for `mock` / `Mock` / `patch` near those three test bodies — confirm none wrap that function).

## Map Anchors (inbound)
- **Structural:** `scripts/run_crew.py:954-1046` (changed), `scripts/run_crew.py:286-361` (dependencies,
  must be unchanged — diff them explicitly), `scripts/run_crew.py:364-` (`spine_blocked_id`, must be
  unchanged).
- **Map confidence flags:** repo's derived code map is DEGRADED-UNPARSEABLE repo-wide (not specific to this
  gate) — do not expect or require map citations from the implementer.

## Evidence Produced
From `IMPLEMENTER_RESULT` at
`.agent-work/crew-verdict-and-door/crew-handoffs/g1-implementer-result.md` (read it in full): red-before-green
pytest output for the three named tests (3 failed pre-fix — 1 genuine logic failure, 2 via `KeyError` on the
brand-new `verdict_source` field not yet existing — then 3 passed post-fix), full `FinalizeFromExitCodeTests`
class 8/8 post-fix, `git check-ignore` exit 1 for both files, a wiring grep for `verdict_source`, and answers
to the two open questions (relocation code lives in `scripts/spine_lifecycle.py::close_work`, not
`checklist_engine.py`; a `failed` verdict while the spine is terminal remains possible and intentional
whenever `exit_code != 0`). Re-run the pytest commands yourself rather than trusting the pasted output
verbatim — this gate's own `g1-integrate.c3` postcondition re-runs the same `-k` filter mechanically.

## Suggested Model Tier
simple bounded — a contained, well-tested diff to one function.

## Stop Conditions
BLOCK if: the diff touches anything outside the allowed scope; the three pinned test names/assertions don't
match what was actually required; `blocked_gate` precedence was weakened; a genuinely-failed scenario now
reads `completed`; the red-before-green claim doesn't reproduce when you re-run it yourself.

## Return Format
Return REVIEW_RESULT (verdict APPROVE or BLOCK, per-check findings, blockers, out-of-scope observations,
workflow feedback) to `.agent-work/crew-verdict-and-door/crew-handoffs/g1-reviewer-result.md` before ending
your turn.
