# Implementer Handoff — `g2` · the role specs

**Work id:** `epic-559/c2-generate-the-spine` · **Gate:** `g2-implement` · **Model:** Sonnet
**Dispatched by:** the Commander (delegated) under Admiral `admiral-epic-418-followon`.
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c2-generate-the-spine`, branch
`epic-559/c2-generate-the-spine`.

## Gate

`g2` of `.agent-work/epic-559/c2-generate-the-spine/execute.json`.

## Task

Write the **first two real role specs** in the format `g1` shipped, generate a spine from each, and
answer the question this whole mission turns on.

1. `specs/implementer.spine.toml` — a `gated` spec whose intent matches the shipped
   `skills/implementer/templates/IMPLEMENTER_PLAN.template.json`.
2. `specs/reviewer.spine.toml` — a `survey` spec whose intent matches the shipped
   `skills/reviewer/templates/REVIEW_SURVEY.template.json`.
3. Generate both, committing the output:
   - `.agent-work/epic-559/c2-generate-the-spine/generated/implementer.spine.json`
   - `.agent-work/epic-559/c2-generate-the-spine/generated/reviewer.spine.json`
4. Write every disagreement between a generated spine and its shipped template as a **finding** in
   `.agent-work/epic-559/c2-generate-the-spine/notes-2.md`.
5. Do the one carried-over cleanup in §Carried finding below.

**Read first, in this order:** `.agent-work/epic-559/c2-generate-the-spine/DESIGN_NOTE.md` (the frozen
format — §3 the spec shape, §4 the five kinds and their exact compiled output, §5 handback, §6 claims),
then `scripts/generate_spine.py`, then the two shipped templates you are matching in intent.

## Protected Intent — and the question you are actually here to answer

The mission exists because a check is a shell string typed from memory and a wrong one exits 0. `g1`
built a format with **no raw-command field**. `g2` is where we find out whether that was true or merely
tidy.

> **The settling question: does the role spec still ask its author to type a shell command from
> memory?**

You are the author. **Report exactly what you typed**, verbatim, for every postcondition in both specs,
and say for each whether any part of it was recalled rather than derived — a flag name, a path, a module
name, a selector. If you had to look something up, say where you looked. If you wanted a check the five
kinds could not express and worked around it, **say so plainly and say what you wanted** — that is the
single most valuable sentence you can write in this gate, and it is worth more to us than a clean
result.

**A measured negative is a complete deliverable here.** If the defect moved rather than went, we ship
that finding. Do not manufacture a success.

## Test Mode

```
env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests
```

`python`, not `python3` — on this host `python` has pytest importable and `python3` does not. Unsetting
the three spine variables matters: `scripts/mcp_spine_server.py` reads `SPINE_FILE` at import time.
Baseline: **2765 passed, 3 skipped, 1121 subtests**.

## Close Criteria

1. Both specs exist and both generate, exit 0.
2. **Both generated spines are clean under the oracle with ZERO undecidable:**
   ```
   cd /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine && python scripts/validate_spine.py .agent-work/epic-559/c2-generate-the-spine/generated/implementer.spine.json .agent-work/epic-559/c2-generate-the-spine/generated/reviewer.spine.json --root /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine
   ```
   must print `OK` for both and print **no** `undecidable` line. This is the gate's own machine check.
3. **Neither generated spine carries an unresolved placeholder outside the resolver-owned families.**
   The shipped `IMPLEMENTER_PLAN.template.json` carries `<exact test command>` at `m1.c2` — the exact
   defect this mission exists to make unauthorable. Your generated implementer spine must not have an
   equivalent. Show what you wrote instead.
4. **Neither generated spine carries a `falsifiable-all-null` gate.** The shipped `m0-context` and
   `r0-context` gates do (they are two of the 23 baseline faults). Show how the `qualitative` kind's
   required `because` handled it, and paste the emitted statement so the stated form is visible.
5. **Every gate in both generated spines carries the handback contract.** Assert it, don't assume it.
6. **At least one gate carries a large claim**, so the escalation and the rollup are exercised on a real
   spec rather than only in a unit test. Choose a claim that is genuinely large — do not invent a
   throwaway one to tick the box; if neither role spec has a genuinely large claim, say so and put the
   claim where it honestly belongs.
7. `notes-2.md` records every generated-vs-shipped disagreement as a finding.
8. `python scripts/validate_spine.py --sweep --root .` still reports exactly **23** fault lines. You are
   editing no shipped template.
9. The full suite passes.

## Carried finding — from `g1`'s cold review

`scripts/generate_spine.py:51` imports `_RESOLVER_OWNED_TOKEN_RE` from `init_work_area` and **never uses
it**. The reviewer found this by walking every `ast.Name` node. DESIGN_NOTE §4 cites that regex to
justify emitting `<repo-root>` unresolved, but the justification lives in prose and is wired to nothing.

**Do not simply delete the import. Turn it into a real assertion**, so the design note's claim is pinned
by a test rather than by a sentence: a test asserting `_RESOLVER_OWNED_TOKEN_RE.fullmatch("<repo-root>")`
is truthy and that a non-resolver token like `<exact test command>` is not. If after trying you judge
deletion genuinely better, delete it and say why.

## Allowed Scope

- **Create** `specs/implementer.spine.toml`, `specs/reviewer.spine.toml`.
- **Create** the two generated spines under
  `.agent-work/epic-559/c2-generate-the-spine/generated/`.
- **Create** `.agent-work/epic-559/c2-generate-the-spine/notes-2.md`.
- **Modify** `scripts/generate_spine.py` and `tests/test_generate_spine.py` **only** for the carried
  finding above, or for a defect you find while authoring the specs. If you change the generator for any
  other reason, stop and ask.

## Specific Exclusions

- **Do not edit any shipped template** under `skills/*/templates/`. If your generated spine and the
  shipped template disagree, the generator is the thing under construction and the disagreement is a
  **finding** — that is `decision:no-template-edited-to-pass`, ruled by the Admiral.
- **Do not modify `scripts/validate_spine.py`.** If your spec would only validate by moving the oracle,
  **stop and return** — moving the oracle is a float to the Admiral, not a patch. This is a hard stop.
- Do not modify `scripts/checklist_engine.py` or the engine's on-disk format.
- Do not add a raw-command escape to the spec format. If you need one, that is the honest-null finding
  — report it, do not build it.
- Do not run `scripts/install_constellation.py` (#539). Do not touch `settings.json`. Do not push. Do
  not `git add -A` — `.agent-work/` is tracked here; stage by name.

## Constraints

- The two specs express the shipped templates' **intent**, not their bytes. You are not producing a
  byte-diff-clean replica; you are answering "can this format say what these two roles actually need to
  say."
- A `<placeholder>` is legitimate in a template and a fault in an instance. The resolver-owned families
  (`<work-id>`, `<repo-root>`, `<*-skill-dir>`, `<*-session-id>`) are fine — `init_work_area.resolve_spine`
  substitutes them before a spine is driven. Anything else is a fault.
- Quote any `-k` selector you write anywhere. An unquoted one is one of the four defects that motivated
  this mission — though in the `pytest` kind you should not be writing shell at all.

## Map Anchors (inbound)

No architecture map exists here (`map_orient` → `DEGRADED-UNPARSEABLE`). Your entry points are the
declared substitutes, hash-pinned in `.agent-work/epic-559/c2-generate-the-spine/map-orientation.json`:

- **`docs/CHECKLIST_SCHEMA.md`** — primary. The `Task` table, the `Condition` table, the `gated` vs
  `survey` distinction (a survey item **is** the check and needs a `result` field), and §Rendering.
- `scripts/validate_spine.py` — the oracle, especially `_shape_task_faults` for survey rules and
  `_fault_unresolved_placeholder` for which tokens are accepted.
- `skills/implementer/templates/IMPLEMENTER_PLAN.template.json` and
  `skills/reviewer/templates/REVIEW_SURVEY.template.json` — the intent you are matching. Read, never
  edit.

## Deliverable Path Check

`git check-ignore` exits 1 (not ignored) for `specs/implementer.spine.toml`,
`specs/reviewer.spine.toml`, and the `generated/` outputs — verified by the Commander before dispatch.
`specs/` is a new top-level directory; confirm nothing in the repo's discovery or install machinery
breaks on it (the full suite is your check).

## Required Evidence

Paste commands and their output, not descriptions:

1. Both generation runs, exit 0.
2. The oracle on both generated spines: two `OK`s, no `undecidable` line.
3. The emitted `m1` test-command check from the generated implementer spine, next to the shipped
   template's `<exact test command>` — the before/after that shows the placeholder is gone.
4. The emitted context-gate postcondition showing the stated qualitative form, next to the shipped
   template's silent `check: null`.
5. A command proving every gate in both spines carries the handback contract.
6. The gate carrying the large claim: its injected `c-escalation` and the rollup on the last gate.
7. `--sweep` fault-line count.
8. The full suite.
9. **The settling-question report** (§Protected Intent) — verbatim, per postcondition.

## Verification Commands

```
cd /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine && env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests

cd /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine && test $(python scripts/validate_spine.py .agent-work/epic-559/c2-generate-the-spine/generated/implementer.spine.json .agent-work/epic-559/c2-generate-the-spine/generated/reviewer.spine.json --root /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine | grep -cE 'OK$') -eq 2

test $(cd /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine && python scripts/validate_spine.py --sweep --root /home/tommy/projects/constellation-skills-wt/c2-generate-the-spine | grep -cE '^  \[') -eq 23
```

## Suggested Model Tier

Sonnet. The human's instruction is verbatim: *"prefer sonnet crews."*

## Authority

The dispatching Commander (delegated), under Admiral `admiral-epic-418-followon`.

## Stop Conditions

- Your spec would only validate if `validate_spine.py` moved — **hard stop**, return, do not patch.
- The five kinds cannot express something a role spec genuinely needs — **do not add a raw-command
  field**; write the finding and return.
- A shipped template and your generated spine disagree in a way that looks like a real defect in the
  shipped template — record it as a finding, do not fix it.
- Your scope would have to grow past the files above.

## Return Format

Write the full `IMPLEMENTER_RESULT` to
`.agent-work/epic-559/c2-generate-the-spine/crew-handoffs/g2-implement-result.md` **before you end your
turn** — that write is the delivery.

Open with **`Return status: complete`** on its own line, lowercase (never `COMPLETE`) — the engine's
artifact match is exact dict equality. Then the evidence above, the settling-question report, every
finding, anything you decided where the design note was silent, and a **Workflow Feedback** section.
