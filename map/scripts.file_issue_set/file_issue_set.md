# scripts.file_issue_set:file_issue_set
function, scripts/file_issue_set.py:264, 50 lines

```python
def file_issue_set(manifest: dict, spec_text: str, adapter: FilingAdapter, receipt_path: Path, *, crash_at: str | None = None) -> dict
```

File the set idempotently, returning the receipt. Runs the rail first.

`crash_at` is a test-only injection point: one of "before-file",
"after-file-before-receipt", "after-receipt". Each re-run after a crash
yields no duplicate epic.

calls internal: _crash x3, _write_receipt x2, FilingAdapter.create_epic, FilingAdapter.create_issue, FilingAdapter.find_epic, FilingAdapter.find_issue, _load_receipt, build_epic_body, build_issue_body, epic_key, issue_key
calls stdlib: pathlib.Path
calls third-party: verify_issue_set.verify_issue_set
writes internal: file_issue_set.receipt_path
unresolved: 5 calls (dispatch-unknown-base), 1 writes (non-name-expr)

referenced by: 1 sites, this module only
