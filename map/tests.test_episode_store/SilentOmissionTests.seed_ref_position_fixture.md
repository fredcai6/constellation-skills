# tests.test_episode_store:SilentOmissionTests.seed_ref_position_fixture
method, tests/test_episode_store.py:999, 8 lines

```python
def seed_ref_position_fixture(self)
```

Three episodes that all genuinely carry TARGET as an artifact-ref — first,

middle, and last in their respective lists. Every one of them is a correct
answer to "which episodes reference TARGET".

calls internal: QueryTestCase.seed x3
calls stdlib: builtins.sorted
reads internal: SilentOmissionTests.TARGET x3

referenced by: 1 sites, this module only
