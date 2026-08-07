# tests.test_fowler_pass
tests/test_fowler_pass.py, 255 lines, 31 holes

Tests for the constellation-reviewer sharpening rail

(scripts/verify_fowler_pass.py).

The reviewer drives a survey whose `r6-fowler` item runs a refactoring / code-smell
pass in the sense of Martin Fowler's *Refactoring*. This rail mechanically enforces
the two locked behaviors of DESIGN_SPEC Section D3 on the Fowler-pass RECORD:

  * VisitEverySmellTests -- the pass must render a verdict on every baseline Fowler
                            smell; a record that omits one is REFUSED (it can't be
                            silently narrowed so a present smell is never looked at).
  * PlantedSmellTests    -- a fixture carrying an obvious Fowler smell is SURFACED:
                            a record that flags it passes and the smell shows in the
                            flagged set; a record that drops that smell is refused.
  * OverrideLogTests     -- a smell judged subordinate to a DOCUMENTED repo standard
                            (verdict `overridden`, so not flagged) is honored ONLY
                            with a logged reason (standard + why); an override with
                            no logged reason is REFUSED (the bounded rail).
  * RailExceptionTests   -- skipping the WHOLE pass needs an independent reviewer's
                            co-sign + a log; self-assertion never passes, and the
                            exception never excuses a single unlogged override.
  * StructureTests       -- record-shape refusals + CLI exit codes.

Loaded the same way as the sibling script tests: importlib from ROOT/scripts.

imports stdlib: importlib.util, json, pathlib.Path, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
PLANTED_FIXTURE = 'def build_report(title, author, date, body, footer, theme, locale):\n return title + a...
PLANTED_SMELL = 'long-parameter-list'
REQUIRED_SMELLS = ('long-method', 'large-class', 'duplicated-code', 'feature-envy', 'data-clumps', 'primi...
```

- [load](load.md) function: HOLE: no docstring
- [_smell](_smell.md) function: HOLE: no docstring
- [_all_absent](_all_absent.md) function: A complete, valid pass where every baseline smell is absent.
- [_with](_with.md) function: The full baseline with one smell's entry overridden by `overrides`.
- [_record](_record.md) function: HOLE: no docstring
- [VisitEverySmellTests](VisitEverySmellTests.md) class: Every baseline smell must carry a verdict — the pass can't be silently skipped.
  - [VisitEverySmellTests.setUp](VisitEverySmellTests.setUp.md) method: HOLE: no docstring
  - [VisitEverySmellTests.test_complete_pass_passes](VisitEverySmellTests.test_complete_pass_passes.md) method: HOLE: no docstring
  - [VisitEverySmellTests.test_missing_smell_refused](VisitEverySmellTests.test_missing_smell_refused.md) method: HOLE: no docstring
  - [VisitEverySmellTests.test_unknown_smell_refused](VisitEverySmellTests.test_unknown_smell_refused.md) method: HOLE: no docstring
  - [VisitEverySmellTests.test_duplicate_smell_refused](VisitEverySmellTests.test_duplicate_smell_refused.md) method: HOLE: no docstring
  - [VisitEverySmellTests.test_bad_verdict_refused](VisitEverySmellTests.test_bad_verdict_refused.md) method: HOLE: no docstring
- [PlantedSmellTests](PlantedSmellTests.md) class: A fixture with an obvious Fowler smell is surfaced by the pass.
  - [PlantedSmellTests.setUp](PlantedSmellTests.setUp.md) method: HOLE: no docstring
  - [PlantedSmellTests.test_planted_smell_flagged_passes_and_surfaces](PlantedSmellTests.test_planted_smell_flagged_passes_and_surfaces.md) method: HOLE: no docstring
  - [PlantedSmellTests.test_flagged_smell_without_finding_refused](PlantedSmellTests.test_flagged_smell_without_finding_refused.md) method: HOLE: no docstring
  - [PlantedSmellTests.test_dropping_the_planted_smell_is_refused](PlantedSmellTests.test_dropping_the_planted_smell_is_refused.md) method: HOLE: no docstring
- [OverrideLogTests](OverrideLogTests.md) class: A smell subordinate to a documented repo standard is honored only when logged.
  - [OverrideLogTests.setUp](OverrideLogTests.setUp.md) method: HOLE: no docstring
  - [OverrideLogTests.test_override_with_logged_reason_honored](OverrideLogTests.test_override_with_logged_reason_honored.md) method: HOLE: no docstring
  - [OverrideLogTests.test_override_without_logged_reason_refused](OverrideLogTests.test_override_without_logged_reason_refused.md) method: HOLE: no docstring
  - [OverrideLogTests.test_override_missing_standard_refused](OverrideLogTests.test_override_missing_standard_refused.md) method: HOLE: no docstring
  - [OverrideLogTests.test_override_missing_reason_refused](OverrideLogTests.test_override_missing_reason_refused.md) method: HOLE: no docstring
- [RailExceptionTests](RailExceptionTests.md) class: Skipping the whole pass needs an independent reviewer's co-sign + log.
  - [RailExceptionTests.setUp](RailExceptionTests.setUp.md) method: HOLE: no docstring
  - [RailExceptionTests.test_reviewer_cosigned_whole_pass_skip_passes](RailExceptionTests.test_reviewer_cosigned_whole_pass_skip_passes.md) method: HOLE: no docstring
  - [RailExceptionTests.test_self_asserted_whole_pass_skip_refused](RailExceptionTests.test_self_asserted_whole_pass_skip_refused.md) method: HOLE: no docstring
  - [RailExceptionTests.test_exception_does_not_excuse_a_single_unlogged_override](RailExceptionTests.test_exception_does_not_excuse_a_single_unlogged_override.md) method: HOLE: no docstring
- [StructureTests](StructureTests.md) class: HOLE: no docstring
  - [StructureTests.setUp](StructureTests.setUp.md) method: HOLE: no docstring
  - [StructureTests.test_empty_diff_ref_refused](StructureTests.test_empty_diff_ref_refused.md) method: HOLE: no docstring
  - [StructureTests.test_no_smells_refused](StructureTests.test_no_smells_refused.md) method: HOLE: no docstring
  - [StructureTests.test_non_object_refused](StructureTests.test_non_object_refused.md) method: HOLE: no docstring
  - [StructureTests.test_absent_needs_no_finding_or_override](StructureTests.test_absent_needs_no_finding_or_override.md) method: HOLE: no docstring
  - [StructureTests.test_shipped_template_clears_the_rail](StructureTests.test_shipped_template_clears_the_rail.md) method: HOLE: no docstring
  - [StructureTests.test_cli_refuses_unlogged_override_nonzero](StructureTests.test_cli_refuses_unlogged_override_nonzero.md) method: HOLE: no docstring
  - [StructureTests.test_cli_accepts_complete_pass_zero](StructureTests.test_cli_accepts_complete_pass_zero.md) method: HOLE: no docstring
