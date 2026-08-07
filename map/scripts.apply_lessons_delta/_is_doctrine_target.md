# scripts.apply_lessons_delta:_is_doctrine_target
function, scripts/apply_lessons_delta.py:328, 8 lines

```python
def _is_doctrine_target(target: str) -> bool
```

A path is a doctrine artifact (an agent reads it; no unit test grades it) when it

ends in `.md` OR contains `.template.` — covers SKILL.md, _shared/*.md, docs/** prose,
and *.template.json / *.template.md spine/checklist/handoff templates. Everything else
(`.py`, `.js`, …) is a code target and is exempt. Pure path rule: never inspects
contents or judges quality.

unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
