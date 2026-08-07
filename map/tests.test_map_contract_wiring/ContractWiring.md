# tests.test_map_contract_wiring:ContractWiring
class, tests/test_map_contract_wiring.py:138, 96 lines

```python
class ContractWiring(TestCase)
```

`verify-orientation` at CONTEXT, `verify-frame` at PLAN, and NEVER

`verify-frame` at context.

The first draft of this plan was ambiguous here and a cold critic BLOCKed
it, because the cheap resolution -- run the same pair at both steps and let
an absent frame pass at context -- silently destroys the property the frame
check exists for. No frame exists at context: the step runs before
`understand` and `plan`. Making 'absent frame' a pass anywhere teaches the
checker that an absent frame is acceptable, and the ABSENT-frame refusal is
the single most important negative case in the whole contract (an absent
frame must never vacuously pass). The road not to take, recorded so a future
implementer hitting the contradiction does not take it: do NOT resolve the
asymmetry by weakening the refusal. If `verify-frame` ever has to be
context-safe, add a step-scoped subcommand -- never a vacuous pass.

- [test_context_c2_is_a_command_check_naming_verify_orientation](ContractWiring.test_context_c2_is_a_command_check_naming_verify_orientation.md) method: HOLE: no docstring
- [test_the_plan_step_carries_a_verify_frame_command_check](ContractWiring.test_the_plan_step_carries_a_verify_frame_command_check.md) method: HOLE: no docstring
- [test_verify_frame_never_runs_at_the_context_step](ContractWiring.test_verify_frame_never_runs_at_the_context_step.md) method: The load-bearing negative. No frame exists at context.
- [test_verify_orientation_is_not_duplicated_onto_the_plan_step](ContractWiring.test_verify_orientation_is_not_duplicated_onto_the_plan_step.md) method: Symmetry is the failure mode here, not the goal: the orientation
- [test_neither_new_check_uses_a_relative_root](ContractWiring.test_neither_new_check_uses_a_relative_root.md) method: Command checks inherit the launcher's cwd. `<repo-root>` (added in
- [test_the_plan_check_is_waivable_by_a_human_with_a_recorded_reason](ContractWiring.test_the_plan_check_is_waivable_by_a_human_with_a_recorded_reason.md) method: The trivial-change escape ('shrink or skip the frame') must survive
- [test_the_context_check_policy_is_tighter_than_the_plan_check](ContractWiring.test_the_context_check_policy_is_tighter_than_the_plan_check.md) method: No `override_policy` on the context check: waiving it needs the
- [test_the_plan_imperative_names_where_the_frame_must_be_written](ContractWiring.test_the_plan_imperative_names_where_the_frame_must_be_written.md) method: A check nobody can satisfy is worse than no check: the step that is
- [test_the_plan_imperative_records_the_asymmetry_and_the_road_not_to_take](ContractWiring.test_the_plan_imperative_records_the_asymmetry_and_the_road_not_to_take.md) method: Required in PROSE, not only in code: a future implementer hitting
- [test_the_plan_imperative_states_that_the_check_is_a_floor_not_the_fix](ContractWiring.test_the_plan_imperative_states_that_the_check_is_a_floor_not_the_fix.md) method: Do not overclaim: the plan-step check inherits the late-anchor defect

referenced by: none found
