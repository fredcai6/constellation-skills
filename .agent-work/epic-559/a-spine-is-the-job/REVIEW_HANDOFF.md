# Cold reviewer handoff — A: the spine is the job, not a document beside it (#559)

**Work id:** `epic-559/a-spine-is-the-job` · **Gate:** `g2-review` · **Role:** reviewer · **Model:** Opus
**Worktree:** `/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job` (branch `epic-559/a-spine-is-the-job`)
**Under review:** commit `6fc83013` against `main`@`9d593e0a`, plus `IMPLEMENTER_RESULT.md`.
**Your spine:** `.agent-work/epic-559/a-spine-is-the-job/REVIEW_SURVEY.json` — drive it item by item.

You are **cold**. You did not plan this and you are not here to agree with it.

## What the change was supposed to do

A dispatched crew is told to read a handoff document; the change makes it read its bound spine
instead. Four parts: a spine-carried prompt branch in `build_crew_argv`; `--handoff` becomes
optional; the two crew `SKILL.md` files stop sending crews to the engine CLI; and a crew loses the
ability to waive its own check, per the human's ruling — *"agent cannot waive itself. I'll allow
commander to waive crew, admiral to waive commander, human for admiral. always ask up."*

## What already checked out, so you can spend your effort elsewhere

Verified by the Admiral directly: the branch is 6 files, +526/−71; the suite reports
`2548 passed, 1 skipped`; the `CREW_ALLOWED_TOOLS` grant did genuinely grow from 7 to the door's
real 9 and now has a test tying it to `mcp_spine_server.TOOL_NAMES`; the escape hatch the handoff
offered (import at module scope is awkward because `mcp_spine_server` reads `SPINE_FILE`/
`SPINE_ENGINE` at import) was used as designed rather than improvised around. Do not re-derive
those.

## Where the risk actually sits

The implementer solved job 4 with a mechanism this repo has never used before: `build_crew_argv`
now appends `--settings` carrying an **inline JSON blob with a `PreToolUse` hook** to **every** crew
dispatch, which denies `action=waive` on `mcp__spine__spine_evidence`. That is a good idea, and it
is the load-bearing part of the diff, and almost none of it is proven by the tests on the branch.

Three specific gaps, each an item on your spine:

**`r4a` — nobody has run a spine-only crew.** Every test on this branch asserts on the *argv string*
`build_crew_argv` returns. That proves the prompt was constructed, not that a crew can work from it.
The entire point of the change is that a crew reads its spine instead of a document, and that claim
is untested end to end. **Run one.** Scratch spine, two trivial gates, real dispatch with `--spine`
and no `--handoff`. If the crew flounders because the prompt names no task, the code being clean is
irrelevant.

**`r4b` — the merge claim is an assumption.** The docstring states the inline `--settings` "merges
with" the repo's `.claude/settings.json` and the worktree's project settings. If it *replaces* them,
every crew silently loses the permission allows in `.claude/settings.local.json`, and unrelated
hooks stop firing. Measure it against the installed binary; do not read the docstring.

**`r4c` — the hook was tested standalone, not in a dispatch.** Piping fake JSON at the hook script
proves the script's logic. It does not prove Claude Code invokes it, matches it to the right tool,
or honours a `deny`. And test both directions: a hook that denied *everything* would pass a
waive-only test while breaking every crew, since `attest` and `attach` live behind the same tool.

## Three more, smaller

**`r4d`** — `crew_settings_json` emits the literal command `python3 -c '...'`. Hardcoded interpreters
are an open, already-painful problem here (#539, #553); the repo probes `("py","python3","python")`
and writes an `interpreter.json` sidecar. The human has ruled such a hardcode is acceptable
short-term **only if it is recorded against #539**. Judge whether it blocks and name the smallest
correct fix.

**`r4e`** — the change removed `implementer`/`reviewer` from `TIER2_SKILL_FILES` and replaced a test
class in `tests/test_mcp_adoption.py`. Deleting a pin so a change passes is the exact escape-hatch
shape this epic is hunting. The deletion may well be right — the pinned fact was deliberately
overturned — but confirm no unrelated assertion rode along, and prove the replacement is two-sided
by putting the old CLI text back in a scratch copy and watching it go red.

**`r4f`** — attack the inline hook's shell quoting rather than reading it.

Standard items `r1`–`r6` still apply: handoff compliance, scope drift, evidence quality,
reconciliation, design quality.

## Hard no-gos the change was under

`checklist_engine.py` and `mcp_spine_server.py` unmodified; `settings.json` and `docs/agents/*`
untouched; handoff templates not deleted; spine templates not changed (another crew owns those);
no push to `main`. Confirm each. Note that `tests/test_mcp_adoption.py` **was** modified and the
implementer explains why in its Scope section — judge that explanation, don't just accept it.

## Test mode

`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`

Unset those three or you inherit your own dispatch's binding into the suite. Use `python`, not
`python3`.

## Drive your own spine through the door

Your dispatch binds `SPINE_FILE` and `SPINE_SESSION` for you. Use the `mcp__spine__*` tools, found
via `ToolSearch`. Note the irony available to you here: you are the first reviewer running under the
grant this change modifies. If your own `spine_evidence` calls behave oddly, that is evidence.
If you reach for the CLI, say so and say what made it the natural move.

## Verdict

`APPROVE` or `BLOCK`, with the evidence you personally ran. **An honest partial is acceptable and a
silent gap is not.** If you approve something you did not test, say so.

Write your verdict to `.agent-work/epic-559/a-spine-is-the-job/REVIEWER_RESULT.md`, including its
Workflow Feedback section, before ending your turn — that write is the delivery.
