# scripts.checklist_engine:_render_anchor_lines
function, scripts/checklist_engine.py:1627, 15 lines

```python
def _render_anchor_lines(anchors) -> list[str]
```

Format the `anchors` field for display. Three shapes appear in the

live corpus (verified against 20+ archived execute.json gates plus the
shipped EXECUTE_PLAN.template.json, issue #420): a dict of
category -> [str] (most Commander mission-frame anchors), a dict of
category -> str (e.g. g1-review's `{"inherits": "..."}`), or a flat [str]
on some archived gates. Unrecognized shapes render nothing rather than
guessing at a format the corpus doesn't actually use.

calls internal: _anchor_category_items
calls stdlib: builtins.isinstance x2
reads stdlib: builtins.dict, builtins.list
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
