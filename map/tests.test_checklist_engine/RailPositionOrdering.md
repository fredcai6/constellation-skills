# tests.test_checklist_engine:RailPositionOrdering
class, tests/test_checklist_engine.py:1960, 57 lines

```python
class RailPositionOrdering(TestCase)
```

Item 4 / constraint 4 (issue #227 gate g3): the RAIL banner moves to

the FRONT for every railed verb (including `current`), and to the front
of the REFUSED path in main() -- the operative result/refusal line lands
LAST on its stream, so `tail -1` reads the result, not the banner. This
is the exact field defect: the Admiral piped engine output through
`tail -1` and saw only the banner, silently hiding a real REFUSED line.

- [test_success_output_rail_banner_is_first_operative_line_is_last](RailPositionOrdering.test_success_output_rail_banner_is_first_operative_line_is_last.md) method: HOLE: no docstring
- [test_current_rail_banner_is_first_suffix_ordering_after_body_unchanged](RailPositionOrdering.test_current_rail_banner_is_first_suffix_ordering_after_body_unchanged.md) method: HOLE: no docstring
- [test_refused_output_rail_banner_is_first_operative_refused_line_is_last](RailPositionOrdering.test_refused_output_rail_banner_is_first_operative_refused_line_is_last.md) method: HOLE: no docstring
- [test_tail_minus_1_yields_refusal_not_banner_state_caused](RailPositionOrdering.test_tail_minus_1_yields_refusal_not_banner_state_caused.md) method: HOLE: no docstring
- [test_tail_minus_1_yields_success_result_not_banner](RailPositionOrdering.test_tail_minus_1_yields_success_result_not_banner.md) method: HOLE: no docstring
- [test_survey_refusal_still_no_rail_operative_line_still_last](RailPositionOrdering.test_survey_refusal_still_no_rail_operative_line_still_last.md) method: HOLE: no docstring

referenced by: none found
