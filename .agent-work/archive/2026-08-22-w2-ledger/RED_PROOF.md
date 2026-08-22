# Red-proof — #503 waive() authority defects — pinned to shipped SHA

**Shipped SHA:** `0427898a8b2e8b57a4c2761dc525dea4d4b6b9f8` (HEAD of `epic-569/w2-ledger` at
archive time, after g1-g4).

**Base (pre-fix) SHA:** `9d5aac6d` — the launch order's own stated Base, verified green by the
Admiral (3622 passed, 6 skipped, 0 failed).

## Repro

Fixture: a `waive`-able postcondition declaring `override_policy.authority: "human"`, waived with
`--authority commander`.

```python
cl = {"type": "gated", "tasks": {"g1": {"id": "g1", "postconditions": [
    {"id": "c1", "check": None, "satisfied": False,
     "override_policy": {"allowed": True, "authority": "human", "reason_required": False}}
], "preconditions": []}}}
E.waive(cl, "g1", "c1", "postconditions", authority="commander", reason=None, forced=False)
ev = cl["tasks"]["g1"]["evidence"][-1]
```

## RED — `git show 9d5aac6d:scripts/checklist_engine.py`

```
produced_by: human                    <- hardcoded, ignores the real authority ("commander")
authority_mismatch present?: False    <- the human/commander mismatch is silently dropped
```

Both are exactly issue #503's two named defects.

## GREEN — shipped SHA `0427898a`

```json
{
  "payload": {
    "cond": "c1", "authority": "commander", "reason": null, "forced": false,
    "authority_mismatch": true, "expected_authority": "human"
  },
  "produced_by": "commander",
  "ts": ""
}
```

`produced_by` echoes the real authority; the mismatch is recorded (`authority_mismatch: true`,
`expected_authority: "human"`); `waive` still returned success (`"waived g1.c1 by commander ->
e-g1-1"`, no exception) — the fix is report-only, per the standing epic rule that a brand-new
refusal ships non-blocking.

## Where this could fail (and how it's proven not to, in the shipped suite)

- `tests/test_checklist_engine.py`'s waive test class (`-k waive`, 34 tests) exercises this exact
  shape plus the match/absent-policy cases where neither field should appear.
- The dispatch-only chokepoint for the OTHER three ledger paths (`force-claim`/`force-release`/
  `waive` entries into `override_ledger`) is proven by an AST-based test asserting the exact caller
  graph (`test_compliance_ledger_write_site_is_unreachable_from_any_cli_verb`), not by this
  hand-rolled repro — this file demonstrates #503 specifically, the ledger unification's own proof
  lives in the test suite committed at `2895dc8b`/`87ea0655`.
