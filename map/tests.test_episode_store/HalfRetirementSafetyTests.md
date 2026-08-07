# tests.test_episode_store:HalfRetirementSafetyTests
class, tests/test_episode_store.py:1953, 227 lines

```python
class HalfRetirementSafetyTests(QueryTestCase)
```

C6 — the store is never left HALF-RETIRED.

A retirement has two halves: the field update (`status`, `retired-reason`, …) and the
file's move into the archive. A store where one landed and the other did not is
corrupt in a specific, nasty way — it reads as retired while still being in the
ordinary-search candidate set, or vice versa — and nothing about it is loud.

Two independent defenses, proven separately below:

  1. **By construction.** The updated content is only ever rendered to the NEW path.
     "Fields updated but file not moved" has no representation in the write plan at
     all, and neither does its mirror image: there is one plan entry and it carries
     both halves. This is asserted directly against write_plan(), not inferred.
  2. **By compensation.** Binding the layout gave the placement phase a second step
     (place the archived file, remove the source), so a failure BETWEEN them would
     leave the id in both directories. Faults are injected at each step and the store
     is asserted consistent afterwards.

- [_sets](HalfRetirementSafetyTests._sets.md) method: (ordinary-set ids, archive ids) read straight off the filesystem, without
- [assert_consistent](HalfRetirementSafetyTests.assert_consistent.md) method: The invariant, stated once: an id is in EXACTLY ONE of the two sets, and the
- [test_the_write_plan_cannot_express_a_half_retirement](HalfRetirementSafetyTests.test_the_write_plan_cannot_express_a_half_retirement.md) method: HOLE: no docstring
- [test_a_failure_placing_the_archived_file_leaves_the_episode_wholly_unretired](HalfRetirementSafetyTests.test_a_failure_placing_the_archived_file_leaves_the_episode_wholly_unretired.md) method: HOLE: no docstring
- [test_a_failure_removing_the_source_rolls_the_retirement_back_whole](HalfRetirementSafetyTests.test_a_failure_removing_the_source_rolls_the_retirement_back_whole.md) method: The window binding Option A actually opened, and the one this gate owes.
- [test_a_half_retired_store_is_reported_rather_than_answered_around](HalfRetirementSafetyTests.test_a_half_retired_store_is_reported_rather_than_answered_around.md) method: Compensation covers every failure the process survives to observe; a hard kill
- [test_a_half_retired_store_is_loud_for_the_seams_that_do_not_scan](HalfRetirementSafetyTests.test_a_half_retired_store_is_loud_for_the_seams_that_do_not_scan.md) method: The other half of "loud", and the half that was missing.
- [test_a_successful_retirement_is_whole](HalfRetirementSafetyTests.test_a_successful_retirement_is_whole.md) method: HOLE: no docstring

referenced by: none found
