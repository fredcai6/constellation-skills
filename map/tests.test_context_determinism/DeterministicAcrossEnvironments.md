# tests.test_context_determinism:DeterministicAcrossEnvironments
class, tests/test_context_determinism.py:141, 150 lines

```python
class DeterministicAcrossEnvironments(TestCase)
```

HOLE: no docstring

```python
ENVIRONMENTS = ({'LC_ALL': 'C', 'LANG': 'C', 'PYTHONHASHSEED': '1'}, {'LC_ALL': 'tr_TR.UTF-8', 'LANG':...
```

- [setUpClass](DeterministicAcrossEnvironments.setUpClass.md) class method: HOLE: no docstring
- [tearDownClass](DeterministicAcrossEnvironments.tearDownClass.md) class method: HOLE: no docstring
- [_cleanup](DeterministicAcrossEnvironments._cleanup.md) class method: HOLE: no docstring
- [setUp](DeterministicAcrossEnvironments.setUp.md) method: HOLE: no docstring
- [test_the_two_environments_really_are_distinct](DeterministicAcrossEnvironments.test_the_two_environments_really_are_distinct.md) method: HOLE: no docstring
- [test_the_locale_and_hash_seed_mutations_took_effect_inside_the_child](DeterministicAcrossEnvironments.test_the_locale_and_hash_seed_mutations_took_effect_inside_the_child.md) method: HOLE: no docstring
- [test_content_is_byte_identical_excluding_exactly_the_run_subtree](DeterministicAcrossEnvironments.test_content_is_byte_identical_excluding_exactly_the_run_subtree.md) method: HOLE: no docstring
- [test_the_compared_bytes_are_the_ones_the_children_wrote](DeterministicAcrossEnvironments.test_the_compared_bytes_are_the_ones_the_children_wrote.md) method: HOLE: no docstring
- [test_the_run_subtrees_differ_so_the_exclusion_is_load_bearing](DeterministicAcrossEnvironments.test_the_run_subtrees_differ_so_the_exclusion_is_load_bearing.md) method: HOLE: no docstring
- [test_the_content_is_a_real_projection_not_an_empty_one](DeterministicAcrossEnvironments.test_the_content_is_a_real_projection_not_an_empty_one.md) method: HOLE: no docstring
- [test_no_absolute_path_leaks_into_the_content](DeterministicAcrossEnvironments.test_no_absolute_path_leaks_into_the_content.md) method: HOLE: no docstring

reads stdlib: builtins.classmethod x3
writes internal: DeterministicAcrossEnvironments.ENVIRONMENTS

referenced by: 1 sites, this module only
