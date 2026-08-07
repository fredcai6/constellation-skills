# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these five lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch (the PID changes every time).

- **step:** execute · item `g0-review` — **in-progress, postcondition c1
  attested.** The review returned **BLOCK** on two blockers; **BOTH ARE NOW
  FIXED AND INDEPENDENTLY VERIFIED** (`e-g0-review-4`, commits `b14ff3ff` +
  `a42fbf6c`). Tommy ruled B1 himself: *"strip the line numbers"*
  (`e-g0-review-3`). **THE ONLY THING LEFT AT THIS GATE IS A FOCUSED RE-REVIEW
  OF THE DELTA** — `git diff b14ff3ff~1..HEAD -- scripts/ tests/`, 2 files,
  +191. Scope it to: are B1 and B2 actually closed, did anything regress, and is
  there a third sibling of the same defect shape. **Do the re-review — do not
  skip it.** The original reviewer found a blocker that three implementer passes
  AND my own re-verification all walked past, so self-verification is
  demonstrably insufficient here. Then `advance g0-review` → `g0-integrate`.
  11 gates: g0 g1 g2 g3 g4 g5 gb g6 g7 g8 gs
- **slug:** work-id `issue-456` · branch `issue-456/code-map` (pushed to origin)
  · worktree `C:/Programs/constellation-skills/.claude/worktrees/issue-456`
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-456/spine.json current` — then re-claim lease `commander-issue-456` idempotently (same id, NOT a takeover), read the DIGEST, and drive `.agent-work/issue-456/execute.json` from `current`. Before any crew: `python scripts/recover_crews.py issue-456`, then dispatch only via `python scripts/run_crew.py --dispatch external --verify-result`.
- **pid:** none — the g0 reviewer is an Agent-tool subagent (`g0-reviewer`), not
  an OS process. Registry entry: `constellation/issue-456/g0/reviewer/attempt-1`.
  Recover with `python scripts/recover_crews.py issue-456`; a `resumable` crew is
  resumed in place via `SendMessage` to its agent id, a `needs-abandon` one via
  `run_crew.py --abandon <session> --relaunch`. The three implementer attempts
  are all resolved (1 and 2 ABANDONED after clean context-trip handoffs, 3
  COMPLETE) — do not rerun them.
- **expected artifact:** immediate — `.agent-work/issue-456/crew-handoffs/g0-review-RESULT.md`. Final — `.agent-work/issue-456/execute.json` with all 34 items `complete`, and each gate's `IMPLEMENTER_RESULT`/`REVIEW_RESULT` under `.agent-work/issue-456/crew-handoffs/`

**Baseline:** `1688 / 2 / 0` before `g0`; `1706 / 2 / 0` after the g0 build;
**`1709 passed, 2 skipped, 0 failed` after the remediation**, reproduced
independently by the Commander in a cleared environment. Any red below that line
is this run's doing.

**THREE environment traps — all three confirmed real on this run.** Clear
`FORCE_COLOR` and `PYTHONIOENCODING` before trusting any suite number (`tc3`,
`tc7`), and **use `python`, never `py`** (`tc19`) — `py` has no pytest, so
`py -m pytest` dies with "No module named pytest" and reads as a silently green
run. That third one is the dangerous one: it already reached three command
postconditions in a crew's own plan before being caught.

**Registry caveat (`tc22`):** a relaunched crew reuses an abandoned attempt
number and then **cannot be result-verified** — `--verify-result` refuses with
"cannot verify an abandoned crew". Verify such a crew by reading its result
artifact and reproducing its evidence by hand, as I did for the remediation pass.

**Authority reminder for a fresh agent:** push and a full non-draft PR are
PRE-APPROVED for this work. **Merge to `main` is NOT approved.** Never
force-push. `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are
read-only corpora. Do **not** `git add -A` in this worktree — the untracked
3,635-page `map/` tree is staged at `gs`, deliberately last; stage explicit paths.

_Updated: 2026-08-07T22:12:00Z_
