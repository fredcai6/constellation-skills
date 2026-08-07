# tests.test_verify_worktree_isolation
tests/test_verify_worktree_isolation.py, 216 lines, 36 holes

HOLE: no docstring

imports stdlib: importlib.util, os, pathlib.Path, shutil, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
PORCELAIN = 'worktree C:/Programs/main\nHEAD abc123\nbranch refs/heads/main\n\nworktree C:/Programs...
HAS_GIT = shutil.which('git') is not None
```

- [load](load.md) function: HOLE: no docstring
- [NormalizeTests](NormalizeTests.md) class: HOLE: no docstring
  - [NormalizeTests.setUp](NormalizeTests.setUp.md) method: HOLE: no docstring
  - [NormalizeTests.test_separator_and_case_fold_equal_on_windows](NormalizeTests.test_separator_and_case_fold_equal_on_windows.md) method: HOLE: no docstring
  - [NormalizeTests.test_dot_segments_folded](NormalizeTests.test_dot_segments_folded.md) method: HOLE: no docstring
  - [NormalizeTests.test_symlink_or_junction_resolved](NormalizeTests.test_symlink_or_junction_resolved.md) method: HOLE: no docstring
- [ParseTests](ParseTests.md) class: HOLE: no docstring
  - [ParseTests.setUp](ParseTests.setUp.md) method: HOLE: no docstring
  - [ParseTests.test_extracts_only_worktree_paths](ParseTests.test_extracts_only_worktree_paths.md) method: HOLE: no docstring
  - [ParseTests.test_empty_input_is_empty_list](ParseTests.test_empty_input_is_empty_list.md) method: HOLE: no docstring
- [CheckDistinctRealTests](CheckDistinctRealTests.md) class: HOLE: no docstring
  - [CheckDistinctRealTests.setUp](CheckDistinctRealTests.setUp.md) method: HOLE: no docstring
  - [CheckDistinctRealTests.test_distinct_registered_nonprimary_pass](CheckDistinctRealTests.test_distinct_registered_nonprimary_pass.md) method: HOLE: no docstring
  - [CheckDistinctRealTests.test_unregistered_path_fails](CheckDistinctRealTests.test_unregistered_path_fails.md) method: HOLE: no docstring
  - [CheckDistinctRealTests.test_primary_checkout_rejected](CheckDistinctRealTests.test_primary_checkout_rejected.md) method: HOLE: no docstring
  - [CheckDistinctRealTests.test_duplicate_provisioned_paths_fail](CheckDistinctRealTests.test_duplicate_provisioned_paths_fail.md) method: HOLE: no docstring
- [CheckHereTests](CheckHereTests.md) class: HOLE: no docstring
  - [CheckHereTests.setUp](CheckHereTests.setUp.md) method: HOLE: no docstring
  - [CheckHereTests.test_match_passes](CheckHereTests.test_match_passes.md) method: HOLE: no docstring
  - [CheckHereTests.test_mismatch_names_both](CheckHereTests.test_mismatch_names_both.md) method: HOLE: no docstring
- [IntegrationTests](IntegrationTests.md) class: HOLE: no docstring
  - [IntegrationTests.setUp](IntegrationTests.setUp.md) method: HOLE: no docstring
  - [IntegrationTests.tearDown](IntegrationTests.tearDown.md) method: HOLE: no docstring
  - [IntegrationTests._git](IntegrationTests._git.md) method: HOLE: no docstring
  - [IntegrationTests.test_gate_passes_for_real_worktree](IntegrationTests.test_gate_passes_for_real_worktree.md) method: HOLE: no docstring
  - [IntegrationTests.test_gate_rejects_main_checkout](IntegrationTests.test_gate_rejects_main_checkout.md) method: HOLE: no docstring
  - [IntegrationTests.test_gate_rejects_missing_path](IntegrationTests.test_gate_rejects_missing_path.md) method: HOLE: no docstring
  - [IntegrationTests.test_here_passes_from_inside_worktree](IntegrationTests.test_here_passes_from_inside_worktree.md) method: HOLE: no docstring
  - [IntegrationTests.test_here_fails_from_main_checkout](IntegrationTests.test_here_fails_from_main_checkout.md) method: HOLE: no docstring
- [CliErrorTests](CliErrorTests.md) class: HOLE: no docstring
  - [CliErrorTests.setUp](CliErrorTests.setUp.md) method: HOLE: no docstring
  - [CliErrorTests.test_here_with_positional_paths_is_usage_error](CliErrorTests.test_here_with_positional_paths_is_usage_error.md) method: HOLE: no docstring
- [GitFailureTests](GitFailureTests.md) class: HOLE: no docstring
  - [GitFailureTests.setUp](GitFailureTests.setUp.md) method: HOLE: no docstring
  - [GitFailureTests.tearDown](GitFailureTests.tearDown.md) method: HOLE: no docstring
  - [GitFailureTests.test_gate_outside_git_repo_returns_1_not_crash](GitFailureTests.test_gate_outside_git_repo_returns_1_not_crash.md) method: HOLE: no docstring
