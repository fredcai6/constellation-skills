# scripts.check_corpus_freshness:main
function, scripts/check_corpus_freshness.py:154, 32 lines

```python
def main(argv: list[str] | None = None, *, remote: GitHubRemote | None = None) -> int
```

HOLE: no docstring

calls internal: GitHubRemote, evaluate, read_marker
calls stdlib: builtins.print x2, argparse.ArgumentParser
reads internal: DEFAULT_BRANCH x2, DEFAULT_REPO x2, FreshnessError
reads stdlib: argparse (module), builtins.__doc__, pathlib.Path, sys (module), sys.stderr
writes internal: main.remote
unresolved: 4 calls (dispatch-unknown-base), 3 reads (dispatch-unknown-base)

referenced by: 1 sites, this module only
