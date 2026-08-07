# scripts.init_work_area:_resolve_skill_dir_token
function, scripts/init_work_area.py:80, 33 lines

```python
def _resolve_skill_dir_token(text: str, token: str, skill_dir: str | None, root: Path) -> str
```

Resolve one ``<token>`` skill-dir placeholder in ``text``.

- ``<token>`` -> ``skill_dir`` when given — but fail visibly when the
  template references ``<token>/scripts`` and ``skill_dir`` carries no
  ``scripts/`` directory (e.g. an explicit repo-relative ``skills/<name>``
  in the source repo, where bundled scripts live at ``<root>/scripts``):
  substituting it verbatim would write a spine whose command checks point
  at nonexistent script paths. When omitted, auto-detect the source-repo
  layout (bundled scripts at ``<root>/scripts``) and collapse the token
  form ``<token>/scripts`` -> ``scripts`` so the init command references
  the real top-level script path; any remaining bare token resolves to
  the repo root (``.``).

calls stdlib: builtins.SystemExit, pathlib.Path
writes internal: _resolve_skill_dir_token.text
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
