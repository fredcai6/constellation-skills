# tests.test_docent_freshness
tests/test_docent_freshness.py, 165 lines, 17 holes

Unit tests for scripts/docent_freshness.py.

The freshness tool is the load-bearing part of docent: a stale explainer site
must be *provably* stale, not eyeballed. These tests pin the digest determinism
and the fresh(exit 0)/stale(nonzero) contract, including that perturbing a single
source-map file flips the verdict.

imports stdlib: contextlib.redirect_stdout, importlib.util, io, pathlib.Path, sys, tempfile, unittest
imported by: none found

```python
ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / 'scripts' / 'docent_freshness.py'
```

- [load_tool](load_tool.md) function: HOLE: no docstring
- [seed_map](seed_map.md) function: Write a minimal but representative source-map tree under root.
- [write_site](write_site.md) function: HOLE: no docstring
- [ComputeStampTests](ComputeStampTests.md) class: HOLE: no docstring
  - [ComputeStampTests.setUp](ComputeStampTests.setUp.md) method: HOLE: no docstring
  - [ComputeStampTests._tmp](ComputeStampTests._tmp.md) method: HOLE: no docstring
  - [ComputeStampTests.test_stamp_is_64_hex_and_deterministic](ComputeStampTests.test_stamp_is_64_hex_and_deterministic.md) method: HOLE: no docstring
  - [ComputeStampTests.test_stamp_changes_when_a_source_file_is_perturbed](ComputeStampTests.test_stamp_changes_when_a_source_file_is_perturbed.md) method: HOLE: no docstring
  - [ComputeStampTests.test_stamp_is_independent_of_absolute_location](ComputeStampTests.test_stamp_is_independent_of_absolute_location.md) method: HOLE: no docstring
  - [ComputeStampTests.test_generated_map_json_included_when_present](ComputeStampTests.test_generated_map_json_included_when_present.md) method: HOLE: no docstring
- [CheckCliTests](CheckCliTests.md) class: HOLE: no docstring
  - [CheckCliTests.setUp](CheckCliTests.setUp.md) method: HOLE: no docstring
  - [CheckCliTests._tmp](CheckCliTests._tmp.md) method: HOLE: no docstring
  - [CheckCliTests.test_stamp_subcommand_prints_digest](CheckCliTests.test_stamp_subcommand_prints_digest.md) method: HOLE: no docstring
  - [CheckCliTests.test_check_fresh_exits_zero](CheckCliTests.test_check_fresh_exits_zero.md) method: HOLE: no docstring
  - [CheckCliTests.test_check_stale_exits_nonzero_after_source_perturbation](CheckCliTests.test_check_stale_exits_nonzero_after_source_perturbation.md) method: HOLE: no docstring
  - [CheckCliTests.test_check_accepts_index_html_file_path_directly](CheckCliTests.test_check_accepts_index_html_file_path_directly.md) method: HOLE: no docstring
  - [CheckCliTests.test_check_missing_stamp_is_error_nonzero](CheckCliTests.test_check_missing_stamp_is_error_nonzero.md) method: HOLE: no docstring
