# tests.test_episode_store:NonForeclosureTests
class, tests/test_episode_store.py:1533, 140 lines

```python
class NonForeclosureTests(QueryTestCase)
```

C4 — the priority-1 obligation, exercised by retrieval.

EPISODE_STORE.md section 5's whole claim is that disputing one agent-supplied
assertion is a one-field, append-history mutation — never a record rewrite. "Never
rewritten" is a claim about BYTES, so it is checked in bytes: the file is read with
open(path, 'rb') before and after, with no decoding and no newline translation
anywhere in the comparison path, because Python's universal-newline handling would
happily make a CRLF and an LF file compare equal and hand back a false pass. (The
writer itself reads and writes with newline="" for the same reason.)

- [assertion_block](NonForeclosureTests.assertion_block.md) method: The exact bytes of one `### assertion:<id>.<aid>` block, from its heading up
- [test_disputing_one_assertion_leaves_its_siblings_byte_identical](NonForeclosureTests.test_disputing_one_assertion_leaves_its_siblings_byte_identical.md) method: HOLE: no docstring
- [test_the_mechanical_bin_and_retirement_block_are_untouched_by_a_dispute](NonForeclosureTests.test_the_mechanical_bin_and_retirement_block_are_untouched_by_a_dispute.md) method: HOLE: no docstring
- [test_a_disputed_episode_is_still_retrievable_and_reports_its_standing](NonForeclosureTests.test_a_disputed_episode_is_still_retrievable_and_reports_its_standing.md) method: HOLE: no docstring

reads stdlib: builtins.bytes x2, builtins.str x2

referenced by: none found
