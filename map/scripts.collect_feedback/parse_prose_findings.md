# scripts.collect_feedback:parse_prose_findings
function, scripts/collect_feedback.py:137, 30 lines

```python
def parse_prose_findings(text: str) -> list[dict[str, str]]
```

Parse the legacy prose export shape into finding dicts.

A finding is a `### <label>` sub-heading under a `## <epic>` block. The label
(minus a leading `Lesson:` prefix) is the candidate slug; inline `**Field:**`
spans and the leading paragraph supply observed/proposal/lesson/etc. The
field-format parser (`parse_entries`) ignores these blocks (they carry no
`- **Field:**` list lines), so the two parsers never double-count.

calls internal: _extract_inline_fields, _map_prose_label
calls stdlib: builtins.len x4, builtins.enumerate x2, builtins.list x2, re.sub
reads internal: ENTRY_HEADING_RE, PROSE_HEADING_RE
reads stdlib: builtins.str x4, builtins.dict x2, builtins.list, re (module)
unresolved: 10 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
