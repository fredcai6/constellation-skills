# Cold reviewer handoff — B: instructions became checks (#562 and the template sweep)

**Work id:** `epic-559/b-instructions-to-checks` · **Gate:** `g2-review` · **Role:** reviewer
**Worktree:** `/home/tommy/projects/constellation-skills-wt/b-instructions-to-checks` (branch `epic-559/b-instructions-to-checks`)
**Under review:** commit `0ee69c94` against `main`@`9d593e0a`, plus `IMPLEMENTER_RESULT.md` and `CENSUS.md`.
**Your spine:** `.agent-work/epic-559/b-instructions-to-checks/REVIEW_SURVEY.json` — drive it item by item.

You are **cold**. You did not plan this and you are not here to agree with it.

## What the change was supposed to do

Move mandatory "run this script" instructions out of spine-template imperatives and into command
postconditions the engine runs, across all six shipped role templates. Plus fix #562 — a Commander
gate whose statement promises "no unresolved blockers" while its check proves only that an
`implementer-result` of some type arrived — and sweep for the same shape elsewhere.

The intent, in the human's words: *"the more we can remove from instructions and put behind tools
the better"*, because the target is a **less capable agent** than you. An instruction can be
misread or skipped; a check is simply true or not.

## The diff is four lines. Do not let that set your effort.

Three files, 4 insertions, 4 deletions. Two of those lines change what the engine will refuse, in
templates that govern **every future Commander and every future Admiral run**. A wrong line here
blocks real runs repo-wide. Review it at the weight of its blast radius, not its size.

## The question that decides the verdict

The #562 fix constrains the check to `match: {"status": "complete"}`. **Nothing in this repo tells a
Commander to attach a `status` field.** The implementer says so itself, in its own Assumptions
section: it inferred the convention by analogy from `review-result`'s `verdict` and could not find
it documented anywhere. Its own Out-of-scope note says *"a commander that doesn't independently
reinvent this convention will find `g1-implement.c1` permanently unsatisfiable."*

So the change may have converted a check that **cannot fail** into a check that **cannot pass**.
That is not an improvement; it is the same defect with the sign flipped, and it would block every
Commander implement gate in the repo.

Settle it with evidence, not reasoning. Find the `implementer-result` evidence records that real
runs actually attached — the archived spines under `.agent-work/` are full of them — and report the
literal payload fields. Then say plainly whether a Commander following today's shipped instructions
would satisfy this gate.

Your item `r4a-satisfiable` owns this. It is the one that decides `APPROVE` vs `BLOCK`.

## What already checked out, so you can spend your effort elsewhere

Verified by the Admiral directly: all three edited templates are valid JSON; `<admiral-skill-dir>`
is genuinely resolved by `init_work_area.resolve_spine` (`_ROLE_SKILL_DIR_RE` matches any
`<role>-skill-dir` token), so that placeholder is not a latent literal. Do not re-derive those.

## The rest of your survey

`r4b` — the Admiral `init` check now **runs a mutating script as its check**, and hardcodes a
relative `.agent-work/<work-id>/` path that `scripts/agent_work_root.py::durable_root` deliberately
relocates depending on whether an epic lease is held. Drive it, don't reason about it.

`r4c` — the census claims 22 instructions found, 19 already fine. Spot-check at least six of the 19
yourself, and sweep for statement/check mismatches independently rather than confirming their list
of five.

`r4d` — the Explorer statement was weakened rather than its check strengthened, on the argument that
`spine.json` must already exist for the engine to be running the gate at all. Test that argument.

Standard items `r1`–`r6` still apply: handoff compliance, scope drift, evidence quality,
reconciliation, and design quality.

## Hard no-gos the change was under

`checklist_engine.py`, `run_crew.py`, crew skill files, `settings.json` and `docs/agents/*` all
untouched; compact-format JSON edited surgically as raw text, never round-tripped through
`json.load`/`json.dump`; no push to `main`. Confirm each.

## Test mode

`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`

Unset those three or you inherit your own dispatch's binding into the suite. Use `python`, not
`python3`. The implementer reports `2532 passed, 1 skipped, 1102 subtests`. Note that a green suite
here proves little about the decisive question — **no test exercises whether a shipped template's
gates are satisfiable by a real run**, which is itself worth saying in your finding if you confirm
it.

## Drive your own spine through the door

Your dispatch binds `SPINE_FILE` and `SPINE_SESSION` for you. Use the `mcp__spine__*` tools, found
via `ToolSearch`; the door covers all 18 engine verbs. If you reach for the CLI, say so and say what
made it the natural move — that is useful evidence and not a mark against you.

## Verdict

`APPROVE` or `BLOCK`, with the evidence you personally ran. **An honest partial is acceptable and a
silent gap is not.** If you approve something you did not test, say so.

Write your verdict to
`.agent-work/epic-559/b-instructions-to-checks/REVIEWER_RESULT.md`, including its Workflow Feedback
section, before ending your turn — that write is the delivery.
