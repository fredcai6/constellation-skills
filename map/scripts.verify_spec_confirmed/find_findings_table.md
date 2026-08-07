# scripts.verify_spec_confirmed:find_findings_table
function, scripts/verify_spec_confirmed.py:91, 32 lines

```python
def find_findings_table(text: str) -> list[str] | None
```

Return the list of Disposition cell values (one per data row), or None

if no findings table is present.

A findings table is any Markdown pipe-table whose header row contains an
``ID`` column and both a ``Disposition`` and a ``Reason`` column (exact
names, tolerant of the Lens(es)/Lens and Sev/Severity header variants).

calls internal: _split_row x3, _is_separator_row
calls stdlib: builtins.len x4
reads stdlib: builtins.list, builtins.str
unresolved: 10 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
