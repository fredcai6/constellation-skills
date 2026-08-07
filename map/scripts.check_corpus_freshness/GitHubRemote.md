# scripts.check_corpus_freshness:GitHubRemote
class, scripts/check_corpus_freshness.py:55, 45 lines

```python
class GitHubRemote
```

Fetches upstream facts from the GitHub REST API. Tries `gh api` first

(inherits the cloud session's auth), then an unauthenticated HTTPS GET. Both
hit the same REST paths, so a fake with the same two methods stands in for the
whole class in tests — no network is ever touched under test.

- [__init__](GitHubRemote.__init__.md) method: HOLE: no docstring
- [_get](GitHubRemote._get.md) method: HOLE: no docstring
- [head_commit](GitHubRemote.head_commit.md) method: HOLE: no docstring
- [compare](GitHubRemote.compare.md) method: GitHub compare of base...head. `ahead_by` is how many commits `head`

reads internal: DEFAULT_BRANCH, DEFAULT_REPO
reads stdlib: builtins.str x6, builtins.dict x2

referenced by: 3 sites, this module only
