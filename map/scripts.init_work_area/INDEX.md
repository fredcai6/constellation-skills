# scripts.init_work_area
scripts/init_work_area.py, 204 lines, 2 holes

Scaffold a Constellation work area: .agent-work/<work-id>/ and its subdirs.

Optionally instantiate spine.json from a named spine template, resolving the
commander placeholders so the result is immediately runnable by the engine.

imports stdlib: __future__.annotations, argparse, json, pathlib.Path, re, sys
imported by: none found

```python
SUBDIRS = ['crew-handoffs', 'evidence', 'triage-candidates']
_ROLE_SKILL_DIR_RE = re.compile('<([a-zA-Z0-9-]+)-skill-dir>')
_ROLE_SESSION_ID_RE = re.compile('<([a-zA-Z0-9-]+)-session-id>')
_RESOLVER_OWNED_TOKEN_RE = re.compile('<(work-id|repo-root|[a-zA-Z0-9-]+-skill-dir|[a-zA-Z0-9-]+-session-id)>')
```

- [_assert_no_resolver_placeholders](_assert_no_resolver_placeholders.md) function: Fail loudly if a resolver-owned placeholder survives resolution.
- [_assert_root_is_not_the_agent_work_dir](_assert_root_is_not_the_agent_work_dir.md) function: Refuse a ``--root`` that already ends in ``.agent-work``.
- [init_work_area](init_work_area.md) function: HOLE: no docstring
- [_resolve_skill_dir_token](_resolve_skill_dir_token.md) function: Resolve one ``<token>`` skill-dir placeholder in ``text``.
- [resolve_spine](resolve_spine.md) function: Resolve spine placeholders in a spine template's text.
- [instantiate_spine](instantiate_spine.md) function: Write .agent-work/<work-id>/spine.json from ``template`` with placeholders resolved.
- [main](main.md) function: HOLE: no docstring
