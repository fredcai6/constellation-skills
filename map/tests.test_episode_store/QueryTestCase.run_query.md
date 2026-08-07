# tests.test_episode_store:QueryTestCase.run_query
method, tests/test_episode_store.py:736, 11 lines

```python
def run_query(self, *args, expect_rc=0)
```

Drive query_episodes.py's CLI in-process and return its parsed JSON envelope.

(The genuinely cross-process exercise is CrossSessionRetrievalTests below — this
helper is for the ordinary unit-level checks.)

calls internal: QueryTestCase.assertEqual
calls stdlib: io.StringIO x2, builtins.str, contextlib.redirect_stderr, contextlib.redirect_stdout, json.loads
reads internal: QueryTestCase.last_stderr, QueryTestCase.q, QueryTestCase.root
reads stdlib: contextlib (module) x2, io (module) x2, json (module)
writes internal: QueryTestCase.last_stderr
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 24 sites, this module only
