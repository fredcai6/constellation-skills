# tests.test_context_determinism:TheComparisonHasTeeth
class, tests/test_context_determinism.py:322, 69 lines

```python
class TheComparisonHasTeeth(TestCase)
```

The acceptance test above, turned on itself.

A determinism test that cannot fail is worse than none, because it reads as
coverage. This class runs the *same* two-child harness against deliberately
defective producers and asserts the comparison **does** separate them — and,
as a control, that the real producer still comes out byte-identical through
the identical path, so a difference here means the defect and not the harness.

- [_producer](TheComparisonHasTeeth._producer.md) method: A copy of the real producer under `tmp`, optionally poisoned.
- [content_bytes_from_two_environments](TheComparisonHasTeeth.content_bytes_from_two_environments.md) method: HOLE: no docstring
- [test_the_real_producer_is_byte_identical_through_this_harness](TheComparisonHasTeeth.test_the_real_producer_is_byte_identical_through_this_harness.md) method: HOLE: no docstring
- [test_an_environment_dependent_encoder_is_caught](TheComparisonHasTeeth.test_an_environment_dependent_encoder_is_caught.md) method: HOLE: no docstring
- [test_a_varying_field_placed_outside_run_is_caught](TheComparisonHasTeeth.test_a_varying_field_placed_outside_run_is_caught.md) method: HOLE: no docstring

referenced by: none found
