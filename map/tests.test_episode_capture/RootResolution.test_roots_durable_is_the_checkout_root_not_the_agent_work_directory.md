# tests.test_episode_capture:RootResolution.test_roots_durable_is_the_checkout_root_not_the_agent_work_directory
method, tests/test_episode_capture.py:149, 14 lines

```python
def test_roots_durable_is_the_checkout_root_not_the_agent_work_directory(self)
```

The silent trap: `durable_agent_work()` returns `<root>/.agent-work`, which

double-nests any `.agent-work/…`-relative durable declaration to
`.agent-work/.agent-work/…` — a path that simply does not exist, so the row
records `rev: null` and every naive check stays green.

calls internal: norm x4, RootResolution.assertNotEqual x2, RootResolution.assertEqual
calls stdlib: builtins.str, os.path.basename
reads internal: ROOT x3, awr x2, ec
reads stdlib: os (module), os.path
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
