# tests.test_context_declaration_lint
tests/test_context_declaration_lint.py, 236 lines, 18 holes

Tests for `scripts/verify_context_declaration.py` -- the mechanical lint

pinning every declared `context_refs` path against the step's own imperative
prose.

The load-bearing test here is `test_divergent_declaration_is_rejected`: a lint
that only passes over the clean shipped corpus proves the corpus is clean, not
that the lint works. `tests/fixtures/context_declaration_lint.json` therefore
carries a fixture whose declaration and prose genuinely diverge, and this
module asserts the lint fails *for that reason* (the offending path is named
in the diagnostic), not merely that some exit code happened to be non-zero --
asserting bare non-zero from a probe that fails for an unrelated reason is the
exact defect this suite is shaped to avoid reintroducing.

imports stdlib: __future__.annotations, contextlib, importlib.util, io, json, pathlib.Path, tempfile.TemporaryDirectory, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
FIXTURES = json.loads((ROOT / 'tests' / 'fixtures' / 'context_declaration_lint.json').read_text(en...
```

- [load](load.md) function: HOLE: no docstring
- [test_divergent_declaration_is_rejected](test_divergent_declaration_is_rejected.md) function: The load-bearing negative test, named and shaped exactly as the gate's
- [CheckChecklistTests](CheckChecklistTests.md) class: Direct tests against the pure `check_checklist` function -- no CLI, no
  - [CheckChecklistTests.setUp](CheckChecklistTests.setUp.md) method: HOLE: no docstring
  - [CheckChecklistTests.test_check_checklist_reports_the_narrowed_away_path](CheckChecklistTests.test_check_checklist_reports_the_narrowed_away_path.md) method: HOLE: no docstring
  - [CheckChecklistTests.test_check_checklist_accepts_the_valid_fixture](CheckChecklistTests.test_check_checklist_accepts_the_valid_fixture.md) method: HOLE: no docstring
  - [CheckChecklistTests.test_prose_naming_more_than_declared_is_not_flagged](CheckChecklistTests.test_prose_naming_more_than_declared_is_not_flagged.md) method: HOLE: no docstring
  - [CheckChecklistTests.test_suffix_of_a_longer_path_is_rejected](CheckChecklistTests.test_suffix_of_a_longer_path_is_rejected.md) method: HOLE: no docstring
  - [CheckChecklistTests.test_legitimate_boundary_occurrences_are_accepted](CheckChecklistTests.test_legitimate_boundary_occurrences_are_accepted.md) method: HOLE: no docstring
  - [CheckChecklistTests.test_trailing_extension_glued_to_a_shorter_path_is_rejected](CheckChecklistTests.test_trailing_extension_glued_to_a_shorter_path_is_rejected.md) method: HOLE: no docstring
  - [CheckChecklistTests.test_legitimate_trailing_occurrences_are_accepted](CheckChecklistTests.test_legitimate_trailing_occurrences_are_accepted.md) method: HOLE: no docstring
- [CliTests](CliTests.md) class: End-to-end through `main()` -- the real entry point CI would invoke.
  - [CliTests.setUp](CliTests.setUp.md) method: HOLE: no docstring
  - [CliTests._write_fixture](CliTests._write_fixture.md) method: HOLE: no docstring
  - [CliTests.test_valid_declaration_is_accepted](CliTests.test_valid_declaration_is_accepted.md) method: HOLE: no docstring
  - [CliTests.test_lint_passes_over_real_shipped_spine_templates](CliTests.test_lint_passes_over_real_shipped_spine_templates.md) method: HOLE: no docstring
  - [CliTests.test_nonexistent_path_fails_visibly_not_silently](CliTests.test_nonexistent_path_fails_visibly_not_silently.md) method: HOLE: no docstring
  - [CliTests.test_narrowed_declaration_is_deliberately_not_caught](CliTests.test_narrowed_declaration_is_deliberately_not_caught.md) method: HOLE: no docstring
- [DiscoveryTests](DiscoveryTests.md) class: The default (no explicit paths) discovery path, since CI will invoke the
  - [DiscoveryTests.setUp](DiscoveryTests.setUp.md) method: HOLE: no docstring
  - [DiscoveryTests.test_default_discovery_finds_the_commander_spine_and_passes](DiscoveryTests.test_default_discovery_finds_the_commander_spine_and_passes.md) method: HOLE: no docstring
  - [DiscoveryTests.test_default_discovery_skips_non_checklist_template_json](DiscoveryTests.test_default_discovery_skips_non_checklist_template_json.md) method: HOLE: no docstring
