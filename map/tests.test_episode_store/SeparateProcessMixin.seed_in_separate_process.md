# tests.test_episode_store:SeparateProcessMixin.seed_in_separate_process
method, tests/test_episode_store.py:1203, 15 lines

```python
def seed_in_separate_process(self, store_root, work_dir, op)
```

HOLE: no docstring

calls internal: SeparateProcessMixin.assertEqual, SeparateProcessMixin.assertIsNotNone, SeparateProcessMixin.run_in_separate_process
calls stdlib: builtins.str x2, json.dumps, pathlib.Path, re.search
reads internal: WRITER_SCRIPT
reads stdlib: json (module), re (module)
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 7 sites, this module only
