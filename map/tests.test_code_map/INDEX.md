# tests.test_code_map
tests/test_code_map.py, 215 lines, 18 holes

Tests for scripts/code_map/ — the derived code map (issue #456, gate g0).

Gate g0 introduces exactly two behaviors of its own: the discovery layer that
enumerates the **mappable corpus**, and the argparse CLI. Those two are
test-first. The three pipeline stages (extract, supplement, render) are a port
of the reference prototype and are covered by end-to-end evidence, not by unit
tests that would freeze prototype behavior gates g2/g3 are going to change.

`mappable corpus` is the set of source files the map is derived FROM. It is not
the skills `corpus` of docs/agents/GLOSSARY.md — different thing, same English
word; the code says `mappable corpus` wherever the distinction matters.

The exclusion tests are the load-bearing ones: `.agent-work/` is deliberately
TRACKED in this repo, so `git ls-files` alone does not exclude it, and letting
it into the corpus makes roughly a third of the map run scratch. Each exclusion
test asserts that the thing being excluded was actually PRESENT in the input —
a filter test over an input with nothing to filter passes without ever
exercising the filter.

imports stdlib: contextlib, io, pathlib.Path, subprocess, sys, tempfile, unittest
imports internal: scripts.code_map.cli:, scripts.code_map.discovery:
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
```

- [_git](_git.md) function: HOLE: no docstring
- [_make_repo](_make_repo.md) function: A synthetic git repo whose tracked set spans every case the filter sees:
- [DiscoveryTests](DiscoveryTests.md) class: The discovery layer, against a synthetic repo — hermetic, so these do not
  - [DiscoveryTests.setUp](DiscoveryTests.setUp.md) method: HOLE: no docstring
  - [DiscoveryTests.tearDown](DiscoveryTests.tearDown.md) method: HOLE: no docstring
  - [DiscoveryTests.test_discovery_excludes_agent_work](DiscoveryTests.test_discovery_excludes_agent_work.md) method: THE load-bearing one: remove the exclusion and this goes red.
  - [DiscoveryTests.test_discovery_excludes_untracked_and_non_python](DiscoveryTests.test_discovery_excludes_untracked_and_non_python.md) method: HOLE: no docstring
  - [DiscoveryTests.test_discovery_is_sorted_posix_relative_paths](DiscoveryTests.test_discovery_is_sorted_posix_relative_paths.md) method: HOLE: no docstring
  - [DiscoveryTests.test_discovery_predicate_and_listing_agree](DiscoveryTests.test_discovery_predicate_and_listing_agree.md) method: The corpus is defined by the predicate the module itself applies, not
- [DiscoveryOnThisRepoTests](DiscoveryOnThisRepoTests.md) class: One integration check against the real repo. It asserts the RULE, never a
  - [DiscoveryOnThisRepoTests.test_discovery_on_this_repo_excludes_agent_work](DiscoveryOnThisRepoTests.test_discovery_on_this_repo_excludes_agent_work.md) method: HOLE: no docstring
- [CliArgumentTests](CliArgumentTests.md) class: The CLI's argument handling — the second behavior gate g0 introduces.
  - [CliArgumentTests.test_cli_parses_every_pipeline_stage_as_a_subcommand](CliArgumentTests.test_cli_parses_every_pipeline_stage_as_a_subcommand.md) method: HOLE: no docstring
  - [CliArgumentTests.test_cli_root_defaults_to_the_repository_root](CliArgumentTests.test_cli_root_defaults_to_the_repository_root.md) method: HOLE: no docstring
  - [CliArgumentTests.test_cli_root_is_overridable](CliArgumentTests.test_cli_root_is_overridable.md) method: HOLE: no docstring
  - [CliArgumentTests.test_cli_rejects_an_unknown_subcommand](CliArgumentTests.test_cli_rejects_an_unknown_subcommand.md) method: HOLE: no docstring
  - [CliArgumentTests.test_cli_requires_a_subcommand](CliArgumentTests.test_cli_requires_a_subcommand.md) method: HOLE: no docstring
  - [CliArgumentTests.test_cli_artifacts_and_out_default_under_the_root](CliArgumentTests.test_cli_artifacts_and_out_default_under_the_root.md) method: HOLE: no docstring
- [CliDiscoverCommandTests](CliDiscoverCommandTests.md) class: `discover` is the discovery layer's caller — it is what keeps
  - [CliDiscoverCommandTests.setUp](CliDiscoverCommandTests.setUp.md) method: HOLE: no docstring
  - [CliDiscoverCommandTests.tearDown](CliDiscoverCommandTests.tearDown.md) method: HOLE: no docstring
  - [CliDiscoverCommandTests.test_cli_discover_prints_the_mappable_corpus_and_exits_zero](CliDiscoverCommandTests.test_cli_discover_prints_the_mappable_corpus_and_exits_zero.md) method: HOLE: no docstring
- [CliBuildCommandTests](CliBuildCommandTests.md) class: `build` is the whole pipeline's caller. This asserts that the three
  - [CliBuildCommandTests.setUp](CliBuildCommandTests.setUp.md) method: HOLE: no docstring
  - [CliBuildCommandTests.tearDown](CliBuildCommandTests.tearDown.md) method: HOLE: no docstring
  - [CliBuildCommandTests.test_cli_build_runs_every_stage_and_writes_the_page_tree](CliBuildCommandTests.test_cli_build_runs_every_stage_and_writes_the_page_tree.md) method: HOLE: no docstring
  - [CliBuildCommandTests.test_cli_build_maps_the_corpus_and_not_the_scratch](CliBuildCommandTests.test_cli_build_maps_the_corpus_and_not_the_scratch.md) method: The exclusion has to hold through the whole pipeline, not only at the
