# Successor note — w5-gates, written by `commander-w5-gates-f`

**The run is done except for three mechanical steps.** No open questions, no unrepaired findings, no blocked work. I tripped HARD at 15% on the spine checklist — my own reading, gauge observed `2026-08-09T04:48:57Z` at `0.150988`, not an inherited one. Everything below is measured, not remembered.

## What is already closed

- **`execute.json`: DONE, no open items.** All four gates closed with integrated evidence. Lease released.
- **Spine: `init` → `context` → `understand` → `plan` → `execute` → `reconcile` → `triage` → `review` all complete.**
- Remaining: **`feedback`**, then **`archive`**, then **open the PR**.

## Do these three things

### 1. `feedback` — record workflow feedback
Nothing is pending here; it is a fresh step. The material worth recording is in this run's discrepancies `D2`, `D3`, `D4` in `REPLAN_INPUT.json`, plus the operational traps in `crew-handoffs/g4-review-HANDOFF.md` §"Operational facts".

### 2. `archive` — commit and push
Commit message is written at `.agent-work/w5-gates/closeout/COMMIT_MSG.txt`. Use it as-is or amend.

- **`git status` must show production paths CLEAN.** The reviewer left the tree as found; I have touched no production file. Only `.agent-work/` should be dirty.
- **Two files under `.agent-work/epic-418-redux/transitions/close-to-w5/` show `M` with EMPTY diffs** — a CRLF stat artifact. **Leave them unstaged.** They are the Admiral's.
- The remote branch `epic-418/w5-bookend-gates` exists but still points at the fork point `aa2038d9`. **Your push carries all eight production commits.**

### 3. Open the PR
**Body is written and complete at `.agent-work/w5-gates/closeout/PR_BODY.md`** with every number already filled in from real measurements. Use it verbatim:

```bash
gh pr create --base main --head epic-418/w5-bookend-gates \
  --title "fix(#418 w5): make the gates at both ends of a run closable" \
  --body-file .agent-work/w5-gates/closeout/PR_BODY.md
```

**The six `Closes` lines are each on their own line — keep it that way.** `Closes #A, #B` closes only `#A`; GitHub honours the first issue in a comma-list. That already left #411 open on another PR in this same wave.

## The numbers, all measured

