# tests.test_grade_lint
tests/test_grade_lint.py, 509 lines, 35 holes

Tests for scripts/grade_lint.py — the @grade: inline-tag linter (issue #230,

epic-226).

Covers the 13 required tests from the g1-implement handoff: the 4 named by the
issue (ungraded FAIL, guess-missing-settle FAIL, dangling-leans FAIL, clean PASS)
plus 9 added by a cold-critic review (prose-is-not-a-decision, the preflight/
execute mode fork, positive leans resolution, the fence regression, multi-path
GL012 file-scoping, the JSON structural walk, --strict-warnings, exit code 2,
and the template round-trip against the real shipped files).

Fixtures are built as REAL Markdown/JSON decision blocks in the exact shape the
shipped templates emit (a real '## Pre-Rulings' heading with real list-item
bullets, a real EXECUTE_PLAN-shaped JSON) rather than hand-simplified stand-ins,
per the fixture-design rule in the handoff.

imports stdlib: contextlib.redirect_stdout, importlib.util, io.StringIO, json, pathlib.Path, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
SHIPPED_TEMPLATES = [ROOT / 'skills' / 'admiral' / 'templates' / 'LATITUDE_CONTRACT.template.md', ROOT / 's...
```

- [_load](_load.md) function: HOLE: no docstring
- [_run](_run.md) function: Call main(argv) capturing stdout; return (exit_code, stdout_text).
- [_write](_write.md) function: HOLE: no docstring
- [GradeLintCoreTests](GradeLintCoreTests.md) class: Tests 1-8: the four issue-named cases plus the cold-critic additions that
  - [GradeLintCoreTests.setUp](GradeLintCoreTests.setUp.md) method: HOLE: no docstring
  - [GradeLintCoreTests.tearDown](GradeLintCoreTests.tearDown.md) method: HOLE: no docstring
  - [GradeLintCoreTests.test_ungraded_decision_fails_preflight](GradeLintCoreTests.test_ungraded_decision_fails_preflight.md) method: HOLE: no docstring
  - [GradeLintCoreTests.test_guess_without_settle_fails](GradeLintCoreTests.test_guess_without_settle_fails.md) method: HOLE: no docstring
  - [GradeLintCoreTests.test_dangling_lean_fails](GradeLintCoreTests.test_dangling_lean_fails.md) method: HOLE: no docstring
  - [GradeLintCoreTests.test_clean_plan_passes](GradeLintCoreTests.test_clean_plan_passes.md) method: HOLE: no docstring
  - [GradeLintCoreTests.test_prose_is_not_a_decision](GradeLintCoreTests.test_prose_is_not_a_decision.md) method: HOLE: no docstring
  - [GradeLintCoreTests.test_execute_mode_suppresses_gl001](GradeLintCoreTests.test_execute_mode_suppresses_gl001.md) method: HOLE: no docstring
  - [GradeLintCoreTests.test_positive_leans_resolution](GradeLintCoreTests.test_positive_leans_resolution.md) method: HOLE: no docstring
  - [GradeLintCoreTests.test_fence_regression](GradeLintCoreTests.test_fence_regression.md) method: HOLE: no docstring
- [GradeLintMultiFileAndJsonTests](GradeLintMultiFileAndJsonTests.md) class: HOLE: no docstring
  - [GradeLintMultiFileAndJsonTests.setUp](GradeLintMultiFileAndJsonTests.setUp.md) method: HOLE: no docstring
  - [GradeLintMultiFileAndJsonTests.tearDown](GradeLintMultiFileAndJsonTests.tearDown.md) method: HOLE: no docstring
  - [GradeLintMultiFileAndJsonTests.test_gl012_scoped_per_file_not_across_files](GradeLintMultiFileAndJsonTests.test_gl012_scoped_per_file_not_across_files.md) method: HOLE: no docstring
  - [GradeLintMultiFileAndJsonTests.test_json_structural_walk](GradeLintMultiFileAndJsonTests.test_json_structural_walk.md) method: HOLE: no docstring
- [GradeLintCliFlagsTests](GradeLintCliFlagsTests.md) class: HOLE: no docstring
  - [GradeLintCliFlagsTests.setUp](GradeLintCliFlagsTests.setUp.md) method: HOLE: no docstring
  - [GradeLintCliFlagsTests.tearDown](GradeLintCliFlagsTests.tearDown.md) method: HOLE: no docstring
  - [GradeLintCliFlagsTests.test_strict_warnings_flips_exit_code](GradeLintCliFlagsTests.test_strict_warnings_flips_exit_code.md) method: HOLE: no docstring
  - [GradeLintCliFlagsTests.test_exit_code_2_missing_file](GradeLintCliFlagsTests.test_exit_code_2_missing_file.md) method: HOLE: no docstring
  - [GradeLintCliFlagsTests.test_exit_code_2_invalid_json](GradeLintCliFlagsTests.test_exit_code_2_invalid_json.md) method: HOLE: no docstring
- [GradeLintTemplateRoundTripTests](GradeLintTemplateRoundTripTests.md) class: 13. Lint the REAL shipped files and assert exit 0. These files are edited
  - [GradeLintTemplateRoundTripTests.setUp](GradeLintTemplateRoundTripTests.setUp.md) method: HOLE: no docstring
  - [GradeLintTemplateRoundTripTests.test_shipped_templates_lint_clean](GradeLintTemplateRoundTripTests.test_shipped_templates_lint_clean.md) method: HOLE: no docstring
  - [GradeLintTemplateRoundTripTests.test_shipped_templates_lint_clean_combined](GradeLintTemplateRoundTripTests.test_shipped_templates_lint_clean_combined.md) method: HOLE: no docstring
  - [GradeLintTemplateRoundTripTests.test_shipped_templates_clean_under_strict_warnings](GradeLintTemplateRoundTripTests.test_shipped_templates_clean_under_strict_warnings.md) method: The templates carry a grade slot on their own placeholder bullets, so
- [GradeLintPlaceholderChildGradeTests](GradeLintPlaceholderChildGradeTests.md) class: Regression: a grade welded to a decision that was skipped as template
  - [GradeLintPlaceholderChildGradeTests.setUp](GradeLintPlaceholderChildGradeTests.setUp.md) method: HOLE: no docstring
  - [GradeLintPlaceholderChildGradeTests.tearDown](GradeLintPlaceholderChildGradeTests.tearDown.md) method: HOLE: no docstring
  - [GradeLintPlaceholderChildGradeTests.test_grade_under_placeholder_bullet_is_not_an_orphan](GradeLintPlaceholderChildGradeTests.test_grade_under_placeholder_bullet_is_not_an_orphan.md) method: HOLE: no docstring
  - [GradeLintPlaceholderChildGradeTests.test_real_orphan_grade_still_reported](GradeLintPlaceholderChildGradeTests.test_real_orphan_grade_still_reported.md) method: The fix must not blunt GL010 generally: a grade under a PROSE line
- [GradeLintReviewerRegressionTests](GradeLintReviewerRegressionTests.md) class: Two correctness bugs found by adversarial probing at review, fixed in
  - [GradeLintReviewerRegressionTests.setUp](GradeLintReviewerRegressionTests.setUp.md) method: HOLE: no docstring
  - [GradeLintReviewerRegressionTests.tearDown](GradeLintReviewerRegressionTests.tearDown.md) method: HOLE: no docstring
  - [GradeLintReviewerRegressionTests.test_two_bracket_spans_are_not_scaffolding](GradeLintReviewerRegressionTests.test_two_bracket_spans_are_not_scaffolding.md) method: A line starting with one angle-bracket span and ending with another
  - [GradeLintReviewerRegressionTests.test_true_placeholder_still_skipped](GradeLintReviewerRegressionTests.test_true_placeholder_still_skipped.md) method: The narrower rule must not break the placeholder skip the template
  - [GradeLintReviewerRegressionTests.test_nested_sub_bullet_is_elaboration_not_a_decision](GradeLintReviewerRegressionTests.test_nested_sub_bullet_is_elaboration_not_a_decision.md) method: A bullet indented under a graded decision elaborates it. Treating it
  - [GradeLintReviewerRegressionTests.test_sibling_bullet_at_same_indent_is_still_its_own_decision](GradeLintReviewerRegressionTests.test_sibling_bullet_at_same_indent_is_still_its_own_decision.md) method: The nesting rule keys on indentation, so a SIBLING bullet must still
- [GradeLintWrappedBulletTests](GradeLintWrappedBulletTests.md) class: Human ruling, issue #239 item 3: "wrapped bullets should be invalid and
  - [GradeLintWrappedBulletTests.setUp](GradeLintWrappedBulletTests.setUp.md) method: HOLE: no docstring
  - [GradeLintWrappedBulletTests.tearDown](GradeLintWrappedBulletTests.tearDown.md) method: HOLE: no docstring
  - [GradeLintWrappedBulletTests.test_wrapped_bullet_reports_gl013_not_gl001_gl010](GradeLintWrappedBulletTests.test_wrapped_bullet_reports_gl013_not_gl001_gl010.md) method: HOLE: no docstring
  - [GradeLintWrappedBulletTests.test_normal_welded_bullet_still_passes_clean](GradeLintWrappedBulletTests.test_normal_welded_bullet_still_passes_clean.md) method: HOLE: no docstring
  - [GradeLintWrappedBulletTests.test_truly_ungraded_decision_still_gives_gl001](GradeLintWrappedBulletTests.test_truly_ungraded_decision_still_gives_gl001.md) method: A decision with no @grade anywhere nearby is the plain GL001 case,
  - [GradeLintWrappedBulletTests.test_truly_orphaned_tag_still_gives_gl010](GradeLintWrappedBulletTests.test_truly_orphaned_tag_still_gives_gl010.md) method: A @grade tag with no decision bullet anywhere near it (only prose)
  - [GradeLintWrappedBulletTests.test_shipped_templates_lint_clean_under_strict_warnings](GradeLintWrappedBulletTests.test_shipped_templates_lint_clean_under_strict_warnings.md) method: Regression guard named by the handoff: the wrapped-bullet diagnostic
