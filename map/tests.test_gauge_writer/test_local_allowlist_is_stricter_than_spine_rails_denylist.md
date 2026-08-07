# tests.test_gauge_writer:test_local_allowlist_is_stricter_than_spine_rails_denylist
function, tests/test_gauge_writer.py:807, 12 lines

```python
def test_local_allowlist_is_stricter_than_spine_rails_denylist(proj)
```

g1's rejection is a hand-maintained DENYLIST (`#`, `/`, `\`, `..`) and

it still admits `:`, `*` and `?` -- every one of which reaches this
module's `agent-{agent_id}.jsonl` interpolation on a Windows filesystem.
So this module validates at its OWN boundary, with an ALLOWLIST (the real
ids observed are hex-ish tokens plus `-` and `_`) rather than by extending
someone else's denylist.

Each id below is one spine_rail ADMITS and this module must not.

reads internal: gw, sr
unresolved: 2 calls (dispatch-unknown-base)

referenced by: none found
