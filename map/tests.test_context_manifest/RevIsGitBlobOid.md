# tests.test_context_manifest:RevIsGitBlobOid
class, tests/test_context_manifest.py:48, 167 lines

```python
class RevIsGitBlobOid(TestCase)
```

`rev` is the git blob OID of the LF-normalised bytes, computed in-process.

No `git` subprocess in production code; the subprocess here is the *oracle*
the implementation is measured against.

```python
TARGETS = ['scripts/checklist_engine.py', 'scripts/agent_work_root.py', 'skills/commander/templat...
```

- [_git](RevIsGitBlobOid._git.md) method: HOLE: no docstring
- [test_rev_equals_git_hash_object_for_real_tracked_files](RevIsGitBlobOid.test_rev_equals_git_hash_object_for_real_tracked_files.md) method: HOLE: no docstring
- [test_rev_equals_git_rev_parse_head_for_tracked_clean_files](RevIsGitBlobOid.test_rev_equals_git_rev_parse_head_for_tracked_clean_files.md) method: HOLE: no docstring
- [test_rev_of_crlf_and_lf_twins_is_identical](RevIsGitBlobOid.test_rev_of_crlf_and_lf_twins_is_identical.md) method: HOLE: no docstring
- [test_rev_crlf_twin_written_to_disk_matches_git_hash_object](RevIsGitBlobOid.test_rev_crlf_twin_written_to_disk_matches_git_hash_object.md) method: HOLE: no docstring
- [_raw_blob_oid](RevIsGitBlobOid._raw_blob_oid.md) method: Git's blob OID of exactly these bytes, with no normalisation. The second
- [test_rev_diverges_from_git_for_content_git_refuses_to_normalise](RevIsGitBlobOid.test_rev_diverges_from_git_for_content_git_refuses_to_normalise.md) method: HOLE: no docstring
- [test_gitattributes_exempts_no_path_from_lf_normalisation](RevIsGitBlobOid.test_gitattributes_exempts_no_path_from_lf_normalisation.md) method: HOLE: no docstring
- [test_rev_of_empty_bytes_is_the_git_empty_blob](RevIsGitBlobOid.test_rev_of_empty_bytes_is_the_git_empty_blob.md) method: HOLE: no docstring
- [test_rev_is_sensitive_to_content_change](RevIsGitBlobOid.test_rev_is_sensitive_to_content_change.md) method: HOLE: no docstring

writes internal: RevIsGitBlobOid.TARGETS

referenced by: none found
