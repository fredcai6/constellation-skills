# Implementer Handoff — batch A + B

Eight bounded changes across three files. Each has an exact site and an exact
reason. Do these and nothing else; anything you discover beyond them is a
float-up, not a fix-now.

## Standing criterion

There are no bad actors. The only adversary is an honest agent about to make a
mistake. **Ease of use is the success criterion** — if the tools get harder to
use, the change failed. Added machinery is a cost.

## Why this batch exists

`_is_stale` exists, works, and is called in four places — none of them a
rendering path. So `current` on a plan whose owner died 22 days ago prints
`LEASE active` and `RAIL: ... you are 7 steps from done. Next: ... Run it.`
All 58 active leases in this checkout are stale. The system does not fail to
warn an honest agent; it instructs one into the mistake.

Measured cost: stale leases have been reclaimed **0 times by plain `claim` and
25 times by `--force`** in this repository's history.

---

## A — display and message

### A1. Remove `"current"` from `RAIL_VERBS`
`scripts/checklist_engine.py:457`. The set is
`{"claim","current","start","advance","attest","attach"}`. `current` is the only
railed verb a non-owner routinely calls; the other five are things you call
*after* deciding the plan is yours. Removing it is what stops a dead plan saying
*Run it.*

**Leave the five `_RAIL_STRINGS` byte-identical** — they are frozen as a
measurement precondition for #145. You are removing a verb from a set, not
editing a string.

Update the pinned `test_rail_verbs_set_is_exact` to match, and say in the commit
why the set shrank.

### A2. Archive banner and rail suppression
A plan under `.agent-work/archive/` is finished by definition. Print an
`ARCHIVED` banner and suppress the rail entirely. This is a **path fact** — it
makes no liveness claim, so it cannot be wrong about liveness.

### A3. `HELD`, not `active`
The lease line asserts `active` for leases that are 22 days dead. Render `HELD`
plus the age. **Render age, never a verdict** — pid corroboration is missing for
55 of 57 stale leases, so a STALE/LIVE verdict is not supportable from the data.
A Commander thinking hard for 31 minutes must not render as abandoned.

### A4. `next (for the holder):`
When the plan is held by a session that is not the caller, the `next:` line is
addressed to the wrong reader. Relabel it so a non-owner is not handed an
instruction meant for someone else.

### A5. Staleness in `_scan_active_spine`
`scripts/hooks/spine_rail.py`. `decide_session_start` injects *"Pick the run back
up at this gate and drive it through the engine"* as SessionStart context, and
its fallback selects spines on "an active lease and a non-None active id" with
**no staleness check anywhere in the path**. This is the worst surface of the
four because it is unasked — the agent need not open anything.

Gate the injection on staleness. This is the one item I would not defer.

### A6. Rewrite `require_session`'s refusal text
`scripts/checklist_engine.py:1148-1152`. It currently tells the caller to
*"pass `--session-id <the holder's>` or take over with `claim --force --reason`"*
— and **both recommended remedies are filed defects**, #632 and #369
respectively. The engine's own error message routes users into two known bugs.

A refusal should teach the correct next action. Write one that does.

---

## B — two narrow behavior fixes

### B1. Exempt `waive` from the session gate
This is what forces the five-step handshake (release → claim → waive → release →
reclaim). `waive` is in `MUTATING_VERBS` (`:74`), and `require_session` gates on
that set (`:1136`), so a parent waiving a child's condition is refused while the
child holds a fresh lease.

**Do NOT achieve this by removing `waive` from `MUTATING_VERBS`.** Line 3788
reads that same set to decide journaling, so the naive edit silently deletes the
waiver audit trail. Exempt it at the session gate specifically, and add a test
proving the waiver is still journaled.

The `PreToolUse` self-waive denial in `run_crew.py` implements a verbatim human
ruling ("agent cannot waive itself; commander waives crew, admiral waives
commander") and must keep working unchanged. Prove that too.

### B2. Make `--parent` required
`scripts/run_crew.py`. `crew-runs.json:parent` is already read and gate-enforced
by `verify_declared_dispatch.py`, and it is populated on only 172 of 545
entries. Remove the optionality rather than adding a second lineage edge
elsewhere.

Existing callers that omit it must fail with a message that says what to pass.
Check the test suite and any in-repo callers before you decide the shape.

---

## Evidence required

- The full ordinary suite: `python -m pytest -q`. Baseline at `efe92791` is
  **3447 passed, 6 skipped, 1222 subtests**. Report exact counts; no regressions.
- A focused regression per item, proving both the new behavior and that the
  thing you did not intend to change did not change.
- For A2/A3/A4: show the actual rendered output before and after, against a real
  archived plan. Copy it to scratch; **never mutate a plan another run owns.**
- For B1: prove the waiver is still journaled and self-waive is still denied.
- `git diff --check` must exit 0. This epic already lost one review to trailing
  whitespace in a committed evidence file.

## Scope fence

Allowed: `scripts/checklist_engine.py`, `scripts/hooks/spine_rail.py`,
`scripts/run_crew.py`, their tests, and your own evidence under
`.agent-work/20260821-ab/`.

Excluded: option C or any lease demotion — retired as dominated; the R9/R10
leaseless hole — deliberately not in this batch; `map/`; `docs/architecture`;
GitHub; merge to `main`. **Do not touch `skills/charter/*`,
`skills/_shared/global-everyone.md`, or `tests/data/store_mentions.approved.txt`
in the main checkout — that is the human's own in-progress work.**

## Workspace

- Worktree `/tmp/constellation-20260821-ab`, branch `afk/20260821-ab`, base `efe92791`
- Commit in logical units, not one lump. A and B are separable and should be separable in history.
- Do not push. Do not open a PR. Do not call any `mcp__spine__*` tool — the door
  is bound to the Admiral's epic spine.

## Result

Write `.agent-work/20260821-ab/crew-handoffs/ab-implementer-result.md`: what
changed per item, exact commands and outputs, before/after renders, what you
chose where the handoff left latitude, and anything you found and did not fix.
