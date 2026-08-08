# Implementer Handoff — g2-implement

## Gate
`g2-implement` (execute.json, work-id `b433-render-directives`, issue #433)

Worktree, and the only place to work: `C:/Programs/constellation-skills-wt/r418-433`. Absolute paths.
`g1` is already integrated in the working tree: `directives` now renders, and there is a
`RenderDirectives` test class. Do not undo any of it.

## Task

Make `tests/test_checklist_engine.py`'s `class TaskFieldCompleteness` able to **FAIL** for the shapes
the corpus really carries. Today it cannot: `directives` sits in `_EXCLUDED_FIELDS`, and even
un-excluded, `_flatten` returns `[]` for the nested-dict shape every populated corpus block carries —
so the inner loop body never runs, the property asserts nothing about the field, and it reports green.
That is a check that cannot fail, and it is the exact defect class this issue exists to close.

Five changes, **all inside that class**, plus one small named carry-over in the engine (section
"Carry-over" below).

**(1) Un-exclude the field.** Remove `"directives"` from `_EXCLUDED_FIELDS` and replace its `KNOWN
GAP` comment with a note that it renders as of #433. Every remaining exclusion keeps its stated
per-entry reason — an exclusion set with a reason per entry is the honest form; do not drop any.

**(2) Replace `_flatten` with a TOTAL leaf extractor.** It must recurse dicts and lists to any depth
and stringify scalars, returning `[]` only for `None` and empty containers. This is what makes the
nested-dict shape assertable at all. Name it for what it now does.

**(3) Replace the single `checked_any` flag with a PER-FIELD ledger.** Record which fields the loop
actually asserted on, then assert that set **equals** the set of populated non-excluded fields. One
flag for the whole loop lets any field cover for any other: a recursive extractor alone still reports
green when a future field yields no text. The ledger is what makes vacuity a typed failure.

**(4) The change that actually closes the class.** The loop runs over the **fixture's** keys. A Task
field added to the engine later and forgotten in the fixture is absent from the loop, absent from the
ledger's expected set, and passes green — the identical forgetting failure the property exists to
catch. Assert the fixture's key set is a **superset** of the engine's own canonical Task builder
`_build_amend_task` (`scripts/checklist_engine.py:~2040`, mirrored by `append()` at `~2252`), so a
field added to the engine's Task shape and forgotten here fails mechanically.

State the **residual limit** honestly in the class docstring rather than implying coverage the
property lacks: this closes the hole for fields the *engine* introduces; a field introduced only by a
template and never by either builder still needs a human to add it to the fixture.

**(5) Add an in-suite NEGATIVE self-test.** Feed the same assertion path a render with the
`directives` block stripped out, and assert it raises, with the failure message **naming
`directives`**. A property only ever observed passing is a check that cannot fail; this is the durable
machine proof that it can.

## Carry-over from the g1 review — one line in the engine, with its own test

The g1 reviewer found the fix reproducing its own defect class in miniature: in
`scripts/checklist_engine.py`'s `_render_directive_lines()`, the flat-list branch reads

```python
return [f"  {item}" for item in directives if isinstance(item, str)]
```

so a non-string item is **silently dropped** — contradicting the helper's own docstring rule and
diverging from `_render_anchor_lines`, which does not filter its list branch. Make it total by
sending each item through `_directive_leaf`, and add one test for a list carrying a non-string item.
This is authorized, bounded, and the only engine edit in this gate.

## Protected Intent

- Every other exclusion in `_EXCLUDED_FIELDS` keeps its stated reason. Do not silently widen or
  narrow the set beyond removing `directives`.
- The test's leaf extractor stays **independent** of the renderer's `_directive_leaf` /
  `_render_directive_lines`. Do not import or share them. A shared bug would render nothing and assert
  nothing, in agreement, and both sides would report green.
- The `ACTIVE` first line stays byte-identical; `GoldenOutputBriefing` and `ShippedTemplates` green.

## Test Mode

**TDD in the strong sense: the red-proofs are the deliverable.** After the class is rewritten, break
the world three ways by hand, run the suite each time, and paste the **REAL output** into the result.
Revert each break before the next.

- **R2** — make the extractor return `[]` for dicts (the old `_flatten` behaviour). Expect the
  **ledger set-mismatch** to fail, NOT a green run. Green here means the ledger is not doing its job.
- **R4** — add a throwaway populated field to the fixture whose value flattens to nothing. Expect it
  to fail **by name**.
- **R5** — add a field to `_build_amend_task` in `scripts/checklist_engine.py` and NOT to the fixture.
  Expect the superset assertion to fail **by name**.

Each capture must show the command, the assertion message, and the real exit code.

## Close Criteria

- `directives` is out of `_EXCLUDED_FIELDS`; every remaining exclusion still carries its reason.
- The extractor is total; the ledger is per-field; the superset assertion against `_build_amend_task`
  is in place; the class docstring states the residual limit.
- The in-suite negative self-test exists and asserts the raise names `directives`.
- R2, R4 and R5 each produced a real, pasted red.
- `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py` exits **0** with all
  breaks reverted.
- The flat-list carry-over is total, with a test.

## Allowed Scope

- `tests/test_checklist_engine.py` — `class TaskFieldCompleteness` in full, plus one added test for
  the flat-list carry-over (put it with the `RenderDirectives` class).
- `scripts/checklist_engine.py` — ONLY the one line in `_render_directive_lines`'s list branch named
  above, and its docstring if the rule statement needs to match.

## Specific Exclusions

- `docs/CHECKLIST_SCHEMA.md` — gate `g3-schema` owns it. Do not touch, even though you will notice it
  is wrong about the `directives` type.
- Any other engine change. `state()`, `render_human()`, `_directive_leaf` and the rest of
  `_render_directive_lines` are settled at g1.
- `scripts/collect_feedback.py` (#464), `episodes/` (#460),
  `scripts/verify_worktree_precondition_coverage.py` (#436) — concurrent sibling issues this wave.
- The gate schema itself.

## Constraints

- No new dependency.
- Match the surrounding test module's idiom and comment density.
- The ledger's failure message must name the offending field — "the loop asserted nothing" is the
  message this change exists to replace.

## Map Anchors (inbound)

- **Structural:** `tests/test_checklist_engine.py` — `class TaskFieldCompleteness` (was ~3958, moved
  by g1's insertion; **find it by symbol name, not line number**), `_EXCLUDED_FIELDS`, `_flatten`;
  `scripts/checklist_engine.py` — `_build_amend_task` ~2040, `append()` ~2252,
  `_render_directive_lines` ~1689.
- **Capability:** the Task field contract — `docs/CHECKLIST_SCHEMA.md`'s Task table is the enumeration
  the property is cut against, but the **engine's own builder** is the enumeration that can be
  checked mechanically. That substitution is finding 1 of the cold plan critic and is the point of
  change (4).
- **Constraints/assumptions:** `constraint:a-check-that-cannot-fail` — a guard whose output is
  identical in the healthy and the defective world is not a guard.
- **Decision anchors:**
  - `decision:per-field-ledger-is-the-class-fix` — the durable part is the per-field record of what
    the property actually asserted, not the flattener.
    `@grade: settled/measured · leans g2 · settle: the R4 red-proof — a field whose value flattens to nothing must fail by name`
  - `decision:independent-extractor` — the test's extractor is not the renderer's.
    `@grade: settled/human · leans g2`
- **Evidence expectations:** `claim:the-completeness-property-fails-when-a-populated-field-is-unrendered`.
- **Map confidence flags:** no `docs/architecture` map exists; orientation DEGRADED by standing
  condition. `docs/CHECKLIST_SCHEMA.md` is known stale on the `directives` row — do not cut the
  property against that row.

## Deliverable Path Check

- **Committed** — `tests/test_checklist_engine.py`, `scripts/checklist_engine.py`;
  `git check-ignore -v` exits 1 (not ignored).
- **Committed** — `.agent-work/b433-render-directives/crew-handoffs/g2-implement-IMPLEMENTER_RESULT.md`
  and any capture under `.agent-work/b433-render-directives/evidence/`; same, exit 1. New files:
  they appear in `git status`, not in `git diff`, until staged.

## Required Evidence

**Load-bearing — prove rigorously:**

1. The three red-proofs R2, R4, R5, each with its exact command, the real assertion message, and the
   real exit code. This is the gate's whole point: a property observed only passing is a check that
   cannot fail.
2. `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py; echo "EXIT=$?"` with
   every break reverted — summary line **and** real exit code. Do not infer green from the summary.
3. Proof the working tree is clean of the breaks afterwards: `git diff --stat` showing only the two
   intended files.

**Confirmatory — spot-check:**

4. `GoldenOutputBriefing` and `ShippedTemplates` still green (covered by 2, name them).
5. The flat-list carry-over test.

## Wiring Grep

```bash
grep -rn "_build_amend_task" --include=*.py C:/Programs/constellation-skills-wt/r418-433/tests
```

State the count. Zero means change (4) is not actually reaching the engine's builder, which is the
whole mechanism — a stop condition.

## Verification Commands

```bash
cd C:/Programs/constellation-skills-wt/r418-433
FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests/test_checklist_engine.py; echo "EXIT=$?"
```

Never `py` for pytest (#454). `FORCE_COLOR=3` produces false reds.

## Suggested Model Tier

**Stronger.** The deliverable is falsifiability itself, and three of the five changes exist because a
cold critic showed the obvious version passes green in the defective world.

## Authority

Already decided, not yours to reopen: the per-field ledger rather than the flattener alone; the
extractor's independence from the renderer's; the superset assertion against `_build_amend_task`; the
negative self-test in the suite. The ledger's data structure and the exact message wording are yours.

## Stop Conditions

Stop and return if: allowed scope must be exceeded; an exclusion must be touched; a red-proof cannot
be produced or comes back GREEN (that is a finding, report it, do not paper over it); or a decision
outside the authority above is needed.

## Return Format

Return IMPLEMENTER_RESULT: completed slice, files changed, test mode satisfied, evidence produced
(R2/R4/R5 verbatim), assumptions used, stop conditions hit, out-of-scope observations, workflow
feedback.

Write it to:
`C:/Programs/constellation-skills-wt/r418-433/.agent-work/b433-render-directives/crew-handoffs/g2-implement-IMPLEMENTER_RESULT.md`
