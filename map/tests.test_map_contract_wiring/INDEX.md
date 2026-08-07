# tests.test_map_contract_wiring
tests/test_map_contract_wiring.py, 278 lines, 11 holes

The map-first contract as it is actually SERVED to a Commander run.

Two different things are pinned here and they must not be confused:

1. **The anchor** (`ContextImperativeAnchor`). PRE-B captured five runs with
   *verified* Commander loads, so both pathless map-first imperatives definitely
   fired -- and orientation still moved not at all (`map_before_src` false on 4
   of 4 runs that read source; bootstrap orientation 0 of 5). The measured
   diagnosis is that **a map-first imperative anchored to a late artifact is not
   a map-first imperative**: the served plan imperative said *"BEFORE authoring
   execute.json, produce a mission frame from the current map"*, and authoring
   `execute.json` happens at the END of a long run, so a run can crawl source for
   fifty calls, read the map, then author the frame and have **complied exactly**
   (run #698: source at call 25, map at call 57). The instruction was never
   ignored; it was satisfied by a sequence it does not constrain. These tests pin
   the CONTEXT imperative to an **act** anchor -- before you open any source file
   -- because `context` precedes `understand` and `plan` in the spine, so an
   instruction anchored there is anchored before exploration.

2. **The wiring** (`ContractWiring`). The two engine-checked command
   postconditions, and specifically their **asymmetry**: `verify-orientation` at
   CONTEXT, `verify-frame` at PLAN, and `verify-frame` deliberately NOT at
   context. See that class's docstring for why the cheap symmetric resolution
   silently destroys the property.

Honest limit, stated here so no reader has to infer it: none of this makes the
frame check *sound*. Measured against the epic's baseline five, the citation
check has sensitivity 0/4 and specificity 0/1. It ships as a regression floor so
map-*ignoring* cannot silently return; the measured defect is map-*lateness*,
and the anchor above -- not this wiring -- is the untested variable aimed at it.

imports stdlib: __future__.annotations, importlib.util, json, pathlib.Path, sys, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / 'skills' / 'commander' / 'templates' / 'COMMANDER_SPINE.template.json'
```

- [spine](spine.md) function: HOLE: no docstring
- [task](task.md) function: HOLE: no docstring
- [imperative](imperative.md) function: HOLE: no docstring
- [command_checks](command_checks.md) function: (condition id, command) for every `command` postcondition on `step`.
- [ContextImperativeAnchor](ContextImperativeAnchor.md) class: HOLE: no docstring
  - [ContextImperativeAnchor.test_the_map_read_is_anchored_before_any_source_file_is_opened](ContextImperativeAnchor.test_the_map_read_is_anchored_before_any_source_file_is_opened.md) method: The whole point. The anchor is an ACT the run cannot postpone.
  - [ContextImperativeAnchor.test_the_context_map_read_is_not_anchored_to_a_late_artifact](ContextImperativeAnchor.test_the_context_map_read_is_not_anchored_to_a_late_artifact.md) method: `execute.json` is authored at the END of a run.
  - [ContextImperativeAnchor.test_the_context_imperative_names_the_orient_command_it_expects](ContextImperativeAnchor.test_the_context_imperative_names_the_orient_command_it_expects.md) method: A pathless 'read the map' fired in all five PRE-B runs and moved
  - [ContextImperativeAnchor.test_later_source_reads_are_framed_as_confirming_not_building](ContextImperativeAnchor.test_later_source_reads_are_framed_as_confirming_not_building.md) method: The sequence claim, stated in the prose the agent actually reads.
  - [ContextImperativeAnchor.test_degraded_is_a_declared_reading_not_a_licence_to_start_from_code](ContextImperativeAnchor.test_degraded_is_a_declared_reading_not_a_licence_to_start_from_code.md) method: HOLE: no docstring
  - [ContextImperativeAnchor.test_every_declared_context_ref_still_appears_verbatim_in_the_prose](ContextImperativeAnchor.test_every_declared_context_ref_still_appears_verbatim_in_the_prose.md) method: `tests/test_context_declaration_lint.py` owns this rule; it is
  - [ContextImperativeAnchor.test_the_prose_rules_a_path_list_cannot_express_survive_the_rewrite](ContextImperativeAnchor.test_the_prose_rules_a_path_list_cannot_express_survive_the_rewrite.md) method: HOLE: no docstring
- [ContractWiring](ContractWiring.md) class: `verify-orientation` at CONTEXT, `verify-frame` at PLAN, and NEVER
  - [ContractWiring.test_context_c2_is_a_command_check_naming_verify_orientation](ContractWiring.test_context_c2_is_a_command_check_naming_verify_orientation.md) method: HOLE: no docstring
  - [ContractWiring.test_the_plan_step_carries_a_verify_frame_command_check](ContractWiring.test_the_plan_step_carries_a_verify_frame_command_check.md) method: HOLE: no docstring
  - [ContractWiring.test_verify_frame_never_runs_at_the_context_step](ContractWiring.test_verify_frame_never_runs_at_the_context_step.md) method: The load-bearing negative. No frame exists at context.
  - [ContractWiring.test_verify_orientation_is_not_duplicated_onto_the_plan_step](ContractWiring.test_verify_orientation_is_not_duplicated_onto_the_plan_step.md) method: Symmetry is the failure mode here, not the goal: the orientation
  - [ContractWiring.test_neither_new_check_uses_a_relative_root](ContractWiring.test_neither_new_check_uses_a_relative_root.md) method: Command checks inherit the launcher's cwd. `<repo-root>` (added in
  - [ContractWiring.test_the_plan_check_is_waivable_by_a_human_with_a_recorded_reason](ContractWiring.test_the_plan_check_is_waivable_by_a_human_with_a_recorded_reason.md) method: The trivial-change escape ('shrink or skip the frame') must survive
  - [ContractWiring.test_the_context_check_policy_is_tighter_than_the_plan_check](ContractWiring.test_the_context_check_policy_is_tighter_than_the_plan_check.md) method: No `override_policy` on the context check: waiving it needs the
  - [ContractWiring.test_the_plan_imperative_names_where_the_frame_must_be_written](ContractWiring.test_the_plan_imperative_names_where_the_frame_must_be_written.md) method: A check nobody can satisfy is worse than no check: the step that is
  - [ContractWiring.test_the_plan_imperative_records_the_asymmetry_and_the_road_not_to_take](ContractWiring.test_the_plan_imperative_records_the_asymmetry_and_the_road_not_to_take.md) method: Required in PROSE, not only in code: a future implementer hitting
  - [ContractWiring.test_the_plan_imperative_states_that_the_check_is_a_floor_not_the_fix](ContractWiring.test_the_plan_imperative_states_that_the_check_is_a_floor_not_the_fix.md) method: Do not overclaim: the plan-step check inherits the late-anchor defect
- [ScriptIsBundled](ScriptIsBundled.md) class: HOLE: no docstring
  - [ScriptIsBundled._installer](ScriptIsBundled._installer.md) method: HOLE: no docstring
  - [ScriptIsBundled.test_map_orient_ships_with_every_skill_whose_template_invokes_it](ScriptIsBundled.test_map_orient_ships_with_every_skill_whose_template_invokes_it.md) method: The drift this guards: `gauge_reader.py` was never added to any of
  - [ScriptIsBundled.test_the_bundled_script_source_actually_exists](ScriptIsBundled.test_the_bundled_script_source_actually_exists.md) method: HOLE: no docstring
