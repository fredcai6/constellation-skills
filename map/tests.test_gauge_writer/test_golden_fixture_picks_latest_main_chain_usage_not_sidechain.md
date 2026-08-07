# tests.test_gauge_writer:test_golden_fixture_picks_latest_main_chain_usage_not_sidechain
function, tests/test_gauge_writer.py:97, 26 lines

```python
def test_golden_fixture_picks_latest_main_chain_usage_not_sidechain(proj)
```

The fixture's trailing lines 5-6 (a subagent's own context, isSidechain:

true) are LATER in the file AND in time than the real main-chain answer
on line 4, and carry BIGGER usage totals. Because
_iter_tail_lines_reverse scans from the end of the file, it hits both
sidechain lines FIRST and must skip both (find_latest_usage's
isSidechain-continue branch) before it reaches line 4's answer -- so a
correct result here is only possible if that skip actually ran, not an
artifact of the true answer already being the last line.

calls internal: _bind, _hook_data
calls stdlib: json.loads
calls third-party: pytest.approx
reads internal: EXPECTED_FILL, EXPECTED_MODEL, _FIXTURE, gw
reads stdlib: json (module)
reads third-party: pytest (module)
unresolved: 4 calls (dispatch-unknown-base)

referenced by: none found
