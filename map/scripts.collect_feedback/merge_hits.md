# scripts.collect_feedback:merge_hits
function, scripts/collect_feedback.py:335, 12 lines

```python
def merge_hits(*groups: Hits) -> Hits
```

Merge candidate groups (e.g. new + open) into one fingerprint -> hits view.

Filing eligibility cares about a finding's *total* open occurrences across the
whole sweep, regardless of which projects have already marked it collected, so
the new and open-unresolved buckets are merged before counting recurrence.

reads internal: Hits
unresolved: 3 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
