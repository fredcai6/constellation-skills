# scripts.stage_feedback:stage_feedback
function, scripts/stage_feedback.py:100, 55 lines

```python
def stage_feedback(root: Path, work_id: str, *, feedback_body: str, launch_order: str, ownership: str, return_shape: str, lessons_delta: str | None = None, constellation_feedback: str | None = None, fence_text: str | None = None, entry_date: str | None = None, force: bool = False) -> Path
```

Write the four staged-feedback files at

`<root>/.agent-work/staged-feedback/<work-id>/`. Returns that directory.

Refuses (like `instantiate_spine`) to overwrite an existing staged run
directory unless `force` is passed, so a re-run never silently clobbers a
prior staging.

calls internal: _agent_feedback_text, _default_constellation_feedback, _default_lessons_delta, _fence_text
calls stdlib: builtins.SystemExit x2, datetime.date.today, json.loads
reads internal: TRIO_FILES
reads stdlib: datetime.date, json (module)
writes internal: stage_feedback.entry_date
unresolved: 10 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
