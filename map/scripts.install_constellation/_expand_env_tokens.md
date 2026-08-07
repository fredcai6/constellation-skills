# scripts.install_constellation:_expand_env_tokens
function, scripts/install_constellation.py:632, 14 lines

```python
def _expand_env_tokens(text: str, env: Mapping[str, str]) -> str
```

Expand ONLY `_EXPANDABLE_ENV_TOKENS`, and only when actually set,

leaving every other token LITERAL rather than dropping it -- a dropped
token would collapse the path to a shorter one that might coincidentally
exist. A surviving token is the signal `detect_hook_wiring` uses to declare
an entry undeterminable rather than guessing at it.

- [replace](_expand_env_tokens.replace.md) method: HOLE: no docstring

reads internal: _ENV_TOKEN_RE
reads stdlib: builtins.str, re (module), re.Match
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
