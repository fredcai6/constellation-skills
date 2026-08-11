# Cold reviewer handoff — C1 round 2: the lint stopped refusing good spines

**Work id:** `epic-559/c1-spine-lint` · **Gate:** `g6-review2` · **Role:** reviewer · **Model:** Sonnet
**Worktree:** `/home/tommy/projects/constellation-skills-wt/c1-spine-lint`
**Under review:** `8708493b` and `96fb9412`, and the whole branch against `main`@`3c0fc7d2` as an integration.
**Your spine:** `.agent-work/epic-559/c1-spine-lint/REVIEW_SURVEY2.json`. Write your Fowler record to `.agent-work/epic-559/c1-spine-lint/FOWLER_PASS2.json`.

You are **cold**. A different reviewer blocked round 1.

## What this is

`scripts/validate_spine.py` refuses a spine that the engine cannot read, or that carries a check
which cannot fail. Four faults: a gate where every postcondition is `check: null`; a pytest selector
that collects zero tests; an artifact check with no `match` whose statement asserts a property; an
unresolved `<placeholder>` in a command. Every one has really shipped in this repo.

## Round 1's verdict, so you do not redo it

A reviewer swept 552 files and hand-inspected every distinct trigger. **Faults 1, 3 and 4: zero false
positives** — all three distinct fault-3 statement texts across 128 hits hand-verified as genuine
#562-shaped defects, every distinct fault-4 placeholder confirmed unresolved.

**Fault 2 was 8 false positives in 9 findings.** `_pytest_segments` split on bare `|`, so in the
corpus's own recommended idiom the `2>/dev/null` token was folded in as a nonexistent pytest target,
and the resulting empty collect was reported as zero-collect. It refused checks running 32 passing
tests. Second mechanism: `_collects_zero` used `sys.executable` without confirming pytest was
importable, so `python3 -m scripts.validate_spine` reported 6 spurious faults where `python` reported
0.

## What the rework claims

Fault 2 at **1 hit, 0 false positives**, down from 9 hits and 88.9%. The surviving hit is claimed as
a genuine defect in an archived epic-298 spine.

## Your five items

`w1` — **get your own numbers.** Re-run the sweep and hand-inspect every remaining hit across all
four fault classes, not just fault 2. The fix touched shared tokenization, so confirm nothing
regressed into the three that were clean. A new false positive anywhere is a `BLOCK`.

`w2` — **the direction the fix moves is toward blindness.** It makes the lint stop flagging things,
and that is where a false *negative* hides. Build real zero-collect defects in several shapes — with
a redirect, without, behind a pipe, with an interpreter that does have pytest — and confirm each is
still caught. Say which shapes the lint now declines to judge.

`w3` — the rework's rule was *an undecidable check is not a failing check*. Check what actually
happens when pytest is unavailable: does the lint stay silent, or say it could not tell? Silence and
a clean pass look identical to a caller, and refusing things that look fine is this tool's entire
purpose.

`w4` — verify the surviving true positive: the commit that renamed the test away, and that the
selector really collects nothing today.

`w5` — **judge the Admiral's own check scripts.** Two checks on the crew's spine are scripts the
Admiral wrote and put out of the crew's reach — it may block against them but not edit them. The
crew did block against one and was right: it had been scoped to all of `.agent-work/`, wrongly
assuming archived spines from earlier epics had runnable selectors. The Admiral rescoped it to
`epic-559` and `epic-418-followon`, 14 files. Read both scripts. Are they a fair statement of
"fixed"? Is 14 files now too narrow to mean anything? **Say so if it is** — a check the parent
authored is still a check that can be wrong, and this one already was.

Standard items `r1`–`r6` apply.

## Hard no-gos

`checklist_engine.py`, `mcp_spine_server.py`, `run_crew.py`, `settings.json`, `docs/agents/*`, every
spine template, and the two Admiral check scripts. No push to `main`.

## Test mode

`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_ENGINE FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`
Use `python`, not `python3` — `python3` on this host has no pytest, which is itself one of the bugs
under review.

## Drive your own spine through the door

`SPINE_FILE`/`SPINE_SESSION` are bound; `mcp__spine__*` via `ToolSearch`. Say so if you use the CLI.
**Do not dispatch anything and then end your turn waiting for it** — that killed a crew on a sibling
branch tonight.

## Verdict

`APPROVE` or `BLOCK`, with evidence you personally ran. Write to
`.agent-work/epic-559/c1-spine-lint/REVIEWER_RESULT2.md` including Workflow Feedback.
