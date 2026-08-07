# tests.test_episode_store:RatifiedLayoutTests
class, tests/test_episode_store.py:1741, 52 lines

```python
class RatifiedLayoutTests(EpisodeStoreTestCase)
```

g4 — the retirement layout is RATIFIED and BOUND. Tommy's ruling, verbatim:

"move the file, prefer to keep files clean of history unless they're
    historical. archives are available strats."

So retirement MOVES the file: episodes/active/<id>.md -> episodes/retired/<id>.md
(EPISODE_STORE.md section 7, Option A). Option B — a `status` field filtered
negatively, with the file never moving — is rejected, and its adapters are gone.
These tests assert the BOUND behavior directly, with no adapter switch to flip,
because there is no longer a switch: a second adapter would re-open a decision the
human has closed.

- [test_a_new_episode_is_written_under_active](RatifiedLayoutTests.test_a_new_episode_is_written_under_active.md) method: HOLE: no docstring
- [test_retiring_moves_the_file_into_retired](RatifiedLayoutTests.test_retiring_moves_the_file_into_retired.md) method: HOLE: no docstring
- [test_the_layout_adapter_switch_is_gone](RatifiedLayoutTests.test_the_layout_adapter_switch_is_gone.md) method: HOLE: no docstring
- [test_membership_is_a_directory_fact_not_a_parsed_field](RatifiedLayoutTests.test_membership_is_a_directory_fact_not_a_parsed_field.md) method: HOLE: no docstring

referenced by: none found
