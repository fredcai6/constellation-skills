# scripts.apply_episode_delta:Episode.all_assertions
method, scripts/apply_episode_delta.py:251, 7 lines

```python
def all_assertions(self) -> dict[str, Assertion]
```

Flat aid -> Assertion map spanning both agent-supplied and diagnosis bins,

for amend-assertion lookup by id (e.g. "a4" or "d1").

reads internal: Episode.agent_supplied, Episode.diagnosis
unresolved: 1 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
