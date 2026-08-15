# Launch Order: `launcher-hygiene` — three false signals that each cost a dispatch today

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

## Mission

Three defects, all observed live during today's wave, all filed with evidence. They are independent —
**ship what you can, report what you cannot.** Partial delivery is acceptable; silent scope creep is not.

Source documents in the **primary checkout** (your worktree does not contain them):

- `/home/tommy/projects/constellation-skills/.agent-work/triage-candidates/auto-backgrounding-breaks-the-foreground-crew-dispatch-contract.md`
- `/home/tommy/projects/constellation-skills/.agent-work/archive/2026-08-15-crew-verdict-and-door/triage-recommendations/full-suite-false-fails-inside-a-spine-bound-shell.md`

Read both before planning.

---

## Task 1 — the suite false-fails inside a spine-bound shell

**Highest value per line of change.** Cost two lanes a diagnostic cycle today; one of them blocked a gate
over it and needed a human ruling to proceed.

`tests/test_mcp_identity.py:600`,
`DC3InheritanceMechanismTests::test_launching_the_parent_never_touches_the_calling_processs_own_environ`
asserts `SPINE_FILE` / `SPINE_SESSION` / `SPINE_PARENT` are absent from `os.environ`. But **any** crew
dispatched via `run_crew.py --backend cli --spine ...` has those three bound into its real environment
before Claude Code starts. So the doctrine-recommended workflow — verify your door, then work — *causes*
a false failure.

Reproduced today, both directions: it fails as-is inside a bound crew, and
`env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q` reproduces the clean baseline
exactly.

**The test's intent is right and must survive**: it verifies that `run_crew.py`'s launch does not mutate
the *launcher's own* `os.environ`. That property should be asserted **in isolation from whatever the test
runner's ambient environment happens to carry.** Save and restore the three keys around the test itself.

**Evidence:** a red proving the test fails when those vars are pre-set, and green after — driven by
setting them in the test process, not by narrating it.

---

## Task 2 — `archive` relocates the spine, so spine-only dispatches still invert

PR #587 (merged, `6947b15e`) fixed the case where `--result` was relocated by `archive` and a terminal
spine rescues the verdict. **The same inversion still exists for `--spine`.**

`archive` relocates the **entire work area**, including `spine.json` itself, into
`.agent-work/archive/<date>-<work-id>/`. `spine_terminal` treats a missing spine as never-terminal, so a
spine-only dispatch that successfully archives is recorded `failed`.

Measured today, using #587's own new field:

```json
{ "crew_id": "constellation/tc1-episode-rewording/execute/commander/attempt-2",
  "status": "failed", "exit_code": 0,
  "verdict_source": "spine_terminal", "door_bound": true }
```

`verdict_source` correctly named which check decided — and that check was reading a path `archive` had
just emptied. Every spine-only dispatch reaching `archive` is affected.

This is the unanswered half of `crew-verdict-and-door`'s own open question: *"Do other gates relocate
artifacts the launcher watches, or is `archive` the only one?"* The answer is that `archive` relocates
**both** watched artifacts.

**Follow #587's own precedent**, which is in the file you are editing: when the watched artifact is gone
but the work is genuinely done, resolve it honestly and record which check decided. Consider resolving
the spine through the archive relocation before concluding "not terminal."

**Do not** make the verdict a rubber stamp: a genuinely incomplete run must still read `failed`. #587's
fix has a matching guard — read how it did it and be consistent.

---

## Task 3 — Commanders park on a resumption that never comes

**Five occurrences today**, across three lanes. Each cost a full dispatch and each looked like partial
progress rather than failure — correct work left in a working tree, spine mid-gate, nothing committed.

The mechanism, in a Commander's own words:

> Dispatched the g1 implementer crew … as a **foreground/blocking** `run_crew.py` call; it's running long
> enough that **the harness moved it to background** … and will notify me when it completes.

`skills/commander/references/crew-dispatch.md:7` promises the wrapper "launches foreground/blocking."
The **agent harness auto-backgrounds** any bash command that runs long — and the full suite takes ~2
minutes, so it fires on the one step every gated lane must run. The parent's process then exits at
turn end, so the awaited notification can never be acted on.

**Critical finding: warning the Commander does not work.** One dispatch carried a section headed "Do not
park" that stated the lifetime fact, named the ~2 minute suite as the trigger, said to poll the output
file, and noted four lanes had already been lost. It parked anyway. The agent is not disobeying — at the
moment it ends its turn, waiting looks correct, and **it has no blocking primitive to reach for.**

### 3a — ship the idiom (required)

Document in `crew-dispatch.md`: the Commander's process ends with its turn; a harness-backgrounded
command is therefore not awaitable; "wait for the notification" is never a valid way to end a turn. Then
give the working alternative **by name** — this shape is one foreground command that does not return
until the result exists, and it is the only thing that has actually stopped the parking:

