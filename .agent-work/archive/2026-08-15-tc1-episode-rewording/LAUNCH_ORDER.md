# Launch Order: `tc1-episode-rewording` — two episode statements read as instructions

**Issued:** 2026-08-15 by `admiral-post-568` · **Model:** sonnet · **Frozen.**
Read it as written. Where it is wrong, **say so and float rather than quietly working around it.**

Small and precisely scoped. PR #588 is otherwise ready to merge and is blocked only by this.

## Mission

The lane before you (`tc1-windows-path-form`) wrote three episode records on this branch. Two of them
trip the episode-observation guard, so the full suite reds at **2 failed** where it must read **0**:

```
FAILED tests/test_episode_observations.py::RealStoreTests::test_the_real_store_is_clean_under_strict
FAILED tests/test_episode_observations.py::RealStoreTests::test_the_real_store_scan_actually_examined_the_records

OFFENDER tc1-windows-path-form-002 a5 (workaround) imperative: 'Read'
OFFENDER tc1-windows-path-form-002 a5 (workaround) imperative: 'keep'
OFFENDER tc1-windows-path-form-003 a5 (workaround) imperative: 'pass'
```

The two statements, verbatim:

- **`episodes/active/tc1-windows-path-form-002.md:49`**
  > Read the verifier source (not just the template) to get the exact required/optional field split,
  > then keep the template's structural shape and substitute real run content -- rather than guessing at
  > which template fields could be dropped.

- **`episodes/active/tc1-windows-path-form-003.md:47`**
  > Always pass --why with a genuine one-line understanding statement on every advance call for a
  > non-exempt gate, rather than waiting for the refusal to name it.

Both are written as **advice to a future reader**. The guard exists because
`tests/test_episode_observations.py:2` states the store's purpose: *"records reading as observations
rather than instructions (issue #460)."* An episode is a record of what happened on one run, not a rule
for the next one.

## What to do

**Reword both statements as records of what this run actually did and found.** Past tense, describing
the run, not addressing a reader. The substance must survive — you are changing voice, not content. A
future reader should still learn the same thing, as a fact about a run rather than as an order.

Rough shape, not wording to copy:

- `-002`: the run read the verifier source rather than only the template; that is what exposed the exact
  required/optional field split, and preserving the template's structural shape while substituting real
  run content worked where guessing at droppable fields had not.
- `-003`: advance calls on non-exempt gates refused until `--why` carried a genuine one-line
  understanding statement; supplying it upfront avoided the refusal round-trip.

Write them in your own words from the records' surrounding context, which carries what actually happened.
**Read each file in full before editing** — the other fields say what the run observed, and a restatement
that contradicts them is worse than the imperative you replaced.

## The escape hatch you must NOT take

There is an **exception list**, and it currently carries 11 entries. **Do not add yourself to it.**
Those are grandfathered records; the list is not a way to make new writing pass. If you conclude a
statement genuinely cannot be expressed as an observation, **stop and report** — that is a finding about
the guard, not a reason to bypass it.

Do not delete the records either. They are real run history and their content is worth keeping.

## `apply_episode_delta.py` is the only write path

The episode store has one writer. **Do not hand-edit the markdown** unless you establish that the
delta tool cannot express a restatement, and say so explicitly if you find that. Check first:
`python scripts/apply_episode_delta.py --help`.

## Pre-Rulings — settled

1. **`decision:reword-not-except` — settled/human.** Restate as observations. The exception list is not
   available to this lane.
2. **`decision:content-survives` — settled.** Voice changes; substance does not. A reader must still
   learn the same thing.
3. **`decision:clear-caches-before-measuring` — settled.**

## File Ownership

**Yours:** `episodes/active/tc1-windows-path-form-002.md`, `episodes/active/tc1-windows-path-form-003.md`,
and your work area.

**NOT yours:** `tests/test_episode_observations.py` and its exception list — the guard is correct and is
doing its job. `scripts/checklist_engine.py`, `tests/test_spine_origin_isolation.py` (#588's actual
content, already correct and pushed), `scripts/hooks/spine_rail.py` (#589 open), `scripts/run_crew.py`,
`.mcp.json`. The four `tc1-worktree-identity-00*.md` episodes pass the guard — leave them.

## The MCP door

`spine_status` **must** describe `tc1-episode-rewording`. If it resolves to anything else — especially a
`f-424` demo spine — stop and report.

## Workspace

Worktree `/home/tommy/projects/constellation-skills/.worktrees/tc1-worktree-identity`, **branch
`tc1/worktree-identity` — the existing PR #588 branch.** Commit there and push; do not branch away and do
not open a second PR. Work area `.agent-work/tc1-episode-rewording/`.

Two archived work areas sit alongside yours. **Leave them.**

## A note on your own episodes

You will write episode records of your own at closeout. **They are subject to the same guard.** Write
them as observations the first time — this lane exists because the previous one did not, and a second
round of the same failure would be an unusually pointed irony.

## Evidence required

- Both statements rewritten, quoted before and after in your report.
- `python -m pytest -q tests/test_episode_observations.py` green.
- Full Linux suite, cache-clean. Clear first:
  `find . -name __pycache__ -type d -not -path './.git/*' -prune -exec rm -rf {} +`
  **Target: 3010 passed, 6 skipped, 0 failed, 1136 subtests** from inside this worktree.
  **Run it with `env -u SPINE_FILE -u SPINE_SESSION -u SPINE_PARENT`** — your own spine lease exports
  those three vars and `tests/test_mcp_identity.py:600` asserts they are absent, which produces a false
  failure unrelated to your change. This bit two lanes today; it is a known defect, already filed.
- Commit and push to `tc1/worktree-identity` so #588's CI re-runs.

## Budget

Two statements. If this grows, stop and report.

## Stop Conditions

- `spine_status` does not resolve to `tc1-episode-rewording`.
- A statement cannot be expressed as an observation without losing its substance.
- Green would require the exception list, deleting a record, or touching the guard.
- The suite does not reach 3010 / 6 / 0 / 1136 in a clean env.

## Return Shape

What `spine_status` resolved to, named explicitly; both statements before and after; the episode-guard
result; cache-clean clean-env suite counts; the commit SHA; and confirmation you pushed to
`tc1/worktree-identity`.

**You are fenced from merging.** The Admiral merges. Say plainly that the push is done and #588 is still
unmerged.
