# tests.test_episode_capture:RootResolution.test_roots_durable_resolves_a_declaration_without_double_nesting
method, tests/test_episode_capture.py:164, 30 lines

```python
def test_roots_durable_resolves_a_declaration_without_double_nesting(self)
```

Resolve a `durable`-rooted declaration through the real producer and assert

the absolute path it lands on.

The entry is **synthetic**. Until #308 this test resolved the corpus's one
shipped `durable` declaration (`.agent-work/LESSONS.md` in
`COMMANDER_SPINE.template.json`); cutting the lessons read path removed it, and
the corpus now ships none — asserted below, so a re-added one is visible rather
than silently changing what this test exercises. The subject was never that
path: it is the double-nesting trap in `resolve_roots`, which any
`.agent-work/…`-relative durable path exposes.

calls internal: RootResolution.assertEqual x2, norm x2, RootResolution.assertNotIn
calls stdlib: os.path.normcase x2, json.loads, os.path.join, pathlib.Path
reads internal: ROOT x2, cm, ec
reads stdlib: os (module) x3, os.path x3, json (module)
unresolved: 3 calls (dispatch-unknown-base)

referenced by: none found
