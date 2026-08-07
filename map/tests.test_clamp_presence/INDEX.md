# tests.test_clamp_presence
tests/test_clamp_presence.py, 105 lines, 3 holes

Presence test for issue #142 clamp restoration.

Asserts the transcription-grade four-clause completion doctrine, or the
verbatim pointer-with-force sentence, is present in each target skill file so
the #101 stripping defect (bare pointer with no load-time force) cannot
silently recur. Substring checks only -- this does not judge quality, only
that the required wording exists.

imports stdlib: pathlib.Path, sys
imported by: none found

```python
REPO = Path(__file__).resolve().parents[1]
FOUR_CLAUSE_KEYPHRASES = ['Start here — drive the engine before you touch', 'This is your **first command**', 'i...
FULL_CLAUSE_TARGETS = ['skills/implementer/SKILL.md', 'skills/reviewer/SKILL.md', 'skills/commander/reference...
POINTER_SENTENCE = 'Drive every step through the checklist engine and finish its sequence — final `advance...
POINTER_ONLY_TARGETS = ['skills/cartographer/SKILL.md', 'skills/charter/SKILL.md', 'skills/curator/SKILL.md', ...
RAIL_CITATION_MARKER = 'canonical enforcement source'
```

- [check_full_clause](check_full_clause.md) function: HOLE: no docstring
- [check_pointer_only](check_pointer_only.md) function: HOLE: no docstring
- [main](main.md) function: HOLE: no docstring
