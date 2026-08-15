# Launch Order: `epic-568-441` — resume the transactional binding store on Claude

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

**This is a RESUME, not a new mission.** Your `understand` and `plan` gates are complete and their
output is frozen. You are not re-planning.

## The ruling that unblocks you — read this first

Your spine is blocked with `next_action: "After 2026-08-20 06:19, resume the existing implementer spine
m1 first…"`. **That date does not apply to this dispatch.**

The blocker's own words name the cause:

> Required RED/GREEN execution and even the mandated `apply_patch` result write were rejected by the
> approval layer because the **account-wide Codex usage limit** is exhausted until 2026-08-20 06:19.

That is a **vendor quota on Codex**, not a property of the work, not a safety hold, and not a statement
about the plan's readiness. **You are running on Claude.** The quota does not apply to you.

**Ruled:** proceed now. Do not wait for 2026-08-20. Do not treat the date as a precondition.
The rest of that `next_action` — the resume *order* — **is** binding and is reproduced below.

## Mission

Complete the frozen plan: a single transactional binding store, so concurrent hook writers preserve every
valid binding, reject unsafe identities consistently, and remove only entries whose death is positively
established.

Your `PLAN_CONVERGENCE.md` already settled the shape and you must not revisit it:

> The transaction owns lock acquisition, locked reload, safe reap, one mutation callback, unique-temp
> replace, and release. Claim, release, and SessionStart remain thin callers. Gauge delegates identity
> validation to the rail and never becomes a store owner.

Its **untaken roads are closed**: per-writer locks, lock-only-around-replacement, stale-lockfile/PID
ownership, global or historical sweep, and more than one execute gate. Do not reopen them.

## Resume order — binding

Three nested spines, each with a **stale but `active`** lease (last heartbeat ~2026-08-14T18:19Z).
Resume innermost first:

| # | spine file | blocked gate | session id |
|---|---|---|---|
| 1 | `g1-implementer-plan.json` | `m1-transaction` | `constellation/epic-568-441/g1/implementer/attempt-1` |
| 2 | `execute.json` | `g1-implement` | `constellation/epic-568-441-execute` |
| 3 | `spine.json` | `execute` | `constellation/epic-568-441` |

**Take each lease over. Do not release and do not recreate.** Claim with `--force` plus a `--reason`,
stamping `previous_session_id` and `takeover_reason`. Takeover preserves the chain of custody;
recreation destroys it, and your own blocker explicitly says "without releasing or recreating any lease."

Only `spine.json` is bound into your MCP door. Drive the two child spines through the **engine CLI** with
an explicit `--spine` and `--session-id` — that is the disclosed, documented path and the epic-568
Admiral used it throughout.

## Before you execute: your branch is 4 commits behind main

