# tests.test_gauge_writer:test_ambiguous_binding_writes_skip_flag_to_every_candidate
function, tests/test_gauge_writer.py:523, 31 lines

```python
def test_ambiguous_binding_writes_skip_flag_to_every_candidate(proj)
```

Two genuinely different top-level agents sharing one session_id (#202/

#261) still write NOTHING to gauge.json (unchanged), but now BOTH
candidate spines get a gauge-skip.json: each one genuinely has no reading
because of this exact ambiguity, so each deserves the signal
(decision:skip-sidecar-fanout-and-clear -- unlike a gauge.json reading,
a diagnostic fact about why nothing was written can never cross-write a
misattributed value).

calls internal: _bind x2, _hook_data
calls stdlib: json.loads x2, builtins.isinstance
reads internal: gw x3, _FIXTURE
reads stdlib: json (module) x2, builtins.str
unresolved: 9 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
