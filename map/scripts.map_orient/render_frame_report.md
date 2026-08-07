# scripts.map_orient:render_frame_report
function, scripts/map_orient.py:828, 19 lines

```python
def render_frame_report(first_line: str, code: int, problems: Sequence[str], frame_rel: str, mode: str) -> list[str]
```

PURE. stdout lines; line 0 is always a reserved literal.

Deliberately prints NO part of the map inventory. `orient` never prints an
anchor id for the same reason: if the tool hands over the ids, citing one
stops being evidence the map was read. Only ids the frame itself already
contains are echoed back, and only to name an offender.

calls stdlib: builtins.len
reads internal: EXIT_OK, FRAME_MISSING
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