Branch `epic-568/441-binding-store` sits at `065445de`; `main` is at `453f8492`. Missing: the engine-native
worktree origin stamp (#577), the code map refresh (#578), the worktree relocation to `.worktrees/`
(#585), and the work-area escape fix (#586).

**Bring `main` into your branch before executing**, then re-measure. Working against 4-commit-stale code
would make your suite counts meaningless and could hide a real interaction.

Expect this to be quiet — `git diff main` currently shows differences in `scripts/run_crew.py`,
`scripts/spine_lifecycle.py` and several test files that are **main moving ahead of you**, not your
changes. If integrating main produces a conflict in any file you own, that is a finding: report it.

## The uncommitted work already in your tree — verified, not assumed

`tests/test_spine_rail.py` carries **55 uncommitted added lines**. I confirmed this against
`git diff --stat` in your worktree before issuing this order; it is the spawned regression your
implementer patched but never executed:

> The spawned regression is patched in `tests/test_spine_rail.py` but **remains unexecuted**; no
> production implementation or runtime claim is made.

**Run it first, before writing any production code.** It should be **RED**. That red is your `m1` proof
obligation and the thing the Codex quota prevented from ever being observed.

If it is **green**, stop and report — either the regression does not bite, or something landed that the
record does not know about. Do not proceed on the assumption that it is correct.

## Pre-Rulings — settled, do not relitigate

1. **`decision:codex-quota-is-not-a-hold` — settled/human.** Proceed now; see above.
2. **`decision:takeover-not-recreate` — settled.** Force-claim with a reason; preserve provenance.
3. **`decision:plan-is-frozen` — settled.** `understand` and `plan` are complete. Implement the
   convergence, do not re-derive it.
4. **`decision:no-backfill` — settled.** Safe reap happens only inside a new writer transaction. No
   global or historical sweep.
5. **`decision:fail-open` — settled.** Hook execution stays fail-open and bounded on lock or filesystem
   failure. Stdlib-only, portable advisory locking with crash release. **No stale-lockfile lifecycle.**
6. **`decision:clear-caches-before-measuring` — settled.** A stale `.pyc` fabricated a convincing phantom
   failure last epic and cost four falsifications to attribute.

## File Ownership

**Yours — the frozen four-file scope, plus its config:**
`scripts/hooks/spine_rail.py`, `scripts/hooks/gauge_writer_hook.py`, `tests/test_spine_rail.py`,
`tests/test_gauge_writer.py`, `docs/agents/engine-config.json`, and your work area.

**NOT yours — two other lanes are live in sibling worktrees right now:**
- `scripts/checklist_engine.py` — lane `tc1-worktree-identity` is changing its worktree guard.
- `scripts/run_crew.py` — lane `crew-verdict-and-door` is changing its completion judging.
- `.mcp.json` — shared config; editing it would alter every live lane's door mid-run.
- **`.agent-work/commander-315/`** — a separate spine in *your own work area* whose `plan` gate is blocked
  on an Admiral ruling. That ruling was issued today and is being implemented by another lane. **It is not
  yours. Do not resume it, advance it, or clear its blocker.**

A note you may find useful rather than constraining: `scripts/hooks/spine_rail.py` contains a lexical
worktree derivation (`_worktree_from_spine`) that disagrees with a git-based one elsewhere. **Today's
ruling deliberately keeps it lexical** — an absolute claim path survives archival, and the hook runs on
every tool call where a subprocess would be a real cost. **Do not "fix" it while you are in there.**

## The MCP door — verify before you mutate anything

This dispatch launches through the `cli` backend with `--spine`, binding `SPINE_FILE` and
`SPINE_SESSION` into your process before your MCP servers start.

**`spine_status` must describe `epic-568-441`. If it resolves to any other spine — especially a `f-424`
demo spine — stop and report. Do not proceed and do not fall back.** A claim through a demo-bound door
mutates the wrong spine while looking like success; this bit a Commander last epic.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/epic-568-441`,
branch `epic-568/441-binding-store`. Yours alone.
Work area `.agent-work/epic-568-441/` inside it. Retained across the epic closeout **specifically** so
this work could resume in place.

## Evidence required

- The spawned regression in `tests/test_spine_rail.py` observed **RED first**, then green — the proof
  obligation the quota blocked.
- A concurrency proof using **spawned production handlers**, not mocks: two writers claiming different
  checklists at the same instant, with the final JSON retaining **both** records. Your plan calls for
  deterministic unlocked post-load synchronization, valid-final-JSON and all-entries assertions, plus
  distinct-temp and contention controls.
- The identity-rejection matrix: a punctuation-bearing and a 65-character agent id rejected by **both**
  consumers, **without writing**.
- The retention policy matrix: a readable active checklist stays bound regardless of age; a released one
  is removed; a missing target is removed **only** after the grace.
- Full Linux suite, cache-clean, **after** integrating main. Clear first:
  `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
  **Baseline on `main` at `453f8492` is 3002 passed, 7 skipped, 0 failed, 1130 subtests passed** —
  measured cache-clean immediately before this dispatch. Your post-integration baseline should match it
  before your production change lands.
- Regenerate the map: `python -m scripts.code_map build --root .` and commit if it moves.

## Budget

One execute gate, as your plan froze it. It explicitly rejected splitting into more than one because
"production changes overlap the same store seam and splitting them would create a knowingly inconsistent
intermediate boundary." Hold that line.

## Stop Conditions

- `spine_status` does not resolve to `epic-568-441`.
- The spawned regression is **green** before you write production code.
- A lease cannot be taken over without releasing or recreating it.
- Green would require touching anything in the not-yours list.
- Integrating `main` conflicts inside a file you own.
- The frozen plan turns out to be unimplementable as converged — in which case **stop and report**;
  do not silently re-plan.

## Return Shape

Report: what `spine_status` resolved to, **named explicitly**; the three lease takeovers with their
`previous_session_id` values; the regression's **red-then-green** transcript; the concurrency proof and
how you made it deterministic; the identity and retention matrices; cache-clean suite counts before and
after; whether integrating main was quiet; whether the map moved; and anything floated.

**You may push your branch and open a PR** — your `archive` gate's postconditions require it.
**You are fenced from merging.** The Admiral merges, because the merge gate requires an independent
approval and a lane cannot approve itself. Say plainly in your report that the PR is open and unmerged.

## A harness defect, so it does not surprise you

`run_crew.py` judges completion by the `--result` artifact, but `archive` **moves the whole work area** —
your result document included. The launcher will therefore likely report your run as `failed` even when
everything is correct. **That verdict is the harness being wrong, not you.** Do not react to it, do not
retry, and do not move the result back to satisfy it. A sibling lane is fixing exactly this. The Admiral
judges you on spine state.
