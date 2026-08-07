# G2 Implementer Rework 1

Use `constellation-implementer` to resolve the four reproducible P1 findings in `.agent-work/issue-418-iterative-planning/g2-review/REVIEW_RESULT.md`. Preserve the frozen G2 contract and lean/offline design.

## Required TDD Rework

Add the four adversarial cases to `tests/test_replan.py` before production edits, prove a causal red, then make the identical focused command green:

```bash
uv run python -m pytest -q tests/test_replan.py tests/test_install_constellation.py tests/test_write_a_skill.py
```

1. Because the frozen result has a singular escalation object, fail fast when one packet proposes material changes to more than one distinct fixed boundary; for one fixed boundary, require the escalation boundary and typed proposed value to match it exactly.
2. Reject any `unlaunched_items` entry of kind `issue` whose ID collides with a launched current-wave issue identity.
3. Accept duplicate nonempty strings wherever the exact G1 contract accepts them, including parked possibilities; keep uniqueness only for true identity partitions.
4. Validate rewritten full-G1 issue replacements inside the assembled applicable result graph so dependencies targeting issues in the result current wave are valid, while genuinely dangling/cyclic graphs still fail.

Re-run the reviewer's adversarial probe and registration rail. Update contract prose only where needed to state the single-fixed-boundary-per-packet consequence of the singular schema. Recompute the exact ordinal path+byte digest from the final inventory and refresh `IMPLEMENTER_RESULT.md` with the new causal red/green evidence, digest, scope, and feedback. Do not edit review artifacts, G3 lifecycle prose, tracker/network code, archives/history, or unrelated dirty changes. Write the result at the existing G2 implementer result path and report to `/root`.
