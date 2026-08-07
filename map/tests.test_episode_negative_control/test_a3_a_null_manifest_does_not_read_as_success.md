# tests.test_episode_negative_control:test_a3_a_null_manifest_does_not_read_as_success
function, tests/test_episode_negative_control.py:862, 53 lines

```python
def test_a3_a_null_manifest_does_not_read_as_success(tmp_path)
```

Attack A3, now REACHABLE: every declared ref resolves to a missing file.

A3 scored green before this existed, but it passed through a hole — the control's
plan declared no `context_refs` at all, so there was no row that *could* go null. A
fixture that cannot reach the failing condition is as vacuous as a predicate that
cannot discriminate, so the condition is reached here deliberately and what happens
is asserted rather than assumed.

**The deliberate finding, stated in full.** `context-manifest-ref` remains CORRECT
under A3, and that is not a gap: the field is a byte-pin over the manifest's own
bytes, the bytes really did change, and the harness's independently computed OID
tracks them. What A3 was reaching for is a level down — whether the manifest's ROWS
are honest — and that is covered here by (1) and (2), not by the pin.

calls internal: _git x3, _ControlRun._run x2, _ControlRun, _ControlRun.manifest, _plan, _write_json, blob_oid, compare_manifest_rows, expected_rows
calls stdlib: builtins.dict, builtins.open, json.loads
calls third-party: episode_capture.mechanical_fields
reads internal: DECLARED_CONTEXT x2
reads stdlib: json (module)
reads third-party: episode_capture (module)
unresolved: 4 calls (dispatch-unknown-base), 2 reads (dispatch-unknown-base)

referenced by: none found
