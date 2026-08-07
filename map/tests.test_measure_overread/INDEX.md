# tests.test_measure_overread
tests/test_measure_overread.py, 178 lines, 23 holes

Unit tests for scripts/measure_overread.py.

Fixture-based against the small SYNTHETIC corpus at
tests/fixtures/overread_corpus/ (see that directory's README.md for why it
is synthetic and what schema it is modeled on). No real filesystem paths
outside the repo/tmp_path; no network; deterministic.

imports stdlib: importlib.util, os, pathlib.Path, subprocess, sys
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
CORPUS_DIR = Path(__file__).resolve().parent / 'fixtures' / 'overread_corpus'
mo = load('measure_overread')
```

- [load](load.md) function: HOLE: no docstring
- [test_classify_spine_json_is_state](test_classify_spine_json_is_state.md) function: HOLE: no docstring
- [test_classify_cycle_json_is_state](test_classify_cycle_json_is_state.md) function: HOLE: no docstring
- [test_classify_generic_checklist_json_is_state](test_classify_generic_checklist_json_is_state.md) function: HOLE: no docstring
- [test_classify_execute_json_is_state](test_classify_execute_json_is_state.md) function: HOLE: no docstring
- [test_classify_checklist_engine_py_is_engine_source](test_classify_checklist_engine_py_is_engine_source.md) function: HOLE: no docstring
- [test_classify_journal_file_does_not_count](test_classify_journal_file_does_not_count.md) function: HOLE: no docstring
- [test_classify_references_and_templates_do_not_count](test_classify_references_and_templates_do_not_count.md) function: HOLE: no docstring
- [test_classify_schema_doc_does_not_count](test_classify_schema_doc_does_not_count.md) function: HOLE: no docstring
- [test_classify_unrelated_source_does_not_count](test_classify_unrelated_source_does_not_count.md) function: HOLE: no docstring
- [test_scan_transcript_zero_structural_reads](test_scan_transcript_zero_structural_reads.md) function: HOLE: no docstring
- [test_scan_transcript_several_structural_reads](test_scan_transcript_several_structural_reads.md) function: HOLE: no docstring
- [test_scan_transcript_discriminates_journal_and_references](test_scan_transcript_discriminates_journal_and_references.md) function: HOLE: no docstring
- [test_scan_transcript_skips_malformed_lines_without_crashing](test_scan_transcript_skips_malformed_lines_without_crashing.md) function: HOLE: no docstring
- [test_scan_transcript_counter_actually_discriminates](test_scan_transcript_counter_actually_discriminates.md) function: HOLE: no docstring
- [test_scan_corpus_is_sorted_by_filename](test_scan_corpus_is_sorted_by_filename.md) function: HOLE: no docstring
- [test_scan_corpus_covers_all_four_fixtures](test_scan_corpus_covers_all_four_fixtures.md) function: HOLE: no docstring
- [test_aggregate_sums_across_committed_corpus](test_aggregate_sums_across_committed_corpus.md) function: HOLE: no docstring
- [test_scan_corpus_deterministic_across_repeated_calls](test_scan_corpus_deterministic_across_repeated_calls.md) function: HOLE: no docstring
- [test_format_report_has_per_run_and_aggregate_line](test_format_report_has_per_run_and_aggregate_line.md) function: HOLE: no docstring
- [_child_env](_child_env.md) function: HOLE: no docstring
- [test_cli_default_corpus_prints_aggregate_line](test_cli_default_corpus_prints_aggregate_line.md) function: HOLE: no docstring
- [test_cli_missing_corpus_dir_fails_visibly](test_cli_missing_corpus_dir_fails_visibly.md) function: HOLE: no docstring