```bash
nohup <long command> > /tmp/out.log 2>&1 &
until grep -qE '<completion pattern>' /tmp/out.log; do sleep 15; done
tail -5 /tmp/out.log
```

Show it concretely for the full-suite check, since that is the trigger. Also state the fallback when a
step genuinely cannot finish in-turn: `spine_halt block` with the crew id recorded, so a parent resumes
deliberately — the E1 fail-up path that already works.

### 3b — the mechanical check (gated, and you may decline it)

A Stop-hook condition could refuse the quiet exit outright: turn ending while the bound spine has an
`in-progress` gate and a `running` crew whose pid is not live.

**Attempt this ONLY if you can produce both halves of a falsifiable proof:**

- a **red** showing it fires on the parked shape, and
- a **control** showing it does **not** fire on a legitimate turn end.

Without both, **do not ship it** — report a design instead. A Stop hook that misfires wedges every agent
in the repo, which is far worse than the defect. `scripts/hooks/spine_rail.py` already has a `Stop`
handler; read it and its fail-open posture before touching anything. Declining 3b with reasons is a fully
acceptable outcome for this lane.

---

## Pre-Rulings — settled

1. **`decision:independent-tasks` — settled.** Ship what you can; report what you cannot. Do not let 3b
   hold 1, 2 and 3a.
2. **`decision:no-rubber-stamp` — settled.** Task 2 must not let an incomplete run read as complete.
3. **`decision:intent-survives` — settled.** Task 1 preserves what the test verifies; it changes only the
   isolation of the measurement.
4. **`decision:fail-open-hooks` — settled.** Hook execution stays fail-open and bounded. A hook that
   errors must never wedge a turn.
5. **`decision:clear-caches-before-measuring` — settled.**

## File Ownership

**Yours:** `tests/test_mcp_identity.py`, `scripts/run_crew.py` and its tests,
`skills/commander/references/crew-dispatch.md`, and — only under 3b's proof requirement —
`scripts/hooks/spine_rail.py`'s Stop handler plus its tests. Your work area.

**NOT yours:** `scripts/checklist_engine.py` — the `archive` gate relocating the work area is **correct**;
relocating is what archiving *is*. Do not change the gate to suit the launcher. Also not yours:
`.mcp.json`, `docs/CHECKLIST_SCHEMA.md` and `skills/admiral/templates/LAUNCH_ORDER.template.md` (a sibling
lane `tc6-doctrine` is live in those right now), and `.worktrees/tc6-doctrine/`.

## Do not park — this applies to you

Use the 3a idiom yourself for the suite run. **Do not dispatch a crew.** Everything here is yours, in this
turn. If something must run long, poll it; do not end your turn with anything pending.

## Your own closeout episodes

They face the episode-observation guard, which reds the suite. Write them as **observations of what this
run did** — past tense, describing the run, not addressing a reader. In the `workaround` and
`proposed-remedy` kinds, **do not open a clause with a bare verb** — that flagged `Read`, `keep` and
`pass` in another lane today and cost a dispatch. **Do not add anything to the exception list.**

## Evidence required

- **Red before, green after, per task**, over behavior. Task 1's red must come from actually setting the
  three vars. Task 2's red must drive the real judging path with a relocated spine — this bug lives in how
  two real behaviors compose, and a mocked test would not have caught it.
- A test that a genuinely failed crew still reads `failed` after Task 2.
- Full Linux suite, cache-clean, clean env:
  `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
  then `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT python -m pytest -q`.
  **Baseline on `main` at `0646d61b`: 3027 passed, 7 skipped, 0 failed, 1136 subtests** measured from the
  primary checkout. **From inside your worktree expect 3028 / 6** — `tests/test_spine_lifecycle.py:161`
  skips unless the checkout sits directly inside `.worktrees`. Both are correct; the difference is
  location, not a regression.
- Regenerate the map: `python -m scripts.code_map build --root .` and commit if it moves.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/launcher-hygiene`, branch
`fix/launcher-hygiene`, based on `main` at `0646d61b`. Yours alone.
Work area `.agent-work/launcher-hygiene/` inside it.

`spine_status` must describe `launcher-hygiene` — if it resolves to anything else, especially an `f-424`
demo spine, **stop and report.**

## Budget

Three tasks plus one optional. If any single task grows a second subsystem, stop and report.

## Stop Conditions

- `spine_status` does not resolve to `launcher-hygiene`.
- Task 2 cannot be fixed without letting an incomplete run read as complete.
- Task 1 cannot be fixed without changing what the test verifies.
- 3b cannot produce both a red and a control.
- Green would require touching anything in the not-yours list.

## Return Shape

What `spine_status` resolved to, named explicitly; per task, what you changed and its red/green proof;
whether 3b shipped or was declined **and why**; clean-env cache-clean suite counts before and after;
whether the map moved; and anything floated.

**You may push and open a PR** — your `archive` gate requires it. **You are fenced from merging.** The
Admiral merges; a lane cannot supply its own independent approval. Say plainly that the PR is open and
unmerged.
