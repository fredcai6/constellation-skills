# tests.test_context_determinism
tests/test_context_determinism.py, 626 lines, 21 holes

The acceptance test for issue #300: the projection manifest's *content* is

identical across environments.

Construction: two clean `git worktree` checkouts of the same commit, at two
different absolute paths, each running the real producer in a child process with
different `LC_ALL`, `LANG` and `PYTHONHASHSEED`. The manifests' `run` subtrees are
expected to differ; everything else must be byte-identical.

**The exclusion set is exactly one JSON pointer, `/run`, and nothing else.** If a
field ever has to be masked to make this pass, that field is in the wrong subtree
and the *design* is wrong, not this test.

**Honest limit.** Same OS, same filesystem, same Python. This exercises path
ordering, locale and hash-ordering — the three things that actually vary between
two runs on one machine. It is NOT a cross-OS or cross-filesystem rebuild, and it
does not claim to be one.

**Why two fresh worktrees rather than this checkout versus one fresh worktree.**
The Commander declaration legitimately names paths that are untracked here and
absent in a clean checkout (`docs/agents/…`). Comparing this working checkout
against a fresh one would therefore compare two *different sets of delivered
bytes* — an honest difference in what was delivered, not a determinism failure —
and asserting byte-identity across it would be asserting something false. Two
clean checkouts of the same commit hold the delivered bytes fixed, which isolates
exactly the variables under test. `RealCheckoutSkew` below covers the
untracked-vs-absent case explicitly instead of hiding it.

**Windows trap** (`lesson:windows-subprocess-env-does-not-shadow-path-resolution`):
passing `env=` into `subprocess.run` does not change which executable an
unqualified name resolves to on Windows. The children are launched via
`sys.executable` (fully qualified), and — more importantly — each child *reports
back* the environment it actually saw, which this test asserts against. The
mutation is verified to have taken effect, never assumed.

imports stdlib: importlib.util, json, os, pathlib.Path, shutil, subprocess, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
cm = load('context_manifest')
OVERLAY = ('scripts/context_manifest.py', 'scripts/checklist_engine.py', 'skills/commander/templa...
INSTALL_SHIM = (('skills/_shared/global-orchestrator.md', 'skills/commander/references/global-orchestr...
CHILD = '\nimport importlib.util, json, os, sys\ncheckout = sys.argv[1]\nout = sys.argv[2]\ncon...
POISONS = {'environment_dependent_encoder': '\n\ndef encode(obj): # noqa: F811 - deliberately sha...
```

- [load](load.md) function: HOLE: no docstring
- [DeterministicAcrossEnvironments](DeterministicAcrossEnvironments.md) class: HOLE: no docstring
  - [DeterministicAcrossEnvironments.setUpClass](DeterministicAcrossEnvironments.setUpClass.md) class method: HOLE: no docstring
  - [DeterministicAcrossEnvironments.tearDownClass](DeterministicAcrossEnvironments.tearDownClass.md) class method: HOLE: no docstring
  - [DeterministicAcrossEnvironments._cleanup](DeterministicAcrossEnvironments._cleanup.md) class method: HOLE: no docstring
  - [DeterministicAcrossEnvironments.setUp](DeterministicAcrossEnvironments.setUp.md) method: HOLE: no docstring
  - [DeterministicAcrossEnvironments.test_the_two_environments_really_are_distinct](DeterministicAcrossEnvironments.test_the_two_environments_really_are_distinct.md) method: HOLE: no docstring
  - [DeterministicAcrossEnvironments.test_the_locale_and_hash_seed_mutations_took_effect_inside_the_child](DeterministicAcrossEnvironments.test_the_locale_and_hash_seed_mutations_took_effect_inside_the_child.md) method: HOLE: no docstring
  - [DeterministicAcrossEnvironments.test_content_is_byte_identical_excluding_exactly_the_run_subtree](DeterministicAcrossEnvironments.test_content_is_byte_identical_excluding_exactly_the_run_subtree.md) method: HOLE: no docstring
  - [DeterministicAcrossEnvironments.test_the_compared_bytes_are_the_ones_the_children_wrote](DeterministicAcrossEnvironments.test_the_compared_bytes_are_the_ones_the_children_wrote.md) method: HOLE: no docstring
  - [DeterministicAcrossEnvironments.test_the_run_subtrees_differ_so_the_exclusion_is_load_bearing](DeterministicAcrossEnvironments.test_the_run_subtrees_differ_so_the_exclusion_is_load_bearing.md) method: HOLE: no docstring
  - [DeterministicAcrossEnvironments.test_the_content_is_a_real_projection_not_an_empty_one](DeterministicAcrossEnvironments.test_the_content_is_a_real_projection_not_an_empty_one.md) method: HOLE: no docstring
  - [DeterministicAcrossEnvironments.test_no_absolute_path_leaks_into_the_content](DeterministicAcrossEnvironments.test_no_absolute_path_leaks_into_the_content.md) method: HOLE: no docstring
- [TheComparisonHasTeeth](TheComparisonHasTeeth.md) class: The acceptance test above, turned on itself.
  - [TheComparisonHasTeeth._producer](TheComparisonHasTeeth._producer.md) method: A copy of the real producer under `tmp`, optionally poisoned.
  - [TheComparisonHasTeeth.content_bytes_from_two_environments](TheComparisonHasTeeth.content_bytes_from_two_environments.md) method: HOLE: no docstring
  - [TheComparisonHasTeeth.test_the_real_producer_is_byte_identical_through_this_harness](TheComparisonHasTeeth.test_the_real_producer_is_byte_identical_through_this_harness.md) method: HOLE: no docstring
  - [TheComparisonHasTeeth.test_an_environment_dependent_encoder_is_caught](TheComparisonHasTeeth.test_an_environment_dependent_encoder_is_caught.md) method: HOLE: no docstring
  - [TheComparisonHasTeeth.test_a_varying_field_placed_outside_run_is_caught](TheComparisonHasTeeth.test_a_varying_field_placed_outside_run_is_caught.md) method: HOLE: no docstring
- [RealCheckoutSkew](RealCheckoutSkew.md) class: The untracked-vs-absent case, stated rather than masked.
  - [RealCheckoutSkew.declaration](RealCheckoutSkew.declaration.md) method: HOLE: no docstring
  - [RealCheckoutSkew.test_a_clean_checkout_differs_only_in_rev_never_in_shape](RealCheckoutSkew.test_a_clean_checkout_differs_only_in_rev_never_in_shape.md) method: HOLE: no docstring
    - [RealCheckoutSkew.test_a_clean_checkout_differs_only_in_rev_never_in_shape.project](RealCheckoutSkew.test_a_clean_checkout_differs_only_in_rev_never_in_shape.project.md) method: HOLE: no docstring
  - [RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content](RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content.md) method: Regression, review BLOCKER-1 (#300 g5 rework 1).
    - [RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content.project](RealCheckoutSkew.test_two_checkouts_same_commit_unequal_dirt_on_an_undeclared_file_agree_on_content.project.md) method: HOLE: no docstring
