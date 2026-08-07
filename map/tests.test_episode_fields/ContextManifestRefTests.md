# tests.test_episode_fields:ContextManifestRefTests
class, tests/test_episode_fields.py:609, 49 lines

```python
class ContextManifestRefTests(TestCase)
```

`context-manifest-ref` is `<manifest-ref>@<revision>` per EPISODE_STORE.md §8,

where the revision pins the manifest's OWN blob hash at capture time. That is only
honest because g1's emit is write-if-absent: bytes that could be rewritten cannot
be pinned.

- [setUp](ContextManifestRefTests.setUp.md) method: HOLE: no docstring
- [tearDown](ContextManifestRefTests.tearDown.md) method: HOLE: no docstring
- [manifest](ContextManifestRefTests.manifest.md) method: HOLE: no docstring
- [test_ref_pins_the_manifests_own_blob_oid](ContextManifestRefTests.test_ref_pins_the_manifests_own_blob_oid.md) method: HOLE: no docstring
- [test_the_pin_equals_git_hash_object_on_that_exact_file](ContextManifestRefTests.test_the_pin_equals_git_hash_object_on_that_exact_file.md) method: HOLE: no docstring
- [test_the_pin_moves_when_the_manifest_bytes_move](ContextManifestRefTests.test_the_pin_moves_when_the_manifest_bytes_move.md) method: A pin that did not follow its own bytes would be a decoration.
- [test_ref_is_refused_when_no_manifest_was_taken](ContextManifestRefTests.test_ref_is_refused_when_no_manifest_was_taken.md) method: Never a plausible `ctx-<run>-<step>@` with an empty or invented revision.

calls stdlib: unittest.skipUnless
reads internal: GIT
reads stdlib: unittest (module)

referenced by: none found
