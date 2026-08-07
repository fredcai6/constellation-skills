# scripts.checklist_engine:render_human
function, scripts/checklist_engine.py:1644, 50 lines

```python
def render_human(view: dict) -> str
```

Human adapter: format a StateView as the text agents read from

`current`. Pure presentation — every fact comes from `view`; this function
adds none of its own. The FIRST line of the active branch stays exactly
`ACTIVE {id} [{status}] — {imperative}` (tests/test_checklist_engine.py's
GoldenOutputBriefing class, ~3779 on, pins this across every shipped
template — the docstring used to cite line 818, a stale reference to an
unrelated `require_session` lease test, corrected by issue #420); the
conditions block, `n/m met` summary, `constraints:`/`anchors:` blocks (issue
#420 defect 2 — emitted only when populated, so an empty/absent field adds
no output) and `next:` hint are appended AFTER it. The why/refresh suffix
(`_why_suffix`, composed — not replaced — into `view["why_text"]` by
`state()`) rides last, same relative order as before this change; the Trip
`CONTEXT` advisory is a `dispatch()`-level suffix outside `current()`
entirely and is untouched.

calls internal: _render_anchor_lines
calls stdlib: builtins.len x4
unresolved: 19 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
