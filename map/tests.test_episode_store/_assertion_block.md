# tests.test_episode_store:_assertion_block
function, tests/test_episode_store.py:598, 10 lines

```python
def _assertion_block(text, aid)
```

Extract one "### assertion:<id>.<aid>" block's raw text, up to (not including)

the next "###"/"##" heading -- used to prove a sibling assertion's stored lines are
byte-identical across a dispute.

calls stdlib: re.compile, re.escape
reads stdlib: re (module) x3, re.DOTALL
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 5 sites, this module only
