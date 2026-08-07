# G2 Review Result

gate_id: g2  
verdict: BLOCK  
reviewer_identity: /root/g1_reviewer acting as fresh G2 constellation-reviewer; distinct from G2 implementer  
reviewed_diff_digest: sha256:bcac2c18ac5a6d88883f6123d173b72d4f020fd457b42b4b04268674a481abd5

## Assigned Gate

`g2 — Replanning capability`

## Result

`BLOCK`

The exact 11-path digest matches and the lean/offline core is sound, but four reproducible public-contract defects prevent approval.

## Ranked Blockers

1. **[P1] Not every fixed-boundary delta is escalated.** A result containing material changes to both `intent_and_why` and `fixed_decisions` is accepted with one escalation naming only `intent_and_why`. `_validate_escalation` requires the singular boundary to match *any* fixed change, leaving the second delta uncovered. This violates “any fixed delta requires escalation.”
2. **[P1] Launched and unlaunched issue identities can collide.** `verify_replan_input` accepts `unlaunched_items=[{"id":"A","kind":"issue"}, ...]` when `A` is already a launched current-wave issue. Completed/open are partitioned internally, but unlaunched issue identities are never checked against that partition.
3. **[P1] Valid exact-G1 nested values are rejected.** G1 permits arrays of nonempty strings with repeated values. Replan's shared `_strings` adds an uncontracted uniqueness rule, so a G1-valid `parked_possibilities=["same","same"]` input cannot be preserved as `revised_parked`.
4. **[P1] Full G1 issue replacements lose graph context.** A rewritten issue `U-issue` with `blocks=["B"]` is rejected even when `B` exists in the result current wave. `_validate_issue_replacement` replaces the synthetic plan's entire issue list with only the replacement, making every external dependency appear dangling. This is not validation of the replacement in the applicable output graph.

All four cases are reproduced by:

```text
uv run python .agent-work/issue-418-iterative-planning/g2-review/adversarial_probe.py
ACCEPTED two fixed deltas with only one escalation
ACCEPTED launched/unlaunched identity collision
REFUSED exact G1 parked shape with duplicate nonempty values: result.revised_parked must not contain duplicates
REFUSED G1 issue replacement whose dependency exists in the result wave: ... blocks target 'B' names no known issue
```

## Handoff Compliance

Partial. The skill, templates, renderer, four decisions, dispositions, repair/stop rules, typed single-boundary escalation cases, registration, and offline behavior match the handoff. Exact-G1 compatibility, complete identity partitioning, and complete fixed-delta escalation do not.

## Scope Drift

Pass. The exact 11-path inventory contains only the lean replan skill/verifier/templates/docs, registration/index updates, and focused tests. No checklist engine, tracker mutation, compatibility alias, portfolio policy, or G3 lifecycle wiring was introduced.

## Evidence Verdict

- Digest helper: exit 0, exact match `sha256:bcac2c18…`.
- Focused suite: exit 0, `133 passed, 407 subtests passed in 13.85s`.
- Registration: exit 0, `skill ok: replan is registered, mechanically clean, and installs (--dry-run)`.
- Scoped helper wiring search found executable callers for `verify_replan_input`, `verify_replan_result`, `render_replan_markdown`, and `main`.
- Scoped `git diff --check`: exit 0.
- Template CLI: exit 0 and emitted nonempty Wave review and Current planning truth Markdown.
- Adversarial probe: exit 0 and exposed the four blockers above. The focused suite does not cover them, so its green result is insufficient for the frozen claim.

## Per-Check Findings

- `r0-context`: PASS — context loaded and frozen digest matched before review.
- `r1-handoff`: FAIL — four frozen-contract defects reproduced.
- `r2-scope`: PASS — exact inventory and exclusions respected.
- `r3-evidence`: FAIL — claimed positive evidence reproduces but omits the failing adversarial cases.
- `r4-quality`: FAIL — invalid identity/escalation states pass while valid exact-G1 values fail.
- `r5-reconciliation`: FAIL — Map Impact overstates strictness, identity stability, and escalation coverage.
- `r6-fowler`: FAIL — feature envy flagged in synthetic whole-plan nested validation; the lost graph context causes blocker 4. Primitive JSON is standards-overridden.
- `r4a-schema`: FAIL — exact-G1 compatibility defects 3 and 4.
- `r4b-decisions`: PASS — four exits, repair/stop, disposition completeness, action matching, and evidence-only/drop rules.
- `r4c-identity`: FAIL — launched/unlaunched collision accepted.
- `r4d-escalation`: FAIL — one escalation can leave another fixed delta uncovered.
- `r4e-offline`: PASS — CLI/renderer are read-only and network/tracker-free.
- `r4f-goodness`: FAIL — prose is sharp and honest, but bounded evidence and independent-review compatibility are not met by the verifier.
- `r4g-lean`: PASS — remains a lean agent-authored judgment contract.

## Code/Doc Quality

The skill prose is concise, actionable, explicit about negative space, and has a sharp completion rule. The verifier is readable and side-effect-free. The primary design issue is using synthetic whole-plan mutation to validate nested G1 values; that both imports extra constraints and discards real graph context.

## Map Impact Verdict

- **Evidence supports claimed change:** Partially; core behavior does, strict completeness does not.
- **Constraints not violated:** Scope/offline/lean constraints pass; exact-G1 and fixed-boundary constraints fail.
- **Notes match the diff:** Structural notes match; capability guarantees are overstated.
- **Decision candidates surfaced:** No new authority decision is needed; these are frozen-contract implementation defects.
- **Durable context routed:** Rework belongs inside G2, not Cartographer/Triage.

## Reconciliation Check

No architecture map exists. README/index registration is accurate. Reconcile the verifier against the exact G1 public seam before G2 integration; G3 remains correctly out of scope.

## Required Rework

- Enforce a disjoint launched/current versus unlaunched-issue identity partition.
- Ensure every fixed material delta is represented by escalation. With a singular escalation schema, fail fast on multiple distinct fixed boundaries or revise the frozen result shape through proper authority.
- Separate string-array shape validation from identity-list uniqueness so exact G1 arrays remain accepted.
- Validate issue replacements in the assembled applicable graph, not a synthetic one-issue plan.
- Add each adversarial case to `tests/test_replan.py`, then refresh the digest and dispatch a fresh independent review.

## Out-of-Scope Observations

- None.

## Workflow Feedback

- **Handoff gaps:** “Every fixed-boundary delta requires escalation” conflicts with a singular `escalation` object when more than one fixed surface changes; the handoff should explicitly require at most one fixed boundary per packet or define an escalation array.
- **Context rediscovered:** The exact G1 `_strings` semantics had to be inspected directly to determine that duplicates are valid nested G1 values.
- **Instructions improvised around:** Project doctrine says run `python`, but this environment exposes the project interpreter through `uv run python`. Reviewer-only adversarial evidence was persisted under the assigned G2 review work area.
- **What would have made this easier:** Add cross-partition identity and assembled-graph replacement rules explicitly to the frozen schema, plus an adversarial test matrix in the handoff.

## Return Status

`complete`
