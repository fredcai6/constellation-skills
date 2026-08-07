# scripts.init_work_area:_assert_no_resolver_placeholders
function, scripts/init_work_area.py:33, 19 lines

```python
def _assert_no_resolver_placeholders(text: str) -> None
```

Fail loudly if a resolver-owned placeholder survives resolution.

This is the epic-101/epic-138 class of defect (#114, #154): a role's spine
template introduces its own placeholder (e.g. ``<admiral-skill-dir>``,
``<admiral-session-id>``) that the resolver did not know how to substitute,
and it is left literal inside an engine check-command string — the engine
then refuses to ``advance`` many steps into a run, with a confusing
"file not found" pointing at the literal placeholder, instead of failing
here at instantiation where the cause is obvious.

calls stdlib: builtins.SystemExit, builtins.set, builtins.sorted
reads internal: _RESOLVER_OWNED_TOKEN_RE
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
