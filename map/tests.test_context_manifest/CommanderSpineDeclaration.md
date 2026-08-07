# tests.test_context_manifest:CommanderSpineDeclaration
class, tests/test_context_manifest.py:530, 84 lines

```python
class CommanderSpineDeclaration(TestCase)
```

The first real declaration in the corpus. (Pinning the declaration against

the step's imperative prose is a separate lint and is deliberately not here.)

```python
TEMPLATE = ROOT / 'skills' / 'commander' / 'templates' / 'COMMANDER_SPINE.template.json'
EXPECTED = [('skill', 'references/global-orchestrator.md', True), ('skill', 'references/global-eve...
```

- [setUp](CommanderSpineDeclaration.setUp.md) method: HOLE: no docstring
- [test_the_declaration_is_exactly_the_pinned_root_path_required_list](CommanderSpineDeclaration.test_the_declaration_is_exactly_the_pinned_root_path_required_list.md) method: HOLE: no docstring
- [test_declaration_is_ordered_wellformed_and_non_empty](CommanderSpineDeclaration.test_declaration_is_ordered_wellformed_and_non_empty.md) method: HOLE: no docstring
- [test_declaration_projects_one_row_per_entry_in_declared_order](CommanderSpineDeclaration.test_declaration_projects_one_row_per_entry_in_declared_order.md) method: HOLE: no docstring
- [test_only_the_context_step_carries_a_declaration](CommanderSpineDeclaration.test_only_the_context_step_carries_a_declaration.md) method: HOLE: no docstring
- [test_the_context_imperative_prose_is_not_replaced_by_the_declaration](CommanderSpineDeclaration.test_the_context_imperative_prose_is_not_replaced_by_the_declaration.md) method: HOLE: no docstring

reads internal: ROOT
writes internal: CommanderSpineDeclaration.EXPECTED, CommanderSpineDeclaration.TEMPLATE

referenced by: none found
