# tests.test_check_corpus_freshness
tests/test_check_corpus_freshness.py, 146 lines, 14 holes

HOLE: no docstring

imports stdlib: contextlib, importlib.util, io, json, pathlib.Path, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / 'scripts' / 'check_corpus_freshness.py'
_CHECKER_MODULE = None
```

- [load_checker](load_checker.md) function: HOLE: no docstring
- [FakeRemote](FakeRemote.md) class: Stands in for GitHubRemote — same two methods, zero network.
  - [FakeRemote.__init__](FakeRemote.__init__.md) method: HOLE: no docstring
  - [FakeRemote.head_commit](FakeRemote.head_commit.md) method: HOLE: no docstring
  - [FakeRemote.compare](FakeRemote.compare.md) method: HOLE: no docstring
- [write_marker](write_marker.md) function: HOLE: no docstring
- [CorpusFreshnessTests](CorpusFreshnessTests.md) class: HOLE: no docstring
  - [CorpusFreshnessTests._run](CorpusFreshnessTests._run.md) method: HOLE: no docstring
  - [CorpusFreshnessTests.test_current_exits_zero](CorpusFreshnessTests.test_current_exits_zero.md) method: HOLE: no docstring
  - [CorpusFreshnessTests.test_behind_exits_one_with_count_and_subjects](CorpusFreshnessTests.test_behind_exits_one_with_count_and_subjects.md) method: HOLE: no docstring
  - [CorpusFreshnessTests.test_unknown_source_commit_is_cannot_determine](CorpusFreshnessTests.test_unknown_source_commit_is_cannot_determine.md) method: HOLE: no docstring
  - [CorpusFreshnessTests.test_missing_source_commit_is_cannot_determine](CorpusFreshnessTests.test_missing_source_commit_is_cannot_determine.md) method: HOLE: no docstring
  - [CorpusFreshnessTests.test_missing_marker_is_cannot_determine](CorpusFreshnessTests.test_missing_marker_is_cannot_determine.md) method: HOLE: no docstring
  - [CorpusFreshnessTests.test_invalid_marker_json_is_cannot_determine](CorpusFreshnessTests.test_invalid_marker_json_is_cannot_determine.md) method: HOLE: no docstring
  - [CorpusFreshnessTests.test_remote_unreachable_is_cannot_determine](CorpusFreshnessTests.test_remote_unreachable_is_cannot_determine.md) method: HOLE: no docstring
