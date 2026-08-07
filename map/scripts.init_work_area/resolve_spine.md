# scripts.init_work_area:resolve_spine
function, scripts/init_work_area.py:115, 35 lines

```python
def resolve_spine(template_text: str, work_id: str, skill_dir: str | None, root: Path) -> str
```

Resolve spine placeholders in a spine template's text.

- Every role-specific ``<role-skill-dir>`` token present (``<commander-skill-dir>``,
  ``<admiral-skill-dir>``, and any future role's) resolves via
  ``_resolve_skill_dir_token`` from the same ``skill_dir``/``root`` inputs (see that
  helper), discovered by pattern rather than hardcoded per role so a new role's spine
  template does not recur this defect under a fresh token name (#114/#154). The
  generic ``<skill-dir>`` token resolves the same way; ``<commander-skill-dir>``
  behavior is unchanged (byte-identical) by this generalization.
- Every role-specific ``<role-session-id>`` token (``<commander-session-id>``,
  ``<admiral-session-id>``, ...) -> ``<role>-<work-id>`` (the conventional default),
  likewise discovered by pattern.
- ``<work-id>`` -> the work_id argument (all occurrences).
- ``<repo-root>`` -> the absolute, resolved repo root. A **robustness**
  token, not a repair: the engine passes command checks no ``cwd``, so they
  inherit the launcher's. The relative checks already shipped work because
  the launcher normally sits at the repo root — they are fragile, not
  broken (their fragility is tracked separately as #341). ``<repo-root>``
  lets a template author write a check that does not depend on where the
  launcher happened to be. Emitted with forward slashes
  (``as_posix()``): a spine is JSON and command checks run under a POSIX
  shell, so a Windows ``str(Path)`` value would carry backslashes that
  ``instantiate_spine``'s own ``json.loads`` guard rejects as invalid
  escapes.

calls internal: _resolve_skill_dir_token x2
calls stdlib: builtins.sorted x2, builtins.set, pathlib.Path
reads internal: _ROLE_SESSION_ID_RE, _ROLE_SKILL_DIR_RE
unresolved: 7 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
