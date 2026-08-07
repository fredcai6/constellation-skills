# Reviewer Handoff

## Gate

`g2`

## Review Target

Independently review the 11-path Gate 2 change identified by `sha256:bcac2c18ac5a6d88883f6123d173b72d4f020fd457b42b4b04268674a481abd5`. Read the frozen G2 imperative in `.agent-work/issue-418-iterative-planning/execute.json`, the implementer result, and the persisted digest inventory/helper. Use `constellation-reviewer` and drive its survey to terminal state.

## Required Review

- Recompute and match the exact ordinal path+byte digest before judging.
- Reproduce `uv run python -m pytest -q tests/test_replan.py tests/test_install_constellation.py tests/test_write_a_skill.py`.
- Verify exact strict v1 input and result schemas, including every nested G1 shape, type, enum, cardinality, identity partition, and fail-fast rule in the frozen G2 imperative.
- Exercise all four decisions and their semantic rules: repair holds current wave/forecast, stop alone permits null current wave, evidence-only/drop cannot create issues, and all input discrepancies/unlaunched items have exactly one valid disposition.
- Verify launched issue identities and confirmed fixed fields cannot change in applicable output.
- Verify each of five escalation boundaries uses the correct proposed-value type and makes fixed-boundary deltas non-applicable.
- Inspect renderer and CLI for genuinely offline operation and nonempty review/epic output.
- Apply the semantic skill-goodness subset: completion sharpness, actionable steps, negative space, epistemic honesty, bounded evidence, and independent-review compatibility.
- Confirm the skill remains a lean wave-decision contract and does not introduce an autonomous portfolio/policy engine, tracker mutation, compatibility alias, or G3 lifecycle wiring.
- Run scoped public-helper wiring searches and `git diff --check` for the exact inventory.

## Scope

Review only the 11 paths listed in `.agent-work/issue-418-iterative-planning/g2-implement/G2_DIGEST_PATHS.txt`, plus tests/evidence needed to establish behavior. Preserve unrelated dirty changes. Do not edit production code. No live GitHub/network writes.

## Verdict Rules

Return `APPROVE` only if the frozen contract and semantic goodness checks are met and the digest matches. Otherwise return `BLOCK` with ranked, reproducible findings. The result must include `gate_id: g2`, reviewer identity, and `reviewed_diff_digest`.

## Result

Write `.agent-work/issue-418-iterative-planning/g2-review/REVIEW_RESULT.md`, release the reviewer checklist lease, and report to `/root`.
