# scripts.verify_context_declaration:_bounded_after
function, scripts/verify_context_declaration.py:64, 14 lines

```python
def _bounded_after(prose: str, end: int) -> bool
```

True when nothing immediately after `prose[:end]` continues the path

token that ends there. End-of-string always qualifies. A `.` is special:
it qualifies (does NOT continue the path) only when the character past it
is not alphanumeric -- `.` then alnum is an extension glued onto the
match (a real `.bak`/`.old`/`.tmp` sibling file); `.` then anything else,
or nothing, is ordinary sentence punctuation.

calls stdlib: builtins.len x2
reads internal: _TRAILING_CONTINUATION_CHAR
unresolved: 2 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
