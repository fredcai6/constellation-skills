# tests.test_episode_store:SilentOmissionTests
class, tests/test_episode_store.py:987, 101 lines

```python
class SilentOmissionTests(QueryTestCase)
```

The failure mode this store's whole design fears: not a crash, not an error — a

candidate set one record short, with nothing anywhere signalling that it is short.

Each test here runs a NAIVE implementation and the real primitive over the SAME
adversarial store and asserts the naive one omits. A round-trip over well-formed
input would prove nothing (lesson:round-trip-tests-prove-artifacts-not-parsers);
the input has to be built to make the naive answer wrong.

```python
TARGET = 'docs/EPISODE_STORE.md'
```

- [seed_ref_position_fixture](SilentOmissionTests.seed_ref_position_fixture.md) method: Three episodes that all genuinely carry TARGET as an artifact-ref — first,
- [test_naive_dict_collapse_silently_omits_two_of_three_matching_episodes](SilentOmissionTests.test_naive_dict_collapse_silently_omits_two_of_three_matching_episodes.md) method: HOLE: no docstring
- [test_field_values_returns_every_artifact_ref_not_just_the_last](SilentOmissionTests.test_field_values_returns_every_artifact_ref_not_just_the_last.md) method: HOLE: no docstring
- [test_a_bare_string_is_refused_rather_than_matched_character_by_character](SilentOmissionTests.test_a_bare_string_is_refused_rather_than_matched_character_by_character.md) method: HOLE: no docstring
- [test_enumeration_returns_every_episode_including_ones_a_run_glob_would_miss](SilentOmissionTests.test_enumeration_returns_every_episode_including_ones_a_run_glob_would_miss.md) method: HOLE: no docstring
- [test_a_scanned_id_that_no_longer_resolves_is_raised_not_dropped](SilentOmissionTests.test_a_scanned_id_that_no_longer_resolves_is_raised_not_dropped.md) method: A third shape, found by sweeping for the class rather than by a review note.

writes internal: SilentOmissionTests.TARGET

referenced by: none found
