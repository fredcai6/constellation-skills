# Implementation Result

## Assigned gate
`issue-464` — rename `CONSTELLATION_FEEDBACK`'s `Lesson:` field to match what it now
carries (an episode id), together with its collector, in one change.

## Completed slice
Renamed the field to **`Episode`** across `skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md`,
`.agent-work/CONSTELLATION_FEEDBACK.md` (header prose only), and
`scripts/collect_feedback.py` (`fingerprint()`/`fingerprints()` read `entry['episode']`
first, falling back to `entry['lesson']`), landed in one change with 4 named tests
in `tests/test_feedback_tooling.py` (2 renamed, 2 added).

## Scope
**Files changed:**
- `skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md`
- `.agent-work/CONSTELLATION_FEEDBACK.md`
- `scripts/collect_feedback.py`
- `tests/test_feedback_tooling.py`
- `tests/data/store_mentions.approved.txt` (see below — not a fenced file, a
  required consequence of the rename)

**Specific exclusions touched:** no — `scripts/checklist_engine.py`, `episodes/`,
`scripts/apply_episode_delta.py`, `scripts/verify_worktree_precondition_coverage.py`
were not touched.

## Behavior changed
Yes: `collect_feedback.py` now identifies a finding primarily by an `Episode` field
(same fingerprinting behavior as before, keyed on a new field name), falling back
to the legacy `Lesson` field for un-upgraded external exports. The internal hash
prefix stays the literal `'lesson:'` string, so every fingerprint already recorded
in `CONSTELLATION_FEEDBACK.collected.json`/`CONSTELLATION_INBOX.json` keeps matching
— no re-filing, no orphaned identities.

## Test mode
**Required:** test-first (TDD)
**Satisfied:** yes — the 4 named tests were written/renamed and observed failing
against the pre-rename collector before any implementation edit.

## Evidence

**Enumeration, before (run against the untouched tree by the design predecessor,
reproduced verbatim by me):**
```bash
grep -rn -e '\*\*Lesson\[:*\]' -e '"lesson"' -e \'lesson\' -e 'Lesson field' scripts/ \
  .agent-work/CONSTELLATION_FEEDBACK.md skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md \
  tests/test_feedback_tooling.py
```
→ 12 hits: 3 in `collect_feedback.py` (code, changed), 1 in `CONSTELLATION_FEEDBACK.md:14`
(header, changed), 3 in `CONSTELLATION_FEEDBACK.md:140/173/216` (historical narrative,
left untouched — pre-#447 lesson-slug values, not machine-parsed), 2 in `template.md:14+23`
(changed), 2 in the test file (renamed), 3 in the test file (external-shape tests, left).

**Enumeration, after (same command):**
→ 4 hits, all in the deliberately-kept fallback/external-format set:
`collect_feedback.py:65` (`_PROSE_LABELS['lesson']`, external prose-shape mapping),
`collect_feedback.py:237,261` (the required `entry.get('lesson', '')` fallback),
`tests/test_feedback_tooling.py:267` (new precedence test, uses `'lesson'` on purpose).
Zero readers of the OLD FIELD NAME remain in the must-fix set (template.md,
`CONSTELLATION_FEEDBACK.md` header, or `collect_feedback.py`'s primary read path).
A broader fixed-regex pass (`\*\*Lesson:\*\*` instead of the bracket-escaped variant
above) additionally surfaces the 3 historical narrative lines and 4 more
untouched/new test lines — all confirmed deliberately excluded (see notes-464.md).

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_feedback_tooling.py -k \
  'episode_id_groups_across_slug_drift or episode_id_takes_precedence_over_slug or \
   legacy_lesson_field_format_still_fingerprints or episode_field_takes_precedence_over_legacy_lesson_field'
```
**Result:** pass — `4 passed, 29 deselected` (real exit 0).

```bash
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```
**Result:** pass — **1723 passed, 4 skipped, 643 subtests passed, real exit 0**
(strictly greater than the 1721-passed baseline; +2 for the two new tests, the two
renames don't change the count). First run of this command surfaced 2 self-inflicted
failures (see below); after the fix, re-run confirmed 1723/0-failed.

## TDD evidence
- Failing test observed: 3 of 4 named tests failed against the pre-rename
  collector (`test_episode_id_groups_across_slug_drift`,
  `test_episode_id_takes_precedence_over_slug`,
  `test_episode_field_takes_precedence_over_legacy_lesson_field`); the 4th
  (`test_legacy_lesson_field_format_still_fingerprints`) already passed since that
  code path was unchanged by design.
- Passing test observed: all 4 named tests pass after implementation; full
  `test_feedback_tooling.py` (33 tests) and the full suite (1723) both green.
- Refactor while green: no refactor step beyond the fix below.

## Docs/contracts touched
- `skills/workbench/templates/CONSTELLATION_FEEDBACK.template.md`,
  `.agent-work/CONSTELLATION_FEEDBACK.md` — both in scope, both intended.

## Assumptions
- None beyond what the predecessor's DIGEST already settled.

## Stop conditions hit
- None. No scope change, no fence reach, no out-of-latitude decision needed.

## Out-of-scope observations
- **Self-inflicted, caught and fixed, not filed as triage:** my first pass at the
  `collect_feedback.py` docstrings used the phrase "episode store," which trips
  `scripts/verify_retirement.py`'s `unapproved-store-mention` leg (a frozen
  approval census guarding `constraint:episodes-are-not-prescriptions`, #447/#403).
  Reworded both mentions to drop "episode store" entirely — no behavior change.
  Separately, the template rename invalidated one exact-match entry in
  `tests/data/store_mentions.approved.txt` (`test_every_approved_entry_exists_verbatim`
  failed); updated that one census line (`Lesson:` -> `Episode:`) to match, since
  the line's `episodes/` content and reason are unchanged — only the field label
  moved, which is exactly what this issue asked for. Both fixes are docs/test-data
  only; full detail in `.agent-work/epic-418-redux/notes-464.md`.
- **Context governor pattern worth a look:** every fresh crew-tier agent in this
  session's team arrived already at ~20%+ context fill before touching the task
  (baseline session overhead: CLAUDE.md, memory index, full skill listing,
  teammate roster), tripping HARD against the 15% cap for claude-sonnet-5 before
  any real work. Fired twice in a row on this same plan. Not something I can fix
  from here; flagging for whoever owns the Context Governor calibration.

## Workflow Feedback
- **Handoff gaps:** none — the predecessor's DIGEST was a complete, accurate,
  self-sufficient brief; I found no gaps in the file list, fallback rationale, or
  test names it specified.
- **Context rediscovered:** the `unapproved-store-mention` retirement-guard leg and
  its frozen approval census (`tests/data/store_mentions.approved.txt`) — not
  mentioned anywhere in the handoff or DIGEST, and it fired only because of my own
  wording choice in a docstring I wasn't strictly required to touch (only
  `fingerprint()`/`fingerprints()` behavior was in the MUST-CHANGE list, not the
  module docstring). Worth a note in the implementer skill or engine-config docs:
  any prose edit inside `scripts/*.py` should be checked against
  `verify_retirement.py`'s store-mention patterns (`episodes/`, `episode store`,
  `query_episodes`, `apply_episode_delta`) before considering a change done, since
  the full-suite run is the only thing that surfaces it and it's an 8-minute round
  trip.
- **Instructions improvised around:** none.
- **What would have made this easier:** a one-line pointer from the launch order
  or DIGEST to `verify_retirement.py`'s store-mention census, given this issue sits
  directly adjacent to the #447 retirement boundary — would have saved one 8-minute
  full-suite round trip.

## Return status
`complete`
