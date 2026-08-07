# scripts.docent_freshness:read_embedded_stamp
function, scripts/docent_freshness.py:114, 10 lines

```python
def read_embedded_stamp(site: Path) -> str | None
```

Return the digest embedded in the site's HTML, or None if absent/missing.

calls internal: _resolve_site_html
reads internal: _STAMP_RE
unresolved: 6 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
