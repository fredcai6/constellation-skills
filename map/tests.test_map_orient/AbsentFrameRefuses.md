# tests.test_map_orient:AbsentFrameRefuses
class, tests/test_map_orient.py:726, 43 lines

```python
class AbsentFrameRefuses(TestCase)
```

THE load-bearing negative case of this gate.

A check that passes when the artifact it checks does not exist is not a
check -- it is a decoration that reports success for every run that skips
the work entirely. Everything else in `verify-frame` is downstream of this
one refusal, which is why it was written first.

- [test_an_absent_frame_refuses_on_a_resolved_repo](AbsentFrameRefuses.test_an_absent_frame_refuses_on_a_resolved_repo.md) method: HOLE: no docstring
- [test_an_absent_frame_refuses_on_a_degraded_repo_too](AbsentFrameRefuses.test_an_absent_frame_refuses_on_a_degraded_repo_too.md) method: The degraded arm must not become the vacuous-pass back door.
- [test_an_empty_frame_file_is_the_same_as_no_frame](AbsentFrameRefuses.test_an_empty_frame_file_is_the_same_as_no_frame.md) method: HOLE: no docstring
- [test_the_refusal_names_the_path_it_looked_for](AbsentFrameRefuses.test_the_refusal_names_the_path_it_looked_for.md) method: HOLE: no docstring
- [test_a_frame_without_a_receipt_refuses_rather_than_passing](AbsentFrameRefuses.test_a_frame_without_a_receipt_refuses_rather_than_passing.md) method: No orientation happened at all -- the frame cannot be checked

referenced by: none found
