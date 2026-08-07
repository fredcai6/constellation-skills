# scripts.checklist_engine:_rail_prefix
function, scripts/checklist_engine.py:300, 12 lines

```python
def _rail_prefix(point: str, cl: dict) -> str
```

The doctrine rail as a FRONT-loaded prefix (#227 gate g3, items 2/4):

``"RAIL: <text>\n\n"`` when a rail applies, else ``""``. `_rail()`'s own
unit contract is UNCHANGED (still a ``"\n\n" + "RAIL: " + text`` suffix
shape -- pinned by `test_rail_marker_and_leading_newlines`); this only
repositions the SAME text at the two CLI-boundary call sites
(`dispatch()`'s success path, `main()`'s REFUSED path) so the banner
lands FIRST and the operative result/refusal line lands LAST on the
stream -- the field defect this fixes: `tail -1` used to show only the
banner, silently hiding a real REFUSED line.

calls internal: _rail
calls stdlib: builtins.chr
unresolved: 1 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
