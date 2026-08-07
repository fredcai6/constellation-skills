# tests.test_install_constellation:HookWiringDetectionTests
class, tests/test_install_constellation.py:1988, 202 lines

```python
class HookWiringDetectionTests(_HookWiringFixture)
```

Always-on, no-flag detection (#262). Three states -- wired / stale /

unwired -- classified by RESOLVING the referenced path against the
filesystem, never by string-matching it.

`stale` is the load-bearing state and is not polish: under binary detection
a moved or renamed install reads as *wired*, which is the reassuring-failure
shape. Per #265, "hook not wired at all" is the one silence cause the gauge
writer can never self-report -- a hook that never runs cannot write a sidecar
explaining that it never ran -- so this detector is the only thing in the
system that can ever surface it.

The other half is a human ruling (`decision:opt-in-wiring-only`): without
`--wire-hooks` the installer reads and reports and writes NOTHING, and does
not even create an absent settings.json.

- [test_detects_unwired_when_settings_json_is_absent](HookWiringDetectionTests.test_detects_unwired_when_settings_json_is_absent.md) method: HOLE: no docstring
- [test_detects_unwired_when_settings_has_no_governor_entry](HookWiringDetectionTests.test_detects_unwired_when_settings_has_no_governor_entry.md) method: HOLE: no docstring
- [test_detects_wired_when_the_entry_resolves_on_disk](HookWiringDetectionTests.test_detects_wired_when_the_entry_resolves_on_disk.md) method: HOLE: no docstring
- [test_detects_stale_when_the_entry_path_no_longer_exists](HookWiringDetectionTests.test_detects_stale_when_the_entry_path_no_longer_exists.md) method: The moved-install case. A string-matching detector reports this as
- [test_detection_classifies_by_resolution_not_by_string_match](HookWiringDetectionTests.test_detection_classifies_by_resolution_not_by_string_match.md) method: Two entries, textually indistinguishable in shape; only one has a file
- [test_detection_expands_env_tokens_in_a_hand_wired_entry](HookWiringDetectionTests.test_detection_expands_env_tokens_in_a_hand_wired_entry.md) method: docs/GAUGE_WRITER_HOOK.md currently tells users to hand-wire a
- [test_detection_will_not_expand_an_arbitrary_env_var](HookWiringDetectionTests.test_detection_will_not_expand_an_arbitrary_env_var.md) method: Regression, reproduced by the g2 reviewer: expansion happens in the
- [test_undeterminable_is_reported_as_neither_wired_nor_stale](HookWiringDetectionTests.test_undeterminable_is_reported_as_neither_wired_nor_stale.md) method: "I cannot tell" must not be laundered into either confident verdict.
- [test_a_resolvable_entry_still_wins_over_an_undeterminable_one](HookWiringDetectionTests.test_a_resolvable_entry_still_wins_over_an_undeterminable_one.md) method: A real working entry alongside an unevaluatable one is WIRED: the
- [test_detection_survives_an_unparseable_settings_json](HookWiringDetectionTests.test_detection_survives_an_unparseable_settings_json.md) method: A broken settings.json must not take the install down with it, and
- [test_no_flag_install_run_reports_the_wiring_state](HookWiringDetectionTests.test_no_flag_install_run_reports_the_wiring_state.md) method: HOLE: no docstring
- [test_no_flag_install_run_does_not_create_an_absent_settings_json](HookWiringDetectionTests.test_no_flag_install_run_does_not_create_an_absent_settings_json.md) method: HOLE: no docstring
- [test_no_flag_install_run_leaves_settings_json_byte_identical](HookWiringDetectionTests.test_no_flag_install_run_leaves_settings_json_byte_identical.md) method: HOLE: no docstring
- [test_no_flag_dry_run_detects_without_writing](HookWiringDetectionTests.test_no_flag_dry_run_detects_without_writing.md) method: HOLE: no docstring
- [test_settings_path_is_the_sibling_of_the_installed_skills_dir](HookWiringDetectionTests.test_settings_path_is_the_sibling_of_the_installed_skills_dir.md) method: HOLE: no docstring
- [test_detection_is_skipped_for_agents_with_no_hook_mechanism](HookWiringDetectionTests.test_detection_is_skipped_for_agents_with_no_hook_mechanism.md) method: Hooks are a Claude Code mechanism. Reporting on -- let alone writing --

referenced by: none found
