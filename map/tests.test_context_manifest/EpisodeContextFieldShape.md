# tests.test_context_manifest:EpisodeContextFieldShape
class, tests/test_context_manifest.py:1076, 52 lines

```python
class EpisodeContextFieldShape(TestCase)
```

The manifest must be assignable to an episode `context` field with **no

transformation** — a plain JSON value the caller can store as-is. This is a
test-after/inspection check: it exercises the real producer end to end and
makes the property explicit, rather than trusting it as an implied side
effect of the other tests.

- [test_produced_manifest_is_assignable_to_episode_context_field_untransformed](EpisodeContextFieldShape.test_produced_manifest_is_assignable_to_episode_context_field_untransformed.md) method: HOLE: no docstring

referenced by: none found
