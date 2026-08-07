# tests.test_explorer_templates:_confirmed
function, tests/test_explorer_templates.py:67, 9 lines

```python
def _confirmed(text)
```

Edit the shipped DRAFT into a CONFIRMED spec touching only the designated

fields: drop the marker banner, flip Status, fill confirmer + date, fill the
Disposition/Reason cells.

calls internal: _require x3, _fill_table, _without_banner
reads internal: CONFIRMED_BY_BLANK x2, DATE_BLANK x2, STATUS_DRAFT x2, CONFIRMED_BY_FILLED, DATE_FILLED, STATUS_CONFIRMED
writes internal: _confirmed.text x4
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 5 sites, this module only
