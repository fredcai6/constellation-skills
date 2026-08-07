# tests.test_episode_store:LineBoundaryGuardTests
class, tests/test_episode_store.py:339, 74 lines

```python
class LineBoundaryGuardTests(EpisodeStoreTestCase)
```

REWORK (g2 review BLOCK, defect 1): _reject_newline() must reject every

character str.splitlines() treats as a line boundary, not just literal \n/\r --
parse_episode() sections the file with splitlines(), so any gap between the
guard's character set and splitlines()'s own definition is a silent-corruption
hole. Covers the reviewer's exact reproduction (U+2028) plus every other
splitlines() boundary character, the trailing-separator edge case, and one
end-to-end proof that the forged-status-line attack the guard exists to prevent
is actually rejected once it reaches the writer.

```python
BOUNDARY_CHARS = {'vertical-tab': '\x0b', 'form-feed': '\x0c', 'file-separator': '\x1c', 'group-separato...
```

- [test_reject_newline_unit_rejects_every_splitlines_boundary_character](LineBoundaryGuardTests.test_reject_newline_unit_rejects_every_splitlines_boundary_character.md) method: HOLE: no docstring
- [test_reject_newline_unit_rejects_trailing_separator](LineBoundaryGuardTests.test_reject_newline_unit_rejects_trailing_separator.md) method: HOLE: no docstring
- [test_reject_newline_unit_still_accepts_a_genuinely_single_line_value](LineBoundaryGuardTests.test_reject_newline_unit_still_accepts_a_genuinely_single_line_value.md) method: HOLE: no docstring
- [test_u2028_forged_status_line_end_to_end_create_rejected](LineBoundaryGuardTests.test_u2028_forged_status_line_end_to_end_create_rejected.md) method: HOLE: no docstring
- [test_u2028_forged_status_line_end_to_end_amend_history_rejected](LineBoundaryGuardTests.test_u2028_forged_status_line_end_to_end_amend_history_rejected.md) method: HOLE: no docstring

writes internal: LineBoundaryGuardTests.BOUNDARY_CHARS

referenced by: none found
