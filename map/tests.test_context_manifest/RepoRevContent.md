# tests.test_context_manifest:RepoRevContent
class, tests/test_context_manifest.py:924, 150 lines

```python
class RepoRevContent(TestCase)
```

`repo_rev` -- Tommy's doctrine-version stamp (#300 g5): the repo revision,

admitted into `CONTENT_KEYS` (a fact about canon, not about the run
environment). The per-file blob OID (`rev`, tested above in `RevIsGitBlobOid`)
is untouched -- this is a second, coarser fact, not a replacement.

Split in rework 1 (BLOCKER-1): `repo_rev` in content carries `commit` only,
which is canon-determined (identical for any checkout of that commit). A
review proved the original placement (both `commit` and `dirty` inside
content) wrong: two checkouts at the same commit, delivering byte-identical
declared canon, disagreed on `repo_rev` solely because `git status
--porcelain` is repo-wide and picked up dirt on a file no declaration named.

`dirty` moved to the excluded `run` subtree then, and was removed outright in
#327 (#305 g4) once a real producing caller made its behaviour observable: it
is repo-wide, so what it reports is dominated by the run's own bookkeeping,
and it is computed before the manifest is written, so it reads its
predecessor's tree rather than its own. `test_dirty_appears_nowhere_in_the_manifest`
below is the guard on that removal; the `repo_state` fakes throughout this
class still SUPPLY the field, unchanged, because a consumer that ignores what
it is handed is exactly what is being asserted.

- [setUp](RepoRevContent.setUp.md) method: HOLE: no docstring
- [build](RepoRevContent.build.md) method: HOLE: no docstring
- [test_repo_rev_is_admitted_into_content_keys](RepoRevContent.test_repo_rev_is_admitted_into_content_keys.md) method: HOLE: no docstring
- [test_repo_rev_is_a_content_field_not_a_run_field](RepoRevContent.test_repo_rev_is_a_content_field_not_a_run_field.md) method: HOLE: no docstring
- [test_repo_rev_shape_is_exactly_commit](RepoRevContent.test_repo_rev_shape_is_exactly_commit.md) method: HOLE: no docstring
- [test_dirty_appears_nowhere_in_the_manifest](RepoRevContent.test_dirty_appears_nowhere_in_the_manifest.md) method: HOLE: no docstring
- [test_content_is_unaffected_by_dirty_when_commit_is_equal](RepoRevContent.test_content_is_unaffected_by_dirty_when_commit_is_equal.md) method: HOLE: no docstring
- [test_repo_rev_does_not_replace_the_per_file_blob_oid](RepoRevContent.test_repo_rev_does_not_replace_the_per_file_blob_oid.md) method: HOLE: no docstring
- [test_repo_state_is_injectable_as_the_second_impure_edge](RepoRevContent.test_repo_state_is_injectable_as_the_second_impure_edge.md) method: HOLE: no docstring
- [test_default_repo_state_on_a_non_git_directory_yields_no_commit](RepoRevContent.test_default_repo_state_on_a_non_git_directory_yields_no_commit.md) method: HOLE: no docstring
- [test_default_repo_state_with_no_repo_root_mapped_yields_no_commit](RepoRevContent.test_default_repo_state_with_no_repo_root_mapped_yields_no_commit.md) method: HOLE: no docstring
- [test_default_repo_state_against_the_real_repo_matches_the_commit_oracle](RepoRevContent.test_default_repo_state_against_the_real_repo_matches_the_commit_oracle.md) method: HOLE: no docstring
- [test_repo_rev_survives_json_round_trip_untransformed](RepoRevContent.test_repo_rev_survives_json_round_trip_untransformed.md) method: HOLE: no docstring
- [test_doctrine_version_is_the_repo_rev_field](RepoRevContent.test_doctrine_version_is_the_repo_rev_field.md) method: HOLE: no docstring

referenced by: none found
