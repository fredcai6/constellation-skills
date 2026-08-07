# tests.test_checklist_engine:UnknownCondIdRecovery
class, tests/test_checklist_engine.py:2089, 18 lines

```python
class UnknownCondIdRecovery(TestCase)
```

Constraint 3 (issue #227 gate g3): unknown-cond-id is a 4th axis

OUTSIDE the (status, verb) grid -- a malformed-argument refusal, not a
status one. Its own standalone test: the refusal must literally contain
EVERY real p*/c* id on the task, not just the words
'preconditions'/'postconditions' (test_attest_not_found_names_both_lists
at :236 only asserts the latter and must not be mistaken for coverage of
this).

- [test_unknown_cond_id_enumerates_every_real_id_on_the_task](UnknownCondIdRecovery.test_unknown_cond_id_enumerates_every_real_id_on_the_task.md) method: HOLE: no docstring

referenced by: none found
