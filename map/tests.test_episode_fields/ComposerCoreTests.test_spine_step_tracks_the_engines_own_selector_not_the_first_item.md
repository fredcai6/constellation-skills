# tests.test_episode_fields:ComposerCoreTests.test_spine_step_tracks_the_engines_own_selector_not_the_first_item
method, tests/test_episode_fields.py:214, 7 lines

```python
def test_spine_step_tracks_the_engines_own_selector_not_the_first_item(self)
```

The active step is the first NON-TERMINAL item. A composer that returned

`items[0]`, or any constant, gets this wrong the moment a run is underway.

calls internal: ComposerCoreTests.assertEqual x2, checklist x2
reads internal: ROOT x2, ec x2
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