| | passed | skipped | subtests | collected | exit |
|---|---|---|---|---|---|
| fork point `aa2038d9` | 1867 | 2 | 829 | 1869 | 0 |
| **this branch** | **1891** | **2** | **872** | **1893** | **0** |
| `main` (Admiral's figure) | 1896 | 2 | 829 | 1898 | 0 |

Delta **+24 passed, +43 subtests**, 0 removed, skips unchanged. **Expected merged collect = 1898 + (1893 − 1869) = 1922.** The full suite was measured three times independently — the g4 reviewer, me, and the engine as gate check `g4-integrate.c1` — and agreed exactly each time (473.71s on my run).

## Standing traps — each already cost this epic real time

1. **`python`, NEVER `py`.** Different interpreters; `py` has no pytest and `py -m pytest` exits nonzero, reading exactly like a red suite when nothing ran.
2. **Never pipe a test command into `tail`/`head`** — `$?` becomes the pipe's, and a zero-match `-k` selector exits **5** but reads as 0. Use `cmd > file 2>&1; echo "REAL_EXIT=$?"`.
3. **This repo is CRLF.** A mutation probe with an LF literal silently matches nothing and certifies a no-op.
4. **The gauge is per checklist DIRECTORY, not per agent** (issue #477). Your first reading is *mine*. Make one tool call, then re-read before believing any number.
5. The engine wants `--session-id` on every verb once a lease is claimed, and `claim --force` requires `--reason`.

## What I would want adjudicated by the Admiral

1. **`gh issue create` authority — fifth recurrence.** The latitude contract delegates issue *filing* as a class but leaves the *tool* at `pre-clear`. I filed nothing and routed all 14 triage candidates as `recommend-and-defer`, with an issue-ready list at `.agent-work/w5-gates/TRIAGE_RECOMMENDATIONS.md` and a suggested split. Do not file them yourself without a ruling.
2. **`tc9`** — both #439 and #484 suggest a replacement command that exits 0 on all four PR states, i.e. a check that cannot fail. Worth annotating on the issues so it is not copied forward.
3. **`tc10`** — the Admiral spine template still calls `repair` an enforced exit. Deliberately not edited: cross-crew merge hazard.
4. **`D4` / #477** — the gauge-inheritance loop consumed real crew launches in this wave while looking exactly like correct doctrine.

## One correction I made, so you do not re-find it

`g4-implement-RESULT.md` claimed only the doctrine test file differs from the fork point outside `.agent-work/`. **Three production paths do** — `verify_iterative_role_artifacts.py`, `COMMANDER_SPINE.template.json`, and the test file. True against the g4 baseline `84d1e998`, false against the fork point. Found by the g4 reviewer, re-derived by me with `git diff --numstat`, corrected in place with provenance marked. **The +24 conclusion is unaffected** — only the test file carries tests.

---

# ADDENDUM 2 — Admiral ruling executed; ONE step left

**PR #516 IS OPEN.** https://github.com/fredcai6/constellation-skills/pull/516
Branch pushed: `origin/epic-418/w5-bookend-gates` moved `aa2038d9..34e97f46`.
Verified on the forge, not asserted: `gh pr view 516 --json closingIssuesReferences` returns
**[439, 446, 468, 484, 501, 506]** — all six linked, so the one-`Closes`-per-line format took.

Spine steps `review` and `feedback`'s WORK are done. Five episodes recorded
(`w5-gates-001..005`), capture gate `verify_episode_captured.py` exits **0**.

## The only thing left: close `feedback`, then WAIVE `archive.c2b`

I hit the hard context limit and the engine refused to BEGIN `feedback`, so both it and
`archive` are still `pending`. Nothing is unfinished except the recording.

**The Admiral has RULED that `archive.c2b` is waived.** Do not try to make it pass. Do not
hand-edit `spine.json`. Do not substitute the branch name. The `waive` verb is the sanctioned path.

### Why c2b cannot pass (the Admiral's own inspection, reproduce it, don't trust it)

The spine was instantiated before g3 landed, so `archive.c2b` still holds the **pre-fix** text:

```
gh pr list --head <branch> --state open --json number --jq 'length > 0'
```

Two defects, both documented by this very wave:
1. `<branch>` is unsubstituted, and the engine runs check text through `sh -c`, where an
   unquoted `<` is **input redirection** — `sh` tries to open a file named `branch`, exits 1,
   `gh` is never invoked. **Always red, in every state of the world.**
2. Even if it ran, `--jq 'length > 0'` prints `false` and **exits 0**, and the engine's verdict
   is returncode-only — so the "fixed" form would be a check that cannot FAIL.

### The waiver must carry all four of these

1. **Authority names `Admiral, epic-418-redux`** and cites **#439 / #484 / #446** as the defect
   that forced it.
2. **Reason carries the command text verbatim** and the measured exit code — not a paraphrase.
3. **Nothing may state or imply c2b PASSED.** It did not. It cannot.
4. The waiver is **evidence-only**: it records a defective check. It does not assert the work is
   unreachable-but-fine.

The Admiral verifies PR #516 on the forge himself before merge. **The waiver covers the broken
check, not the requirement — if the PR were not actually open, the waiver would be void.** It is
open; the link above is live.

### Numbers for the merge check

The Admiral will verify the merged total against **1898 + 24 = 1922 collected (1920 passed, 2
skipped)**. He has the base pinned independently at `ea854471` = 1869 collected, and the g4
reviewer measured `aa2038d9` = 1867 passed + 2 skipped — the same number from two directions.

### Already done, do not redo

The g4 implementer RESULT's false premise is **corrected**. I caught the reviewer's float earlier
in my run, re-derived with `git diff --numstat aa2038d9 764a2728 -- . ':(exclude).agent-work/**'`
(three paths: `verify_iterative_role_artifacts.py` 143/22, `COMMANDER_SPINE.template.json` 1/1,
the test file 1370/2) and fixed the sentence in place with provenance marked.
