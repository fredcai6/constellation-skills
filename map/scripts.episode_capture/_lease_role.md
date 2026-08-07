# scripts.episode_capture:_lease_role
function, scripts/episode_capture.py:227, 14 lines

```python
def _lease_role(checklist: Mapping[str, Any]) -> str | None
```

`role` — the lease's `claimed_by`, or a refusal.

A lease-less run genuinely has no role to report. Guessing one would put a
plausible `implementer` on an episode nobody can attribute, which is the exact
fabrication this composer exists to refuse.

calls stdlib: builtins.isinstance x2
reads stdlib: builtins.dict, builtins.str
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
