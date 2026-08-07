# scripts.grade_lint:lint_one_file
function, scripts/grade_lint.py:706, 40 lines

```python
def lint_one_file(raw_path: str, global_ids: set[str], ids_provided_globally: bool, mode: str) -> tuple[list[DecisionRecord], list[Violation]]
```

Scan and validate one plan file, Markdown or JSON.

Returns its decisions and every violation attributable to it (per-decision
validation, the GL011 no-id-source note, and this file's cross-occurrence
findings). Raises LintToolingError if the file cannot be read or parsed.

calls internal: LintToolingError x2, cross_occurrence_violations, extract_plan_ids, make_violation, scan_json, scan_markdown, validate_decision
calls stdlib: json.loads, pathlib.Path
reads stdlib: json (module) x2, builtins.OSError, json.JSONDecodeError
unresolved: 5 calls (dispatch-unknown-base), 4 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
