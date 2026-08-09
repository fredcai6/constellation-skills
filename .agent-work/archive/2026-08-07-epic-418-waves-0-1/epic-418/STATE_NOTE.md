# Crash-resume state note — epic-418

**WAVES 0 AND 1 ARE COMPLETE AND MERGED. The spec is revised, cold-panelled, fully triaged and
CONFIRMED. The epic is at a clean stop, ready for a wave-2 relaunch against the new spec.**

- **step:** `execute` — in progress, between waves. Remaining after `execute`: `closeout` only.
- **slug:** `epic-418` · main checkout `C:/Programs/constellation-skills` · **everything pushed**
  (`origin/main` current, working tree clean)
- **next command:** `python scripts/checklist_engine.py --file .agent-work/epic-418/spine.json current`
  — then plan wave 2 from the confirmed spec's execution order
- **pid:** none — no Commanders in flight
- **expected artifact:** a wave-2 launch, first link in the confirmed order

## The spec of record — read this before planning wave 2

`.agent-work/epic-418/spec-revision/REVISED_SPEC.md` — **CONFIRMED 2026-08-07**, supersedes
`.agent-work/archive/2026-08-03-explore-post-phase1/DESIGN_SPEC.md`. Both gate phases pass
(`--phase review` and `--phase confirm` exit 0). All 81 cold-panel findings dispositioned.

**Execution order: B extended → A2 → F → C → E.** Off-chain, runnable any time: A's remainder
(#452 multi-spine, ship the gauge writer) and D's #436 debt. The chain is a *dependency* order,
not a schedule — each link's reason is stated, and a Commander that finds a link is not real
should say so rather than honour it.

**Organising principle:** reveal the next step, not the whole plan — gate, wave, epic. Safe
because instructions are gate-local while constraints are spine-global.

## What landed

| Wave | Issues | State |
|---|---|---|
| 0 | #419 #420 #422 #425 | merged; #419/#420/#422/#425 all closed |
| 1 | #440 #447 | merged and closed; wave 1 complete |

Main green: **1723 passed, 2 skipped, 643 subtests, exit 0** (real exit code captured).

Closed today with evidence: #419 #420 #422 #425 #328 #329 #428 #437 #440 #443 #454 #462 #463 #466.
Filed today: #452 #457 #458 #460 #461 #464 #465 (+#447's own batch).

## Live defect that will bite the next Admiral — #457

**The spine rail attributes a DESCENDANT's gate to its ancestor.** Crew inherit their
dispatcher's session id with their own agent ids, so the rail resolves an Admiral onto a spine a
descendant is driving and orders it to work that gate. Ten firings this session. **Never run
one** — the lease is live every time, and two agents in one spine is forbidden.

The three-strike escape hatch cannot save you: `spine_rail.py:897` resets the counter on the
*watched spine's* progress, so a productive descendant resets its ancestor's strikes forever.
The better the descendant works, the more relentless the nudging.

## Settled — do NOT re-derive

- **`py` is not the test runner**, and **`FORCE_COLOR=3` produces false reds for `python` too**
  (#454, fixed). `_COMMON.md` now carries both warnings — it previously asserted the opposite.
  Run suites as `FORCE_COLOR= NO_COLOR=1 python -m pytest -q tests`.
- **#180 is CLOSED.** The gauge writer is wired only in untracked `.claude/settings.local.json`,
  so it ships nowhere — that is #458 (workstream R), not #180.
- **`docs/agents/engine-config.json` is a Charter deliverable, not a dangling pointer.**
  `TRIPWIRES.md` T1 fires when an agent creates it. Two independent agents filed it as a defect
  (#443, #462) — both closed. Do not file it a third time.
- **File overlap is not conflict.** The predicted four-file conflict set for #447 was wrong in
  composition: two predicted files merged cleanly, two unpredicted ones conflicted.
- **Commander departures from stale plan specifics are the MODE, not the exception** — five this
  epic, all ratified. A frozen artifact's specifics go stale; the agent applies the governing
  rule and says so.

_Updated: 2026-08-07T20:30:00Z_
