# tests.test_checklist_engine:NextVerbsAreLegalFromHere
class, tests/test_checklist_engine.py:4235, 129 lines

```python
class NextVerbsAreLegalFromHere(TestCase)
```

Rework 1 (#227 g2 review BLOCK): `next:` must only suggest a verb that

will NOT refuse from the state it renders — the ratified panel's invariant
4 ("next_verbs is exhaustive and legal-from-here… derived from (status,
position, condition state)"), which the pre-fix `_next_verbs()` violated.
The reviewer reproduced two concrete refusals: a pending gate with an open
null precondition suggested `start` (refused: preconditions unmet), and a
non-exempt in-progress gate with an open artifact postcondition suggested
`advance` (refused: postconditions unmet) — against the implementer's own
two canonical golden fixtures.

This closes the loop the golden (string-only) tests didn't: for a matrix
of task states and condition mixes, it ACTUALLY RUNS the verb `next:`
suggests against a tmp in-memory fixture (never a real spine file) and
asserts it does not raise `EngineError` — plus proves the terminal verb is
SUPPRESSED while a blocking null/artifact condition is open, and NOT
suppressed by an open command/git-change-policy condition (those are
live-checked inside start()/advance() itself, never probed by state()).

- [_next](NextVerbsAreLegalFromHere._next.md) method: HOLE: no docstring
- [test_pending_with_open_null_precondition_suppresses_start](NextVerbsAreLegalFromHere.test_pending_with_open_null_precondition_suppresses_start.md) method: HOLE: no docstring
- [test_pending_with_open_artifact_precondition_suppresses_start_until_attested](NextVerbsAreLegalFromHere.test_pending_with_open_artifact_precondition_suppresses_start_until_attested.md) method: HOLE: no docstring
- [test_pending_with_only_open_command_precondition_still_suggests_start](NextVerbsAreLegalFromHere.test_pending_with_only_open_command_precondition_still_suggests_start.md) method: HOLE: no docstring
- [test_pending_with_satisfied_preconditions_suggests_start_and_it_runs](NextVerbsAreLegalFromHere.test_pending_with_satisfied_preconditions_suggests_start_and_it_runs.md) method: HOLE: no docstring
- [test_in_progress_with_open_null_postcondition_suppresses_advance](NextVerbsAreLegalFromHere.test_in_progress_with_open_null_postcondition_suppresses_advance.md) method: HOLE: no docstring
- [test_in_progress_with_open_artifact_postcondition_suppresses_advance_until_attested](NextVerbsAreLegalFromHere.test_in_progress_with_open_artifact_postcondition_suppresses_advance_until_attested.md) method: HOLE: no docstring
- [test_in_progress_with_only_open_command_postcondition_still_suggests_advance](NextVerbsAreLegalFromHere.test_in_progress_with_only_open_command_postcondition_still_suggests_advance.md) method: HOLE: no docstring
- [test_in_progress_non_exempt_advance_hint_carries_why_and_runs](NextVerbsAreLegalFromHere.test_in_progress_non_exempt_advance_hint_carries_why_and_runs.md) method: HOLE: no docstring
- [test_blocked_resume_hint_runs](NextVerbsAreLegalFromHere.test_blocked_resume_hint_runs.md) method: HOLE: no docstring
- [test_survey_in_progress_record_hint_runs_even_with_open_null_postcondition](NextVerbsAreLegalFromHere.test_survey_in_progress_record_hint_runs_even_with_open_null_postcondition.md) method: HOLE: no docstring

referenced by: none found
