# tests.test_gauge_writer:test_containment_drops_one_bad_path_writes_the_remaining_single_candidate
function, tests/test_gauge_writer.py:391, 28 lines

```python
def test_containment_drops_one_bad_path_writes_the_remaining_single_candidate(proj)
```

One session_id bound to two spines -- one whose resolved spine path is

OUTSIDE the `.agent-work/<work_id>/` shape (fails `_is_contained`), one
legitimate. `_is_contained` is exercised PER PATH inside
`resolve_gauge_path` itself (unchanged by this rework -- see its own
docstring/#202), so the bad candidate is dropped BEFORE the handler ever
sees the list -- `resolve_gauge_path` returns exactly ONE candidate here,
not two. That means this scenario was never actually a multi-binding case
from `handle_post_tool_use`'s point of view: it collapses to the ordinary
single-candidate path (decision:gauge-write-skips-on-multiple-bindings
only changes behavior when 2+ candidates reach the handler). Retained
rather than retired -- it still proves per-path containment filtering,
just no longer frames it as 'both attempted' since nothing in this design
ever attempted both.

calls internal: _bind x2, _hook_data
reads internal: gw x2, _FIXTURE
unresolved: 7 calls (dispatch-unknown-base)

referenced by: none found
