# tests.test_gauge_reader:ModelTableSyncTests
class, tests/test_gauge_reader.py:79, 28 lines

```python
class ModelTableSyncTests(TestCase)
```

The writer supplies the window, the reader supplies the thresholds. A

model in only one table is a half-added model: either no reading is ever
produced for it, or a reading is produced that the reader then rejects.
Both are silent, so pin the key sets equal.

- [test_writer_and_reader_cover_the_same_models](ModelTableSyncTests.test_writer_and_reader_cover_the_same_models.md) method: HOLE: no docstring
- [test_windows_agree_between_the_two_tables](ModelTableSyncTests.test_windows_agree_between_the_two_tables.md) method: The reader stores the window alongside its caps; a disagreement

referenced by: none found
