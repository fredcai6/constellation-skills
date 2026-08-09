# State note — for the crew-1 successor (`commander-w5-gates-f`)

Written by `commander-w5-gates-e` on tripping HARD at `g4-review`. Reset for relaunch.

## Where the run is

**Three of four gates are CLOSED and need no revisiting.** g4 is half done: its implementation is
landed, committed and verified; only its review and integrate remain.

| gate | state |
|---|---|
| g1 (#501 + #468) | **closed**, APPROVE, 0 findings |
| g2 (#506) | **closed**, BLOCK → rework `bd56ac8a` → re-verified APPROVE |
| g3 (#439 + #484 + #446) | **closed**, BLOCK → rework `84d1e998` → re-verified APPROVE |
| g4-implement | **closed** at `764a2728` |
| **g4-review** | **ACTIVE, p1 attested, not started** — this is your first act |
| g4-integrate | pending |

## Your first command

```
cd C:/Programs/constellation-skills-wt/epic418-w5-gates
python C:/Programs/constellation-skills/scripts/checklist_engine.py --file C:/Programs/constellation-skills-wt/epic418-w5-gates/.agent-work/w5-gates/execute.json current
```

Claim the lease with a **new session id**. Mine was `commander-w5-gates-e-20260808` and I released it,
so `--force` should not be needed. **Use `execute.json`, never `spine.json`** — the spine's digest is
stale by construction.

## g4-review needs no preparation — dispatch and go

- **The REVIEWER_HANDOFF is written in full**:
  `.agent-work/w5-gates/crew-handoffs/g4-review-HANDOFF.md`. It names the target commit
  (`git diff 84d1e998 764a2728 -- tests/test_iterative_planning_doctrine.py`), the two required
  confirmations, the six broken-input mutations the reviewer must build itself, the three claims to
  check hardest, selector hygiene, and the scope. You should not need to rewrite it.
- **No reviewer is running.** I registered `constellation/w5-gates/g4/reviewer/attempt-1` and then
  **abandoned it without dispatching**, so you register a fresh attempt with no duplicate-guard
  conflict. Register with `--backend external`, then dispatch the Agent out-of-band, then
  `--verify-result`. That is the pattern every gate in this run used.
- `p1` is already attested. `start g4-review` is your next engine verb after claiming.

## g4-integrate — three of its four inputs are already measured

Its imperative says to run both verification commands yourself. Two of them I have already run at
this exact tree, so you are confirming, not discovering:

- **c2, the run's own closure check** — I ran it: exit 0,
  `iterative role artifact ok: commander (w5-gates)`.
  `python scripts/verify_iterative_role_artifacts.py commander --work-id w5-gates --skills-root C:/Users/fredc/.claude/skills`
  **This is finding 2 discharged live** — before fix B it could not pass from this worktree.
  Keep `--skills-root`: without it the check validates against whatever is installed on this machine
  rather than the branch under review.
- **c1, the full suite** — `python -m pytest -q`. **The one command I never ran myself.** The
  implementer measured **1891 passed, 2 skipped, exit 0** in 497s. Budget 8–16 minutes.
- **c3** is the reviewer's APPROVE artifact.

**Do not forget the triage routing.** g4-integrate's imperative requires that, BEFORE advancing, you
route this run's three deferred findings to the spine's triage step by name:
1. boundary freshness — recommend-and-defer, with the falsification;
2. finding 1 — both issues' suggested archive fix would create a check that cannot fail;
3. after fix A, `ADMIRAL_SPINE.template.json`'s execute prose and its `directives.decisions` block
   still describe `repair` as an enforced exit — not this run's file.

The plan critic triage also names two more corpus-level candidates worth routing:
`implementer-result` conditions carry no `match` (shipped template defect), and `config_ref` points
at `docs/agents/engine-config.json`, which does not exist.

## Things established by measurement — do not re-derive or contradict these

1. **`archive.c2b` did not fail the way #439/#484/#446 describe.** The engine runs check text through
   `sh -c`, where the unquoted `<` in `--head <branch>` is an **input redirection** — `gh` was never
   invoked. Measured: the old text exits **1 in all four PR states**. It was an *always-fails* check,
   so "accepts only an OPEN PR" was never a true description of shipped behaviour. **All three issue
   bodies are wrong about this**, and the correction is in the commit message, in `REPLAN_INPUT.json`
   as observed evidence, and belongs in the PR body.
2. **The fix those issues suggest is worse.** The engine's verdict is **returncode-only** and stdout
   is discarded. #484's form measured **exit 0 in all four states** — it converts a check that cannot
   pass into one that cannot fail. The count is compared in the shell instead.
3. **#446 is a separate defect**, fixed as the second defect of the same postcondition under
   pre-ruling 5, not collapsed into #439/#484.
4. **The `-k` selectors are the cold critic's BLOCK remedy and are load-bearing.** A zero-match
   selector exits **5** and fails a gate closed. Do not loosen, rename or broaden them. I verified
   after g4 that all six still collect exactly their pre-g4 counts: `guard_location` 11/11 subtests,
   `guard_mutation` 1/6, `stop_boundary` 2, `stop_mutation` 1/8, `archive_c2b` 4/4,
   `archive_mutation` 2/11.

## Operational facts — each has cost this run real time

1. **`python`, never `py`** — different interpreters; `py` has no pytest, so `py -m pytest` reads
   exactly like a red suite when the tests never ran. `references/windows.md` §4 says the opposite
   and is wrong on this box; three crews have now hit it.
2. **Never pipe a test command into `tail`/`head`** — `$?` becomes the pipe's status, and a
   zero-match selector's real answer is **5**.
3. **Subagents cannot spawn *named* teammates** — drop the `name` parameter. Crew dispatch is
   synchronous and blocks your turn; that is expected.
4. **Engine args are shell-expanded** — `$(...)` in a `--why` or `--field` gets command-substituted
   and mangles the record. Use a heredoc for anything with shell metacharacters.
5. **This host is CRLF, and there are two traps.** A mutation can silently fail to *apply* if your
   literal is LF; and a restore can silently fail to *restore*, because `read_text()` +
   `write_text(newline="")` converts CRLF to LF and `read_text() == read_text()` cannot detect it.
   **Verify restores with `read_bytes()` and check `git status` after mutating.**
6. Leave `.agent-work/epic-418-redux/transitions/**` unstaged — the Admiral's; their `M` status is a
   CRLF stat artifact with empty diffs.

## One record correction already applied — do not redo it

The g2 APPROVE was recorded against `bd56ac8a`, and `4b8abc12` landed after it. The Admiral ruled:
**attach a note, do not spend a re-review cycle.** The ruling reached me after `g2-integrate` had
already advanced, so it is a record correction rather than a pre-advance step — the gate closed
without it and does not close on it.

Two notes are attached to `g2-integrate` (`e-g2-integrate-6`, `e-g2-integrate-7`). I verified the
ruling's safety claims rather than relaying them: only the test file moved after the APPROVE
(23/12, no production file), and the `finally` block both restores pristine and asserts the renderer
is clean, so the change is self-checking.

**One thing I found that sharpens it:** the old code restored `pristine` at the head of the *next*
iteration, so the **last** mutation was never undone — the mutated renderer survived the test, and
the new comment names the risk that a later refusal test in the class could have been contaminated.
`4b8abc12` was therefore not a tidy; it closed a real leak that could have made a later refusal test
pass for the wrong reason. That raises the value of the note and does not disturb the ruling.

**The same shape is worth one check at `g4-integrate`:** make sure the g4 APPROVE you record names
the commit it actually judged, and that nothing lands after it. It is the defect the Admiral caught
twice tonight on PRs #509 and #513.

## Two process findings worth carrying up with the PR

- **The engine's journal does not preserve a superseded result.** It records *that* a `record` verb
  ran, with a hash chain, but not the result value or finding text. A gate that BLOCKs and is then
  repaired leaves **no machine-readable trace it ever failed** — the record would show a clean
  APPROVE with 0 findings. Both g2 and g3 blocked; both survive only because the reviewers were told
  to preserve pass-1 findings in their result files. Recommend the journal carry `result` and
  `finding` on `record`.
- **`reopen` refuses on a `survey`** ("reopen applies to gated checklists"), so a survey check that
  fails and is then repaired cannot be formally reopened.

## Commits on this branch, in order

`c63c2bb0`, `6f48ece4` (g1) · `57048457`, `bd56ac8a`, `4b8abc12` (g2) · `ff43e883`, `84d1e998` (g3) ·
`764a2728` (g4-implement), plus Commander work-area commits in between.

**You are the last crew running.** #514 is green and held behind this branch by the Admiral's
merge-order ruling. Your PR triggers the epic's close sequence.
