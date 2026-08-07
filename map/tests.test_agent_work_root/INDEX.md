# tests.test_agent_work_root
tests/test_agent_work_root.py, 372 lines, 40 holes

Tests for the durable-root resolution helper and its wiring into the four

recursive-improvement scripts.

`durable_root(start)` returns the MAIN checkout root only when `start` sits inside
a LINKED git worktree; a plain checkout, a non-git dir, or any git error must
return `start` (or cwd) unchanged. The git-topology tests spin up a real
`git worktree add` in a tmpdir and skip cleanly when git is unavailable.

imports stdlib: importlib.util, json, os, pathlib.Path, shutil, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
GIT = shutil.which('git')
```

- [_load](_load.md) function: HOLE: no docstring
- [_norm](_norm.md) function: HOLE: no docstring
- [_git](_git.md) function: HOLE: no docstring
- [_init_repo](_init_repo.md) function: A git repo with one commit, so `git worktree add` has a valid HEAD.
- [_write_lease](_write_lease.md) function: Simulate an epic lease: `<main>/.agent-work/<epic>/spine.json` carrying an
- [DurableRootGitTests](DurableRootGitTests.md) class: HOLE: no docstring
  - [DurableRootGitTests.setUp](DurableRootGitTests.setUp.md) method: HOLE: no docstring
  - [DurableRootGitTests.tearDown](DurableRootGitTests.tearDown.md) method: HOLE: no docstring
  - [DurableRootGitTests.test_linked_worktree_resolves_to_main_checkout](DurableRootGitTests.test_linked_worktree_resolves_to_main_checkout.md) method: HOLE: no docstring
  - [DurableRootGitTests.test_durable_agent_work_appends_agent_work](DurableRootGitTests.test_durable_agent_work_appends_agent_work.md) method: HOLE: no docstring
  - [DurableRootGitTests.test_plain_checkout_unchanged](DurableRootGitTests.test_plain_checkout_unchanged.md) method: HOLE: no docstring
- [DurableRootEpicLeaseTests](DurableRootEpicLeaseTests.md) class: Under an ACTIVE Admiral epic lease in the main checkout, `durable_root`
  - [DurableRootEpicLeaseTests.setUp](DurableRootEpicLeaseTests.setUp.md) method: HOLE: no docstring
  - [DurableRootEpicLeaseTests.tearDown](DurableRootEpicLeaseTests.tearDown.md) method: HOLE: no docstring
  - [DurableRootEpicLeaseTests.test_active_admiral_lease_resolves_to_worktree](DurableRootEpicLeaseTests.test_active_admiral_lease_resolves_to_worktree.md) method: HOLE: no docstring
  - [DurableRootEpicLeaseTests.test_active_explorer_lease_resolves_to_main](DurableRootEpicLeaseTests.test_active_explorer_lease_resolves_to_main.md) method: HOLE: no docstring
  - [DurableRootEpicLeaseTests.test_released_admiral_lease_resolves_to_main](DurableRootEpicLeaseTests.test_released_admiral_lease_resolves_to_main.md) method: HOLE: no docstring
  - [DurableRootEpicLeaseTests.test_no_lease_resolves_to_main](DurableRootEpicLeaseTests.test_no_lease_resolves_to_main.md) method: HOLE: no docstring
  - [DurableRootEpicLeaseTests.test_malformed_spine_does_not_raise_and_resolves_to_main](DurableRootEpicLeaseTests.test_malformed_spine_does_not_raise_and_resolves_to_main.md) method: HOLE: no docstring
  - [DurableRootEpicLeaseTests.test_verify_agent_feedback_resolves_to_worktree_under_lease](DurableRootEpicLeaseTests.test_verify_agent_feedback_resolves_to_worktree_under_lease.md) method: HOLE: no docstring
- [DurableRootFallbackTests](DurableRootFallbackTests.md) class: HOLE: no docstring
  - [DurableRootFallbackTests.setUp](DurableRootFallbackTests.setUp.md) method: HOLE: no docstring
  - [DurableRootFallbackTests.tearDown](DurableRootFallbackTests.tearDown.md) method: HOLE: no docstring
  - [DurableRootFallbackTests.test_non_git_dir_unchanged](DurableRootFallbackTests.test_non_git_dir_unchanged.md) method: HOLE: no docstring
  - [DurableRootFallbackTests.test_nonexistent_start_returns_verbatim](DurableRootFallbackTests.test_nonexistent_start_returns_verbatim.md) method: HOLE: no docstring
  - [DurableRootFallbackTests.test_git_rev_parse_failure_falls_back](DurableRootFallbackTests.test_git_rev_parse_failure_falls_back.md) method: HOLE: no docstring
    - [DurableRootFallbackTests.test_git_rev_parse_failure_falls_back.boom](DurableRootFallbackTests.test_git_rev_parse_failure_falls_back.boom.md) method: HOLE: no docstring
  - [DurableRootFallbackTests.test_no_start_returns_cwd](DurableRootFallbackTests.test_no_start_returns_cwd.md) method: HOLE: no docstring
- [WiringExplicitWinsTests](WiringExplicitWinsTests.md) class: Explicit path args must ALWAYS win; the durable helper is consulted only
  - [WiringExplicitWinsTests.setUp](WiringExplicitWinsTests.setUp.md) method: HOLE: no docstring
  - [WiringExplicitWinsTests.tearDown](WiringExplicitWinsTests.tearDown.md) method: HOLE: no docstring
  - [WiringExplicitWinsTests._poison](WiringExplicitWinsTests._poison.md) static method: HOLE: no docstring
    - [WiringExplicitWinsTests._poison.boom](WiringExplicitWinsTests._poison.boom.md) method: HOLE: no docstring
  - [WiringExplicitWinsTests.test_apply_lessons_delta_explicit_file_wins](WiringExplicitWinsTests.test_apply_lessons_delta_explicit_file_wins.md) method: HOLE: no docstring
  - [WiringExplicitWinsTests.test_verify_lessons_applied_explicit_file_wins](WiringExplicitWinsTests.test_verify_lessons_applied_explicit_file_wins.md) method: HOLE: no docstring
  - [WiringExplicitWinsTests.test_verify_agent_feedback_explicit_root_wins_for_both](WiringExplicitWinsTests.test_verify_agent_feedback_explicit_root_wins_for_both.md) method: HOLE: no docstring
  - [WiringExplicitWinsTests.test_collect_feedback_explicit_inbox_wins](WiringExplicitWinsTests.test_collect_feedback_explicit_inbox_wins.md) method: HOLE: no docstring
- [WiringDefaultResolutionTests](WiringDefaultResolutionTests.md) class: When the explicit arg is omitted, the default path is computed through
  - [WiringDefaultResolutionTests.setUp](WiringDefaultResolutionTests.setUp.md) method: HOLE: no docstring
  - [WiringDefaultResolutionTests.tearDown](WiringDefaultResolutionTests.tearDown.md) method: HOLE: no docstring
  - [WiringDefaultResolutionTests._stub](WiringDefaultResolutionTests._stub.md) method: HOLE: no docstring
  - [WiringDefaultResolutionTests.test_apply_lessons_delta_default_uses_durable_root](WiringDefaultResolutionTests.test_apply_lessons_delta_default_uses_durable_root.md) method: HOLE: no docstring
  - [WiringDefaultResolutionTests.test_verify_lessons_applied_default_uses_durable_root](WiringDefaultResolutionTests.test_verify_lessons_applied_default_uses_durable_root.md) method: HOLE: no docstring
  - [WiringDefaultResolutionTests.test_verify_agent_feedback_default_durable_split](WiringDefaultResolutionTests.test_verify_agent_feedback_default_durable_split.md) method: HOLE: no docstring
  - [WiringDefaultResolutionTests.test_collect_feedback_default_inbox_uses_durable_root](WiringDefaultResolutionTests.test_collect_feedback_default_inbox_uses_durable_root.md) method: HOLE: no docstring
