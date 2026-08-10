# Reviewer handoff — gate `g2-review`: DC4, same-gate equivalence as a property

**Work id:** `epic-418-followon/commander-424` · **Gate:** `g2-review`
**Worktree (read/verify only here):** `/home/tommy/projects/constellation-skills-wt/f-424`
**Branch:** `epic-418/f-424-mcp-door`
**Authority:** Commander for issue #424 (workstream F of epic #418), under a frozen Admiral launch
order.

## Task statement

Independently verify `tests/test_mcp_imperative_equivalence.py` against **DC4**:

> The CLI projection and the MCP tool result carry the **same imperative text** for **every gate that
> has one**.

The point of this gate is that **one gate matching once establishes nothing**. g1 already shipped a
byte-identity check for a single gate and it was confirmed able to fail. **That was the sample; this
is the population.** Verify the delivered check is genuinely a property over the whole shipped
template tree, discovered by walking it rather than from a hand-maintained list.

## How to inspect the diff

```
cd /home/tommy/projects/constellation-skills-wt/f-424
git show --stat 696caaea
git show 696caaea -- tests/test_mcp_imperative_equivalence.py
git diff fda35ec0..HEAD -- scripts/mcp_spine_server.py    # must be EMPTY
```

The implementer's account, with its exact commands and evidence:
`.agent-work/epic-418-followon/commander-424/crew-handoffs/g2-implementer-result.md`

## Close criteria — verify each yourself, do not take them on report

1. **Population, not sample.** The gates are enumerated by **walking** the shipped template tree
   (`skills/*/templates/*.template.json`), not from a hand-maintained list, so a template added later
   is covered automatically. The implementer reports **61 gates across 12 templates**. Reproduce that
   count yourself and confirm the walk really would pick up a newly added template.
2. **The loop asserts what it looped over.** The count is asserted non-zero and reported, with a floor
   guarding against a silent collapse to a near-empty set. Confirm a comparison over an empty or tiny
   set cannot report clean.
3. **Compared against behaviour, not text describing it.** Both arms render real output — a CLI
   `checklist_engine.py current` subprocess and a real `mcp_spine_server.py` server over JSON-RPC —
   rather than reading docstrings or `description=` fields.
4. **The property was demonstrated able to fail, with the mutation asserted as applied.** There is a
   permanent `PositiveControlTests` class plus a one-time live scratch demonstration. Verify the
   permanent control is not vacuous: **mutate something yourself and watch the property go red**, then
   restore.
5. **The door was not bent to fit the test.** `git diff fda35ec0..HEAD -- scripts/mcp_spine_server.py`
   is empty. A door changing its output to match a test is exactly the drift DC4 exists to detect.
6. No fenced file touched (`scripts/install_constellation.py`, `tests/test_feedback_tooling.py`,
   `tests/test_install_constellation.py`, `tests/test_run_skill_eval.py`, `tests/test_spine_rail.py`);
   `scripts/checklist_engine.py` diff empty; `settings.json` untouched at every scope; no issue
   closed; nothing promoted into `docs/agents/*`; `tests/test_mcp_identity.py` not edited.
7. Full suite **`0 failed`**. Baseline before this change was `2172 passed, 1 skipped, 1061 subtests`;
   the implementer reports `2177 passed, 1 skipped, 1061 subtests`, +5 for 5 new tests. Verify the
   arithmetic and confirm nothing was skipped, xfailed, or padded.

## The one finding I most want you to scrutinise

The implementer reported a **negative result, honestly and unprompted**, and it is the thing that
decides whether this gate is real:

> Mutating a real shipped template on disk does **not** turn the property red, because the CLI and MCP
> arms share one spine file per gate by design — the property is sensitive to **rendering-side**
> divergence, not source-data edits.

That is plausibly correct and plausibly the right target: DC4 is about the two **projections** of the
same gate disagreeing, so a shared source is the control, not the bug. **But it also narrows what this
check can catch, and I want that boundary drawn by you, not by me.** Specifically:

8. State plainly **which divergence modes this property would catch and which it would not**. Would it
   catch the MCP door truncating, re-wrapping, re-encoding, or stripping an imperative the CLI renders
   in full? Would it catch a divergence introduced in only one arm's rendering path? If the answer to
   those is no, the property is much weaker than DC4 claims and you should **BLOCK**.
9. Confirm the **permanent** `PositiveControlTests` exercises a divergence in the **rendering** path
   (the mode the property is actually sensitive to), not merely a synthetic string comparison that
   would pass regardless of how the door behaves.

## Verification commands

```
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_mcp_imperative_equivalence.py
cd /home/tommy/projects/constellation-skills-wt/f-424 && FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

## What I want from you, stated plainly

**BLOCK is a fully acceptable outcome and I will act on it rather than override it.** Two earlier
gates in this run were blocked by their reviewers on real findings, and both blocks held until
evidence resolved them. If the property is weaker than DC4 claims, if the count is inflated by gates
that do not really carry imperatives, or if the permanent control cannot actually fail — say so and
block.

If it holds, say `APPROVE` cleanly and do not manufacture a hedge.

## Reporting

Write your `REVIEW_RESULT` to:

```
/home/tommy/projects/constellation-skills-wt/f-424/.agent-work/epic-418-followon/commander-424/crew-handoffs/g2-reviewer-result.md
```

**Write that file before ending your turn — the write is the delivery.** State the verdict as a bare
`APPROVE` or `BLOCK` on its own line so it is machine-readable. Include a `## Workflow Feedback`
section, blunt and specific. Log out-of-scope finds as triage candidates rather than fixing them. If
you mutate anything to test it, restore the tree and confirm it is clean before ending your turn.
