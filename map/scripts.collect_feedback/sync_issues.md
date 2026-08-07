# scripts.collect_feedback:sync_issues
function, scripts/collect_feedback.py:473, 73 lines

```python
def sync_issues(merged: Hits, *, inbox_path: Path, filer=gh_file_issue, commenter=gh_comment_issue, include_singles: bool = False, confirm: bool = False, labels=(), repo: str | None = None) -> dict
```

File new eligible findings and comment on filed issues whose recurrence has

grown since the ledger watermark. Dry run unless `confirm`. The ledger is saved
after each successful action so a mid-run gh failure leaves prior actions durably
recorded. Issues are closed the normal way (a fixing PR references them) — there
is no auto-close.

calls internal: _issue_ref x3, save_inbox x2, _is_open, _recurrence_comment, eligible_for_filing, issue_spec, load_inbox, sync_issues.commenter, sync_issues.filer
calls stdlib: builtins.len x3, builtins.set x2, datetime.date.today x2, builtins.bool, builtins.sorted
reads stdlib: datetime.date x2
unresolved: 14 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
