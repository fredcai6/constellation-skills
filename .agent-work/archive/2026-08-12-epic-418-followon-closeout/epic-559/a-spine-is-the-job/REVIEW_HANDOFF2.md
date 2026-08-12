# Cold reviewer handoff — A, round 2: the rework after a BLOCK

**Work id:** `epic-559/a-spine-is-the-job` · **Gate:** `g3-review2` · **Role:** reviewer · **Model:** Opus
**Worktree:** `/home/tommy/projects/constellation-skills-wt/a-spine-is-the-job` (branch `epic-559/a-spine-is-the-job`)
**Under review:** the three rework commits `554c553a`, `2152ded3`, `99336f96` — and the whole branch against `main`@`9d593e0a` as an integration.
**Your spine:** `.agent-work/epic-559/a-spine-is-the-job/REVIEW_SURVEY2.json` — drive it item by item. Its `r6-fowler` check path is pre-resolved; write your Fowler record to `.agent-work/epic-559/a-spine-is-the-job/FOWLER_PASS2.json`.

You are **cold**. A different reviewer blocked the first pass. You are not here to confirm that the
fixes look like the right fixes.

## Round 1, in one paragraph

A crew dispatched with `--spine` and no `--handoff` can drive its spine — a real probe crew did it.
But the launcher still judged completion on a `--result` artifact the spine-only prompt never asks
for, so a crew that fully succeeded was recorded `failed`; the test covering it made its own
precondition true by writing that artifact from the harness. And the hook that denies a crew's
`waive` hardcoded `python3` while `PreToolUse` hooks fail **open**, so on the wrong host the one
mechanism whose job is to refuse silently permits.

## What the rework claims

`--result` is now optional wherever `--spine` is given, and completion is judged by `spine_terminal`
(`checklist_engine.active_id(...) is None`). The hook emits `shlex.quote(sys.executable)` with
`"shell": "bash"`, and the bare `assert` became `assert_shell_safe_command()`. New tests, plus a
negative control.

## The question that decides the verdict

**Does a crew that correctly BLOCKS now get recorded as a clean success?**

The human's ruling is that a crew which hits a check it cannot satisfy must block and ask up. If
`active_id()` returns `None` for a spine whose gate is blocked or halted — rather than only for one
whose gates all completed — then a crew that correctly gave up is reported to the dispatching
Commander as done. That is worse than the bug this rework fixed, because the first bug was a false
negative and this would be a false positive.

Drive real spines into blocked, halted, and skipped-with-refusals states and report what
`spine_terminal` says about each. Item `v1` owns this and it decides `APPROVE` vs `BLOCK`.

## Then run one, again

`v2`: the previous reviewer found the round-1 bug by dispatching a real crew rather than reading the
code, and said so in its feedback — *"everything I found that matters came from executing rather
than reading."* Do the same. Real spine-only dispatch against the fixed code, confirm `completed`;
then the negative, a crew that leaves a gate open must still record `failed`.

## Three more

`v3` — `run_crew.py` now imports `checklist_engine` at module scope. The last module-scope import
question in this wave was load-bearing: importing the door requires a bound spine because it reads
`SPINE_FILE` at import time. Check what the engine does at import, and whether `run_crew` still
imports in every context that used to work.

`v4` — the two known fail-open paths are fixed. The property is not: a `PreToolUse` hook that errors
still lets the call through. Name the residual modes, say whether any is reachable, and say whether
the code acknowledges it anywhere a future author would see. An accepted risk stated is fine.

`v5` — the argv changed for **every** dispatch, not just spine-only ones. Prove nothing existing
moved.

Standard items `r1`–`r6` still apply.

## What round 1 already settled — do not redo it

`--settings` merges rather than replaces (4 probes against the installed binary). The waive denial
fires in a real dispatch and `attest`/`attach` still work behind the same tool. The deleted pins in
`tests/test_mcp_adoption.py` are the right deletion, proven two-sided by mutation. A spine-only crew
can drive its spine from the prompt alone — it did so while reading the *stale installed skill* that
tells crews to use the CLI, which is a stronger result than the branch claims for itself. Those are
banked. Spend your budget on the five items above.

## Known and deliberately not yours

`tests/test_mcp_adoption.py`'s `DOOR_TOOL_NAMES` (7) and `CLI_ONLY_VERBS` (5) are stale after N1 —
a pin asserting a false fact. Flagged twice, left twice, correctly. Leave it a third time.

The installed skills under `~/.claude/skills/` are Aug 9 copies carrying the pre-#559 CLI paragraph,
so **you are reading old doctrine while reviewing the change that replaces it.** The Admiral
reinstalls at merge. Mentioned so you do not report it as a defect in this diff.

## Hard no-gos the change was under

`checklist_engine.py`, `mcp_spine_server.py`, `settings.json`, `docs/agents/*`, and all spine
templates under `skills/*/templates/` untouched; no push to `main`. Confirm each.

## Test mode

`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`

Use `python`, not `python3`.

## Drive your own spine through the door

Your dispatch binds `SPINE_FILE` and `SPINE_SESSION`. Use `mcp__spine__*`, found via `ToolSearch`.
The door covers all 18 verbs on this branch and the crew tool grant now includes all nine tools.
**Do not reach for the engine CLI without saying so and saying why** — the last crew was told two
tools were denied and responded by using the CLI for everything, which is exactly the behaviour this
wave is trying to remove. If you use it, that is data, not a mark against you.

## Verdict

`APPROVE` or `BLOCK`, with the evidence you personally ran. An honest partial is acceptable; a
silent gap is not. Write to `.agent-work/epic-559/a-spine-is-the-job/REVIEWER_RESULT2.md`, including
Workflow Feedback, before ending your turn — that write is the delivery.
