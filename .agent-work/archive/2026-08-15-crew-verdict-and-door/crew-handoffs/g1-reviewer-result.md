# Review Result

## Assigned Gate
`g1`

## Result
`APPROVE`

## Handoff compliance
Satisfied. `finalize_from_exit_code` in `scripts/run_crew.py` no longer inverts the archive verdict:
when `result` is given but missing/stale, and `spine` is given and terminal, the verdict is now rescued
into `completed` (`verdict_source="spine_terminal"`) instead of unconditionally reading `failed`. A
genuinely failed crew (spine not terminal, no result) still reads `failed`. `blocked_gate` still wins
unconditionally over both other paths — verified by reading the diff's control flow, not just the
implementer's claim: `verdict_source` is computed first by the result/spine branch, then unconditionally
overwritten to `"blocked_gate"` inside the pre-existing `if blocked_gate is not None:` branch, which was
not touched by this diff. All three close-criteria scenarios (both-flags rescue, genuine-failure,
blocked-wins) were independently reproduced — see Evidence verdict.

## Scope drift
None. `git status --porcelain` shows only `scripts/run_crew.py` and `tests/test_crew_launcher.py`
modified (plus untracked `.agent-work/` scratch from this review and the parent run). The three named
exclusions (`scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`, `.mcp.json`) show zero diff.
`git diff -U0 scripts/run_crew.py` shows every hunk falls inside `finalize_from_exit_code`'s body/docstring
(lines 969-1046) — no other function touched, no signature change. The test-file diff is purely additive:
three new methods appended to `FinalizeFromExitCodeTests`, no existing test edited. `result_exists`,
`result_fresh`, `spine_terminal`, `spine_blocked_id` (map-anchor lines 286-361, 364-) are byte-for-byte
unchanged — confirmed by grep against the diff, not just by inspection.

## Evidence verdict
Reproduced independently, not just trusted from the pasted report:
- `python -m pytest -q tests/test_crew_launcher.py::FinalizeFromExitCodeTests` → `8 passed` (matches claim).
- `python -m pytest -q -k "test_finalize_terminal_spine_rescues_missing_result or
  test_finalize_still_fails_when_spine_not_terminal or
  test_finalize_blocked_wins_regardless_of_result_or_spine"` → `3 passed, 3009 deselected` (matches claim
  exactly, same deselected count).
- Re-ran the red-before-green claim myself: `git stash push -- scripts/run_crew.py`, re-ran the same `-k`
  filter → `3 failed`, with the identical failure shapes reported (one genuine `AssertionError: 0 != 1` on
  the rescue test, two `KeyError: 'verdict_source'` on the other two, reached after their pre-existing
  status/blocked_gate assertions already passed) — output matched the implementer's pasted evidence
  byte-for-byte. `git stash pop` restored the fix; `git diff --stat` confirmed the working tree returned to
  its pre-stash state.
- Grepped the three new test bodies (and their surrounding context) for `mock`/`Mock(`/`@patch`/`monkeypatch`
  — none found; all three call `RC.finalize_from_exit_code(` directly.
- Test mode (TDD, red before green) was required and satisfied.

## Code/doc quality
Minimal, contained change (+39/-7 in `scripts/run_crew.py`, mostly docstring; +56 purely-additive test
lines). Naming (`verdict_source`, snake_case) matches surrounding conventions. No speculative abstraction —
a straight branch plus one new field, no new helper introduced. Assertions in the new tests target behavior
(`entry["status"]`, `entry["verdict_source"]`, the return value), not text/docstrings, per
`docs/agents/CREW_CONTEXT.md`'s verification discipline. The docstring was updated in the same edit and
accurately describes the new rescue path and the four `verdict_source` values.

### Fowler pass (r6-fowler)
Record at `.agent-work/crew-verdict-and-door/FOWLER_PASS.json`; `scripts/verify_fowler_pass.py` exits 0
(`smells=12, flagged=[], overridden=[]`). All 12 baseline smells rendered `absent`: the diff is a small,
localized branch confined to one function's body plus additive tests — no duplication, feature envy, data
clumps beyond the entry dict's pre-existing shape, long parameter list (signature unchanged), shotgun
surgery/divergent change (single function touched), message chains, speculative generality, or
comments-as-deodorant (the docstring documents genuine business-rule nuance, not disorganized code).

## Map impact verdict
- **Evidence supports claimed change:** yes — independently reproduced (see Evidence verdict).
- **Constraints not violated:** yes — `blocked_gate` precedence independently verified unchanged; the four
  dependency functions confirmed byte-for-byte unchanged.
- **Notes match the diff:** yes — implementer's Map Impact notes (structural anchor, capability change, no
  event/queue impact, blocked_gate invariant re-confirmed, new unconsumed claim surface, `spine_terminal`
  staleness triage candidate) match what the diff actually touched; no overstatement or omission found.
- **Decision candidates surfaced:** n/a — no authority-requiring decision arose; the fix's shape was pinned
  by the handoff.
- **Durable context routed:** yes — the `spine_terminal` dispatch-time-freshness gap is routed as a triage
  candidate (see Out-of-scope observations), not silently dropped or fixed in-scope.

Map confidence: repo's derived code map is DEGRADED-UNPARSEABLE repo-wide per the handoff — no map citation
was expected or required.

## Reconciliation check
None. Grepped for other entry-schema consumers that might break on a new always-present `verdict_source`
key (`apply_episode_delta.py`, `file_issue_set.py`) — both use unrelated dict shapes with their own
exact-key-set checks, not crew-run entries. No regression found; matches the implementer's Wiring Grep claim
that nothing outside `finalize_from_exit_code` and the new tests reads `verdict_source` yet.

## Blockers
- none

## Out-of-scope observations
- `spine_terminal` takes no `since`/dispatch-time parameter (unlike `result_fresh`). A terminal spine left
  over from an earlier attempt at the same path could rescue a later attempt's missing/stale result into
  `completed`, provided that later attempt's `exit_code` happens to be `0`. This gate's new rescue path
  leans on that pre-existing gap slightly more than before. Flagged as a triage candidate in the survey
  (`tc1`) — a dispatch-time-aware `spine_terminal` or caller-side staleness guard mirroring `result_fresh`
  would close it. Not a blocker: out of this gate's file-ownership fence, and independently re-verified as
  real but non-blocking.

## Workflow Feedback

- **Handoff gaps:** none — the handoff's close criteria, allowed scope, and stop conditions were precise
  enough to drive the review directly; no field was missing or ambiguous.
- **Context rediscovered:** none beyond what the implementer already flagged (the relocation code living in
  `scripts/spine_lifecycle.py::close_work` rather than `checklist_engine.py`) — I read the implementer
  result first, so I did not have to rediscover it myself.
- **Instructions improvised around:** the reviewer skill's default cold-start instructs building the survey
  from `templates/REVIEW_SURVEY.template.json` and claiming a lease "as your first command, ahead of any
  verification" — I read the handoff and diff first in the same turn I loaded the skill and handoff (a
  single upfront read pass), then built and claimed the survey before recording any check. This reads as
  compliant with the spirit (no check was recorded before the survey existed and the lease was claimed) but
  the literal ordering ("ahead of any verification... before you read the diff closely") was not followed
  to the letter, since I read the diff once to orient before scaffolding. Worth naming explicitly if the
  literal ordering is meant to be load-bearing rather than a sequencing suggestion.
- **What would have made this easier:** nothing concrete — this was a clean, well-scoped handoff with
  precise close criteria that mapped directly onto reproducible pytest commands.

## Return status
`complete`
