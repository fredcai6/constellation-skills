# tests.test_episode_fields:checklist
function, tests/test_episode_fields.py:151, 34 lines

```python
def checklist(work_id='wk-042', items=None, statuses=None, claimed_by=None, rework=None, evidence=None, checks=None)
```

A gated checklist with deliberately NON-DEFAULT values, so a composer that

returns constants cannot accidentally match.

writes internal: checklist.checks, checklist.evidence, checklist.items, checklist.rework, checklist.statuses
unresolved: 4 calls (dispatch-unknown-base)

referenced by: 14 sites, this module only
