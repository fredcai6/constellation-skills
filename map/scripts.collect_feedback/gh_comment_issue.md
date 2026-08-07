# scripts.collect_feedback:gh_comment_issue
function, scripts/collect_feedback.py:420, 7 lines

```python
def gh_comment_issue(ref: str, body: str, *, repo: str | None = None) -> dict
```

Default commenter: post a comment on an existing issue via `gh`.

calls stdlib: subprocess.run
reads stdlib: subprocess (module)

referenced by: 2 sites, this module only
