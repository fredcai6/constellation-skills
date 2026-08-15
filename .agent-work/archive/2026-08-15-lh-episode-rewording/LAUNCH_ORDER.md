# Launch Order: `lh-episode-rewording` — three statements, and one that may not be yours to fix

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

Small and precisely scoped. PR #591's code is finished, correct, and verified. This is the only thing
blocking it.

## First, so you write with the right instinct

The episodes you are editing are **unusually good**, and one of them produced the most valuable finding
of the day. `launcher-hygiene-002` recorded the Stop hook refusing a turn-end; following that thread into
`scripts/hooks/spine_rail.py` established that the mid-flight refusal **already exists and works**, and
that six earlier lanes escaped it only because a binding is recorded on Bash-matched
`checklist_engine.py` commands and never on MCP-door claims. That converted an open design question into
a small, specific fix.

**So: preserve the substance completely.** You are changing voice, not content. If a reader would learn
less after your edit, the edit is wrong.

## The mission

The episode-observation guard reds the suite. Three offenders:

```
OFFENDER launcher-hygiene-001 a5 (workaround)        imperative: 'read'
OFFENDER launcher-hygiene-002 a3 (observed-behavior) second-person: 'you'
OFFENDER launcher-hygiene-003 a5 (workaround)        imperative: 'Read'
```

Verified: `tests/test_episode_observations.py::RealStoreTests` reports `2 failed` on this branch, and the
rest of the suite is green (`3029 passed, 6 skipped` otherwise).

### 001 a5 and 003 a5 — reword these

Both open a clause with a bare verb. The guard scopes the imperative rule to the `workaround` and
`proposed-remedy` kinds, and both of these are `workaround`.

- **`launcher-hygiene-001` a5** — *"Called TaskOutput with block=true …, **read** its completed output
  (exit 0, gate closed) inside the same turn, and continued driving the spine …"*
- **`launcher-hygiene-003` a5** — *"**Read** skills/replan/scripts/verify_replan.py's
  verify_replan_input and the installed … directly before authoring REPLAN_INPUT.json, then filled every
  field …"*

Rewrite as past-tense records of what this run did. Both are already **nearly** in that voice — the
problem is a single clause-opening verb, not the framing. A minimal recast should do it. **Do not
shorten them.** 003's detail about the verifier resolving from the installed skills root rather than the
repo's `skills/` tree is a real finding and must survive intact.

### 002 a3 — investigate before you touch it

This one flags second-person `'you'`, and the `'you'` is inside a **verbatim quotation of the Stop hook's
own message**:

> The Stop hook refused the turn-end outright: 'SPINE MID-FLIGHT: gate reconcile is still open -- **you**
> are in the MIDDLE of the spine, not at its end, …'

The guard already has a documented carve-out for exactly this shape —
`tests/test_episode_observations.py:340`,
`test_a_quoted_instruction_the_record_observed_is_not_flagged`, whose docstring describes recording a
candidate instruction verbatim as a cold sensor's own observation. So one of two things is true, and
**your job is to determine which and say so**:

- **(a)** The carve-out exists but this quotation is not in the form it recognizes. Then adjust the
  quoting so the guard sees it, keeping the hook's words **verbatim** — the exact refusal text is the
  evidence, and paraphrasing it destroys the record's value.
- **(b)** The carve-out genuinely does not cover this case. Then it is a **guard gap**, not your defect.
  Record it as a finding, and reword only as much as it takes to get green — but say plainly in your
  report that you altered a verbatim quotation and why.

**Read the carve-out test before deciding.** Prefer (a) — a second-person pronoun inside quoted machine
output is precisely the false positive that test exists to prevent.

## The escape hatch you must NOT take

There is an exception list with 11 grandfathered entries. **Do not add to it.** It is not a way to make
new writing pass. Do not delete a record either — these are real run history.

`scripts/apply_episode_delta.py` is the store's only write path. Check `--help` first; hand-edit the
markdown only if you establish the delta tool cannot express a restatement, and say so if you find that.

## Do not park — run this as your first action

Your process exits when your turn ends; nothing will wake you. The suite auto-backgrounds at ~120s. Use
the blocking shape and stay in your turn:

```bash
cd /home/tommy/projects/constellation-skills/.worktrees/launcher-hygiene
rm -f /tmp/lher-suite.log
find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +
nohup env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT \
  python -m pytest -q > /tmp/lher-suite.log 2>&1 &
until grep -qE '[0-9]+ (passed|failed)' /tmp/lher-suite.log; do sleep 15; done
tail -20 /tmp/lher-suite.log
```

If you find yourself about to write "I'll resume when…", that sentence terminates your run — poll
instead. Note also that `checklist_engine.py advance` **re-runs the suite itself** during postcondition
verification and can be backgrounded the same way; your predecessor hit exactly that and handled it with
`TaskOutput(block=true)`. **Do not dispatch a crew.**

## Your own closeout episodes

Same guard. Past tense, describing the run, not addressing a reader; no clause-opening bare verb in
`workaround` / `proposed-remedy`; no additions to the exception list. Three lanes have now tripped this —
you have the advantage of knowing exactly what it catches.

## File Ownership

**Yours:** `episodes/active/launcher-hygiene-00{1,2,3}.md`, your work area.

**NOT yours:** `tests/test_episode_observations.py` and its exception list (the guard is correct),
`scripts/run_crew.py`, `tests/test_spine_lifecycle.py`, `tests/test_mcp_identity.py`,
`skills/commander/references/crew-dispatch.md` — all of #591's finished content — plus
`scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py` and `.mcp.json`.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/launcher-hygiene`, **branch
`fix/launcher-hygiene` — the existing PR #591 branch.** Commit there and push; no second PR. Work area
`.agent-work/lh-episode-rewording/`. Two archived work areas sit alongside; leave them.

`spine_status` must describe `lh-episode-rewording` — if not, stop and report.

## Evidence required

- Each statement quoted before and after.
- Your (a)/(b) determination for 002, with the carve-out test's behavior as evidence.
- `python -m pytest -q tests/test_episode_observations.py` green.
- Full clean-env suite: **0 failed.** Expect ~3031 passed / 6 skipped.
- Commit and push to `fix/launcher-hygiene` so #591's CI re-runs.

## Two Windows CI failures you should NOT try to fix

#591's CI shows 93 failures against main's 89. Two are the episode guard (yours). The other two are your
predecessor's new tests, `TestSpineTerminalThroughArchiveRelocation::*`, failing with
`SpineLifecycleError: … Author identity unknown` — git has no `user.name`/`user.email` on the Windows
runner. That is the **same pre-existing environmental cause** that already fails several `close_work`
tests on main, and the merge gate compares by cause, not test name. **They are not a regression and not
in scope.** Do not add git-identity setup to the tests or the workflow.

## Stop Conditions

- `spine_status` does not resolve to `lh-episode-rewording`.
- Green would require the exception list, deleting a record, or touching the guard.
- Rewording would cost substance a reader needs.
- The suite shows any failure other than the two Windows-only ones named above.

## Return Shape

What `spine_status` resolved to, named explicitly; the three statements before and after; your (a)/(b)
finding on 002; the clean-env suite summary line; the commit SHA; and confirmation you pushed to
`fix/launcher-hygiene` with #591 open and unmerged.

**You are fenced from merging.** The Admiral merges.
