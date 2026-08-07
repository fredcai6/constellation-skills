# tests.test_checklist_engine:TestGlobToRegex
class, tests/test_checklist_engine.py:4366, 95 lines

```python
class TestGlobToRegex(TestCase)
```

Direct tests of `_glob_to_regex` (scripts/checklist_engine.py:449), which

had zero direct coverage before this class (only reached indirectly through
`_glob_match`, which layers a different concern -- basename fallback -- on
top). `_glob_to_regex` itself is frozen this run; every assertion here
exercises the returned regex string's *matching behavior* via `re.match`
against representative subjects, not a string-diff against a hand-derived
regex literal (which would be brittle to harmless reformatting of the
implementation's regex-building).

- [test_glob_to_regex_literal_chars_are_escaped](TestGlobToRegex.test_glob_to_regex_literal_chars_are_escaped.md) method: HOLE: no docstring
- [test_glob_to_regex_single_star_matches_within_segment_only](TestGlobToRegex.test_glob_to_regex_single_star_matches_within_segment_only.md) method: HOLE: no docstring
- [test_glob_to_regex_double_star_crosses_segments](TestGlobToRegex.test_glob_to_regex_double_star_crosses_segments.md) method: HOLE: no docstring
- [test_glob_to_regex_leading_double_star_slash_matches_zero_or_more_leading_segments](TestGlobToRegex.test_glob_to_regex_leading_double_star_slash_matches_zero_or_more_leading_segments.md) method: HOLE: no docstring
- [test_glob_to_regex_trailing_slash_double_star_also_matches_directory_itself](TestGlobToRegex.test_glob_to_regex_trailing_slash_double_star_also_matches_directory_itself.md) method: HOLE: no docstring
- [test_glob_to_regex_question_mark_matches_exactly_one_non_separator_char](TestGlobToRegex.test_glob_to_regex_question_mark_matches_exactly_one_non_separator_char.md) method: HOLE: no docstring
- [test_glob_to_regex_empty_pattern_matches_only_empty_string](TestGlobToRegex.test_glob_to_regex_empty_pattern_matches_only_empty_string.md) method: HOLE: no docstring
- [test_glob_to_regex_anchoring_requires_full_string_match](TestGlobToRegex.test_glob_to_regex_anchoring_requires_full_string_match.md) method: HOLE: no docstring
- [test_glob_to_regex_path_separator_is_literal](TestGlobToRegex.test_glob_to_regex_path_separator_is_literal.md) method: HOLE: no docstring

referenced by: none found
