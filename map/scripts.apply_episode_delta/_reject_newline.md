# scripts.apply_episode_delta:_reject_newline
function, scripts/apply_episode_delta.py:158, 38 lines

```python
def _reject_newline(value: str, where: str) -> str
```

C3b — the injection defense named in EPISODE_STORE.md section 7: a free-text

value that embeds a line boundary could forge a line that LOOKS like a store
field (e.g. "- status: retired") once rendered. Reject before it is ever written,
rather than trying to escape it at render time.

The predicate is `value.splitlines() != [value]`, NOT a hand-listed character
set (the previous version checked only "\n" / "\r" and was demonstrated to
silently corrupt data: parse_episode() sections the file using str.splitlines()
throughout, and splitlines() treats a WIDER set of characters as line boundaries
than "\n"/"\r" alone — \v, \f, \x1c-\x1e, \x85 (NEL), U+2028 (LINE
SEPARATOR), U+2029 (PARAGRAPH SEPARATOR). A value containing e.g. U+2028 has
neither "\n" nor "\r" in it, so the old guard accepted it; the file wrote
successfully once, and the NEXT parse_episode() call silently truncated the
field at the U+2028, discarding the rest with no error. Defining the guard in
terms of splitlines() itself — the exact function the parser uses to section the
file — makes the guard and the parser the same source of truth, so they cannot
drift apart again the way a maintained character list inevitably would.

`!= [value]` (rather than `len(value.splitlines()) > 1`) also closes the
trailing-separator case for free: a value ending in a boundary character, e.g.
"text\u2028", splits to a SINGLE element (["text"]) — `len(...) > 1` would
wrongly accept it — but ["text"] != ["text\u2028"], so this predicate still
rejects it: the trailing separator is silently dropped on the next parse just
as surely as an embedded one truncates the field.

One explicit carve-out: the empty string. "".splitlines() == [] (NOT [""]), so
the predicate alone would reject "" — wrong, since an empty value contains no
boundary of any kind and several optional fields legitimately pass "". Guard
with `value != ""` first rather than special-casing splitlines()'s output, so
the boundary-detection logic itself stays a single, unmodified call to the
parser's own function.

calls internal: EpisodeDeltaError
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 4 sites, this module only
