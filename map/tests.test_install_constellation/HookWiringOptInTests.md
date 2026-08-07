# tests.test_install_constellation:HookWiringOptInTests
class, tests/test_install_constellation.py:2192, 276 lines

```python
class HookWiringOptInTests(_HookWiringFixture)
```

`--wire-hooks` -- the ONLY path on which the installer writes a

settings.json (`decision:opt-in-wiring-only`, a human ruling).

The command string carries an ABSOLUTE installed path, never
`${CLAUDE_PROJECT_DIR}`. That variable happens to deliver anti-tamper today
only as an accident of undocumented harness behaviour (#269: it is fixed at
session launch, so it happens to point at the main checkout for a worktree
agent). An absolute installed path is pinned BY CONSTRUCTION and asks the
harness to guarantee nothing -- which is what actually protects Fred's
ruling that an agent's own branch cannot edit the code that judges it.

```python
UNRELATED = {'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': 'py "${CLAUDE_PROJECT_DIR}...
```

- [_wire](HookWiringOptInTests._wire.md) method: HOLE: no docstring
- [_settings_json](HookWiringOptInTests._settings_json.md) method: HOLE: no docstring
- [_entries](HookWiringOptInTests._entries.md) method: HOLE: no docstring
- [test_wire_hooks_writes_an_absolute_path_not_a_project_dir_token](HookWiringOptInTests.test_wire_hooks_writes_an_absolute_path_not_a_project_dir_token.md) method: HOLE: no docstring
- [test_wired_command_uses_the_probed_interpreter_and_documented_timeout](HookWiringOptInTests.test_wired_command_uses_the_probed_interpreter_and_documented_timeout.md) method: The interpreter comes from the existing probe, not a hardcoded `py`;
- [test_the_wired_command_string_actually_executes](HookWiringOptInTests.test_the_wired_command_string_actually_executes.md) method: Run the generated command EXACTLY as Claude Code would -- same string,
- [test_a_wired_entry_then_detects_as_wired](HookWiringOptInTests.test_a_wired_entry_then_detects_as_wired.md) method: Round trip: what the wiring writes is what the detector recognises.
- [test_wire_hooks_with_dry_run_together_writes_nothing](HookWiringOptInTests.test_wire_hooks_with_dry_run_together_writes_nothing.md) method: THE risky combination, and it gets its own test on purpose: `dry_run`
- [test_wire_hooks_with_dry_run_does_not_create_an_absent_settings_json](HookWiringOptInTests.test_wire_hooks_with_dry_run_does_not_create_an_absent_settings_json.md) method: HOLE: no docstring
- [test_wire_hooks_is_additive_and_preserves_unrelated_settings](HookWiringOptInTests.test_wire_hooks_is_additive_and_preserves_unrelated_settings.md) method: An unrelated PostToolUse matcher must survive intact and unreordered,
- [test_wire_hooks_appends_a_sibling_and_never_nests_in_an_existing_matcher](HookWiringOptInTests.test_wire_hooks_appends_a_sibling_and_never_nests_in_an_existing_matcher.md) method: HOLE: no docstring
- [test_wire_hooks_creates_settings_json_only_under_the_opt_in_flag](HookWiringOptInTests.test_wire_hooks_creates_settings_json_only_under_the_opt_in_flag.md) method: HOLE: no docstring
- [test_wire_hooks_twice_does_not_duplicate_the_entry](HookWiringOptInTests.test_wire_hooks_twice_does_not_duplicate_the_entry.md) method: HOLE: no docstring
- [test_wire_hooks_leaves_a_stale_entry_in_place_and_adds_a_sibling](HookWiringOptInTests.test_wire_hooks_leaves_a_stale_entry_in_place_and_adds_a_sibling.md) method: No self-healing, by design (the design brief names this an accepted
- [test_wire_hooks_hard_errors_when_the_canonical_owner_is_not_installed](HookWiringOptInTests.test_wire_hooks_hard_errors_when_the_canonical_owner_is_not_installed.md) method: Refusing to wire something it cannot locate is correct, and is NOT a
- [test_wire_hooks_refuses_an_unparseable_settings_json_without_clobbering](HookWiringOptInTests.test_wire_hooks_refuses_an_unparseable_settings_json_without_clobbering.md) method: HOLE: no docstring
- [test_wire_hooks_is_rejected_for_an_agent_with_no_hook_mechanism](HookWiringOptInTests.test_wire_hooks_is_rejected_for_an_agent_with_no_hook_mechanism.md) method: HOLE: no docstring
- [test_wire_hooks_is_rejected_with_baseline_only](HookWiringOptInTests.test_wire_hooks_is_rejected_with_baseline_only.md) method: HOLE: no docstring
- [test_wire_hooks_at_project_scope_warns_the_file_is_committable](HookWiringOptInTests.test_wire_hooks_at_project_scope_warns_the_file_is_committable.md) method: An absolute path embeds the user's home directory AND username, and a

reads stdlib: builtins.dict, builtins.list
writes internal: HookWiringOptInTests.UNRELATED

referenced by: none found
