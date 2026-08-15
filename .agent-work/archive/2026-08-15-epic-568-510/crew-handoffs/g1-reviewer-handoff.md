# Reviewer Handoff

## Gate

`g1-review`

## Task

Independently review the #510 pending-HARD advisory correction and direct regression. Verify the pending-HARD text teaches attach refresh-request → start → advance with `--why`; the test executes that sequence and proves successor `current` retains the digest.

## Allowed Scope

Review only the diff in `scripts/checklist_engine.py` and `tests/test_checklist_engine.py`, plus the implementer result at `.agent-work/epic-568-510/crew-handoffs/g1-implementer-result-attempt-2.md`.

## Constraints

- Runtime guard, verb, default, state, and schema behavior must remain unchanged.
- Reject scope expansion or missing red/green proof.

## Verification

```bash
python -m pytest tests/test_checklist_engine.py -k TripHardGuardsBeginNotClose -q
git diff --check
git diff -- scripts/checklist_engine.py tests/test_checklist_engine.py
```

## Return

Write `REVIEW_RESULT` with verdict `APPROVE` or `BLOCK` to `.agent-work/epic-568-510/crew-handoffs/g1-reviewer-result.md`; include exact evidence and workflow feedback. Do not modify source, commit, or push.
