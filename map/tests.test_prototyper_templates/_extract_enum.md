# tests.test_prototyper_templates:_extract_enum
function, tests/test_prototyper_templates.py:31, 9 lines

```python
def _extract_enum(text: str, heading: str) -> list[str]
```

Pull the backtick-quoted, pipe-separated enum on the line directly

under a `## <heading>` heading in the real template file. This is the
ONLY source of enum values this suite uses — never a hand-typed literal
standing in for the template.

calls stdlib: re.compile, re.escape
reads stdlib: re (module) x3, re.MULTILINE
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 2 sites, this module only
