# scripts.verify_issue_set:verify_issue_set
function, scripts/verify_issue_set.py:122, 15 lines

```python
def verify_issue_set(manifest: object, spec_text: str) -> None
```

Raise IssueSetError on any malformed condition; return None if the set is

well-formed. `spec_text` is the DESIGN_SPEC the set was cut from.

Order is deliberate: the spec-confirmation gate (rule 1) runs first — an
unconfirmed spec is refused before the manifest is even inspected.

calls internal: IssueSetError, verify_edges, verify_manifest_shape, verify_types
calls third-party: verify_spec_confirmed.verify_spec_confirmed
reads third-party: verify_spec_confirmed.SpecVerificationError
writes internal: verify_issue_set.manifest

referenced by: 1 sites, this module only
