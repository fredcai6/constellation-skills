# scripts.checklist_engine:_anchor_category_items
function, scripts/checklist_engine.py:1611, 14 lines

```python
def _anchor_category_items(items) -> list[str]
```

Normalize one `anchors` dict category's value to a list of strings.

Two shapes appear in the live corpus: a list of strings (most mission-
frame anchors), or a single bare string (e.g. EXECUTE_PLAN.template.json's
g1-review gate: `{"inherits": "g1-implement anchors — ..."}`). A bare
string must NOT be treated as an iterable of characters — that silently
exploded one sentence into one line per letter (found in review of issue
#420, reproduced against `skills/commander/templates/
EXECUTE_PLAN.template.json`'s shipped g1-review gate).

calls stdlib: builtins.isinstance x3
reads stdlib: builtins.str x2, builtins.list

referenced by: 1 sites, this module only
