# Implementation Result

Status values follow `skills/workbench/references/status-model.md`.

## Assigned gate
`m3-verify` — full suite, PR(s), and result artifact (epic #418 wave 3, dispatch w3c-488-489, issues #488 + #489)

## Completed slice
Both fixes landed as one commit, one PR, per `decision:one-pr-or-two-is-yours`:

- **#488**: `resolve_gauge_path` (`scripts/hooks/gauge_writer_hook.py`) now dedups gauge-path
  candidates by distinct `Path` (order-preserving, first-seen wins) before returning them, so
  the caller's ambiguous-binding skip counts distinct gauge paths, not binding count.
- **#489**: `tests/test_verify_spec_confirmed.py`'s live-spec fixture no longer silently takes
  `matches[0]` from a glob. Extracted `_resolve_revised_spec_matches(agent_work_root)`, which
  raises `AssertionError` naming every match on 2+, and returns the list unchanged on 0 or 1
  (preserving the existing `skipTest`-on-zero behaviour).

This session (`impl-w3c-488-489-b`) is a continuation after the prior session tripped the
context governor at `m3-verify`. Both fixes and their targeted tests were already implemented
and verified by the predecessor; this session's own work was: run the full suite with a
captured real exit code, commit, push, open the PR, and write this artifact.

## Scope
**Files changed:**
- `scripts/hooks/gauge_writer_hook.py`
- `tests/test_gauge_writer.py`
- `tests/test_verify_spec_confirmed.py`
- `.agent-work/epic-418-redux/notes-488-489.md` (working notes, sole writer this wave)
- `.agent-work/w3c-488-489/**` (plan, journal, context, mechanical, PR body — engine-owned artifacts)

**Specific exclusions touched:** no. `scripts/checklist_engine.py` (fenced to #465) and
`tests/test_episode_negative_control.py` (fenced to #461) were not touched. The gauge binding
key's shape is unchanged.

## Behavior changed
Yes.

- `resolve_gauge_path` now returns one candidate, not two, when two bindings resolve to the
  identical gauge path (e.g. an Admiral's own `spine.json` plus the `latitude-interrogation.json`
  its own spine step requires, both under one work directory) — so `handle_post_tool_use` writes
  a real `gauge.json` reading instead of firing the ambiguous-binding skip. Genuinely different
  gauge paths still produce 2+ distinct candidates and the skip still fires (#261 unweakened).
- `ConfirmPhaseRegressionOnALiveSpec._fixture` in the test suite now raises loudly, naming every
  match, if the `REVISED_SPEC.md` glob under `.agent-work/*/spec-revision/` ever finds 2+ files,
  instead of silently verifying the alphabetically-first one. Zero-match behavior (skip) is
  unchanged. Today there is exactly one match, so no live test behavior changed.

## Map Impact
- **Structural anchors touched:** `struct:gauge_writer_hook.resolve_gauge_path` —
  `scripts/hooks/gauge_writer_hook.py` — candidate list is now deduped by distinct `Path` before
  the caller's ambiguity check runs.
- **Capabilities added/changed/affected:** the context-governor gauge write now covers the
  same-work-dir multi-binding case (an Admiral driving its own `latitude` step) that previously
  went dark for a full wave; see "Behavior changed" above.
- **Constraints/assumptions touched:** `decision:dont-weaken-261` — honored; the negative
  direction (genuinely different gauge paths) is covered by a dedicated test and still skips.
- **Claims/evidence produced:** `.agent-work/epic-418-redux/notes-488-489.md` carries the
  before/after evidence for both missions, including both directions of #488's fix.
- **Triage candidates:** none beyond what the launch order already named out of scope (#452
  multi-spine attribution, #458 shipping the writer) — not touched, no new overlap found.

## Test mode
**Required:** `test-first (TDD)` — build the defective world, observe it wrong, then fix.
**Satisfied:** yes. Both missions' before-states were captured against the pre-fix code (see
Evidence and TDD sections below and the pasted transcripts in
`.agent-work/epic-418-redux/notes-488-489.md`).

## Evidence

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

**Result:** pass. `1789 passed, 2 skipped, 683 subtests passed in 522.48s (0:08:42)`, real exit
code `0` (captured via `echo "EXIT_CODE=$?"` immediately after the command, not through a pipe).

Targeted runs (also captured, see notes file):
- `tests/test_gauge_writer.py` — 70 passed (67 pre-existing + 3 new).
- `tests/test_verify_spec_confirmed.py` — 26 passed (22 pre-existing + 4 new).

Isolation proof, run before the git operations in this session:
```
$ python scripts/verify_worktree_isolation.py --here C:/Programs/wt-w3c-488-489
worktree OK: in C:/Programs/wt-w3c-488-489
```

## TDD evidence, if required

- Failing test observed (#488): `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_gauge_writer.py -k "dedups_two_bindings or admiral_shape"` → `2 failed, 1 passed, 67 deselected` against pre-fix `resolve_gauge_path` — the same-work-dir two-binding pair returned 2 candidates (should be 1), so `handle_post_tool_use` wrote no `gauge.json`. The negative-direction test (genuinely different work dirs) already passed pre-fix.
- Failing test observed (#489): ad hoc repro of the exact pre-fix `matches[0]` logic against a synthetic two-fixture tmp `.agent-work/` tree silently returned SPEC A's content and dropped SPEC B with no error or signal.
- Passing test observed: full suite green, `1789 passed, 2 skipped, 683 subtests`, exit 0 (above). Targeted files also independently green (70/70 and 26/26).
- Refactor while green: yes — `_resolve_revised_spec_matches` was extracted as a named helper with `_fixture` delegating to it, then re-verified green.

## Docs/contracts touched
- none — no `docs/agents/*` doctrine changed; this is a bounded bugfix pair.

## Assumptions
- None beyond what the launch order already stated (one PR for both fixes, per
  `decision:one-pr-or-two-is-yours`).

## Stop conditions hit
- None. Neither fix required crossing a fence, changing the binding key's shape, or exceeding
  the two issues' scope.

## Out-of-scope observations
- None new. The launch order's own out-of-scope notes (#452, #458, #457) were not encountered as
  live obstacles during this session's work (commit, push, PR).

## Workflow Feedback
- **Handoff gaps:** none — the launch order (`LO-488-489.md`) and the predecessor's plan/notes
  were sufficient to cold-start this continuation without re-deriving the work from the issues.
- **Context rediscovered:** the working branch had zero commits of its own and was 10 commits
  behind `origin/main` (fast-forwardable) when this session picked it up — the predecessor had
  made all its changes as uncommitted working-tree edits. Fast-forwarding to `origin/main` first,
  then committing, was necessary before push/PR; this wasn't itself documented anywhere for the
  continuation to expect, though it's a reasonable consequence of a mid-flight governor trip.
- **Instructions improvised around:** none.
- **What would have made this easier:** none — the dispatch prompt's explicit statement of
  "gate is m3-verify, both fixes are implemented, what remains is X/Y/Z" made cold-start
  straightforward.

## Return status
`complete`
