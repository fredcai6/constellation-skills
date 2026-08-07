# scripts.checklist_engine:attest
function, scripts/checklist_engine.py:2254, 65 lines

```python
def attest(cl: dict, iid: str, cond_id: str, which: str, note: str | None, evidence_id: str | None = None) -> str
```

Satisfy a condition by attestation.

Two paths:
- `check: null` (qualitative): the agent's manual verification stands in for a
  mechanical check — set `satisfied` from the note. Unchanged legacy behavior.
- `check.kind == "artifact"`: satisfy the postcondition **by reference** to an
  already-attached artifact (`--evidence <id>`), instead of re-attaching the
  same artifact to a sibling task. The engine still enforces mechanism: the
  referenced evidence must EXIST, be of the required `evidence_type`, and match
  the required `match` fields. It never lets an agent assert an artifact out of
  thin air (that is what a `check: null` attest does, not this).

`command` / `git-change-policy` checks stay engine-checked and refuse attest.

The requested `which` list is searched FIRST (an explicit `--which` still wins),
then the OTHER condition list as a fallback — precondition ids (`p*`) and
postcondition ids (`c*`) are disjoint, so a bare `attest <id> --cond c1` (default
`--which preconditions`) still resolves a postcondition without forcing the caller
to pass `--which postconditions`. If the cond is in neither list, the error names
both.

calls internal: EngineError x7, _find_evidence, task
calls stdlib: builtins.all
unresolved: 13 calls (dispatch-unknown-base)

referenced by: 1 sites, this module only
