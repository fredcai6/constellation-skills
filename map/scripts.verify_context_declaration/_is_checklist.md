# scripts.verify_context_declaration:_is_checklist
function, scripts/verify_context_declaration.py:105, 11 lines

```python
def _is_checklist(data: object) -> bool
```

True for anything shaped like a checklist (`gated` or `survey`) this

lint can meaningfully walk: an `items` list and a `tasks` mapping. Plenty
of `skills/*/templates/*.json` files are NOT checklists at all (engine
config, finding templates, issue-set templates) and must be skipped
rather than mis-parsed.

calls stdlib: builtins.isinstance x3
reads stdlib: builtins.dict x2, builtins.list
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
