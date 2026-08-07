# scripts.collect_feedback:_slugify
function, scripts/collect_feedback.py:208, 9 lines

```python
def _slugify(text: str) -> str
```

Normalize a human label into a stable kebab slug.

Strips parenthetical annotations and cross-refs (e.g. "(CORROBORATES
issue-446)") that drift run-to-run but are not part of a finding's identity,
then collapses the rest to kebab-case.

calls stdlib: re.sub x2
reads stdlib: re (module) x2
writes internal: _slugify.text
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 5 sites, this module only
