# scripts.verify_context_declaration:_appears_at_path_boundary
function, scripts/verify_context_declaration.py:80, 23 lines

```python
def _appears_at_path_boundary(path: str, prose: str) -> bool
```

True when `path` occurs in `prose` as a whole path token, not merely as

a substring of a longer, different path. A match counts only when it is
bounded at BOTH ends: the character immediately preceding it -- start-of-
string, whitespace, a quote, a backtick, or `(` all qualify -- is not
itself a path character, AND nothing immediately after it continues the
path (see `_bounded_after` for the `.`-disambiguation). This catches a
declared `agents/GLOSSARY.md` wrongly matching inside prose's
`docs/agents/GLOSSARY.md` (leading side), and a declared
`docs/agents/GLOSSARY.md` wrongly matching inside prose's
`docs/agents/GLOSSARY.md.bak` (trailing side) -- the same defect class,
a declared path resolving to a DIFFERENT file than the prose names, seen
from either end.

calls internal: _bounded_after
calls stdlib: builtins.len
reads internal: _PATH_CHAR
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
