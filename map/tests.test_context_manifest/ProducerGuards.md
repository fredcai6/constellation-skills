# tests.test_context_manifest:ProducerGuards
class, tests/test_context_manifest.py:718, 178 lines

```python
class ProducerGuards(TestCase)
```

Standing invariants of the producer's source and its writes.

```python
SOURCE = ROOT / 'scripts' / 'context_manifest.py'
PY313_ONLY_KWARGS = {'read_text': 'newline', 'write_text': 'newline'}
PY313_ONLY_ATTRS = {'batched', 'TypeIs', 'ReadOnly', 'CommandLineParser'}
```

- [own_files](ProducerGuards.own_files.md) property: The producer plus every test module written against it — discovered, so a
- [_names_used](ProducerGuards._names_used.md) static method: Every identifier and attribute actually *used as code* in a module.
- [test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer](ProducerGuards.test_no_globs_or_filesystem_enumeration_anywhere_in_the_producer.md) method: HOLE: no docstring
- [test_every_manifest_write_is_newline_pinned](ProducerGuards.test_every_manifest_write_is_newline_pinned.md) method: HOLE: no docstring
- [test_producer_and_its_tests_are_py312_compatible](ProducerGuards.test_producer_and_its_tests_are_py312_compatible.md) method: HOLE: no docstring
- [test_producer_shells_out_to_nothing](ProducerGuards.test_producer_shells_out_to_nothing.md) method: HOLE: no docstring
- [test_build_manifest_with_both_edges_injected_shells_out_to_nothing](ProducerGuards.test_build_manifest_with_both_edges_injected_shells_out_to_nothing.md) method: HOLE: no docstring

reads internal: ROOT
reads stdlib: builtins.property, builtins.staticmethod
writes internal: ProducerGuards.PY313_ONLY_ATTRS, ProducerGuards.PY313_ONLY_KWARGS, ProducerGuards.SOURCE

referenced by: none found
