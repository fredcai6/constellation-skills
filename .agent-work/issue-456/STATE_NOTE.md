# Crash-resume state note — issue-456

If this session dies, a fresh agent resumes from exactly these five lines — no
forensics. Rewritten before entering `execute` and again before **each** crew
dispatch (the PID changes every time).

- **step:** execute · item `g0-integrate` — **in-progress.** `g0-implement` and
  `g0-review` are both **complete**. All three review findings (B1, B2, B3) are
  closed and independently verified; do **not** reopen them and do **not**
  re-dispatch any g0 implementer or remediation crew — all six prior crews are
  terminal (`recover_crews` reports 0 unresolved).

  `g0-integrate` has two postconditions:
  - **c1 (command) — ALREADY PASSING, verified by the Commander in a cleared
    environment on this run:** full suite `1709 passed / 2 skipped / 0 failed`,
    and `tests/test_code_map.py -k "discovery or cli"` `14 passed`. It is a
    command-kind check, so it is satisfied by `advance` re-running it, never by
    `attest`.
  - **c2 (artifact) — THE ONLY THING OUTSTANDING:** it requires an evidence
    artifact of type `review-result` whose verdict is **APPROVE**. Both reviews
    on record returned **BLOCK**, and the B3 fix (the docstring at
    `tests/test_code_map.py:127`) was the **Commander's own edit, reviewed by
    nobody**. A third scoped reviewer pass is dispatched to close it:
    handoff `crew-handoffs/g0-approve.md`, slot
    `constellation/issue-456/g0/reviewer/attempt-3`, result expected at
    `crew-handoffs/g0-approve-RESULT.md`.

  If that pass returns APPROVE: attach it as `review-result` with
  `--field verdict=APPROVE`, then `advance g0-integrate`. If it returns BLOCK:
  fix the finding at `g0` and re-review — do not attest around c2.

  **Do NOT add the `pages - 1 - modules` vs `entity_pages` invariant to `g0`.**
  It is the real falsifiable check, it would be RED today (the page genuinely is
  lost and `g2` owns the rename), and it belongs to `g1` with `tc17`. `tc24`
  corrects the misdirection in `tc18` — the root is `sizes`, which feeds three
  fields, and counting the tree again is NOT the fix.

  11 gates: g0 g1 g2 g3 g4 g5 gb g6 g7 g8 gs
- **slug:** work-id `issue-456` · branch `issue-456/code-map` (pushed to origin)
  · worktree `C:/Programs/constellation-skills/.claude/worktrees/issue-456`
- **next command:** `python C:/Users/fredc/.claude/skills/constellation-commander/scripts/checklist_engine.py --file .agent-work/issue-456/spine.json current` — then re-claim lease `commander-issue-456` idempotently (same id, NOT a takeover, no `--force`), read the DIGEST, and drive `.agent-work/issue-456/execute.json` from `current`. Before any crew: `python scripts/recover_crews.py issue-456`, then dispatch only via `python scripts/run_crew.py --dispatch external --verify-result`.
- **pid:** none — the g0 approve-reviewer is an Agent-tool subagent, not an OS
  process. Registry entry:
  `constellation/issue-456/g0/reviewer/attempt-3`. Recover with
  `python scripts/recover_crews.py issue-456`; a `resumable` crew is resumed in
  place via `SendMessage` to its agent id, a `needs-abandon` one via
  `run_crew.py --abandon <session> --relaunch`.
- **expected artifact:** immediate — `.agent-work/issue-456/crew-handoffs/g0-approve-RESULT.md`. Final — `.agent-work/issue-456/execute.json` with all 34 items `complete`, and each gate's `IMPLEMENTER_RESULT`/`REVIEW_RESULT` under `.agent-work/issue-456/crew-handoffs/`

**Baseline:** `1688 / 2 / 0` before `g0`; `1706 / 2 / 0` after the g0 build;
**`1709 passed, 2 skipped, 0 failed` after the remediation**, reproduced
independently by the Commander in a cleared environment twice. Any red below
that line is this run's doing.

**STANDING LESSON, earned at `g0` and binding for the remaining ten gates:**
reproducing a falsifier that a crew designed only proves *that crew's probe*
works. A check claimed to be falsifiable must be attacked with a mutation its
author did **NOT** choose. The Commander missed this twice at `g0`; the
re-reviewer caught it with N4/N5/N8.

**THREE environment traps — all three confirmed real on this run.** Clear
`FORCE_COLOR` and `PYTHONIOENCODING` before trusting any suite number (`tc3`,
`tc7`), and **use `python`, never `py`** (`tc19`) — `py` has no pytest, so
`py -m pytest` dies with "No module named pytest" and reads as a silently green
run. That third one is the dangerous one: it already reached three command
postconditions in a crew's own plan before being caught.

**Registry caveat (`tc22`, `tc25`):** a relaunched crew reuses an abandoned
attempt number and then **cannot be result-verified** — `--verify-result`
refuses with "cannot verify an abandoned crew". `crew-runs.json` also held four
entries under one id, and `--dispatch` refused a slot three times naming a
COMPLETE crew while `--abandon` reported success without clearing it. Verify
such a crew by reading its result artifact and reproducing its evidence by hand.

**Authority reminder for a fresh agent:** push and a full non-draft PR are
PRE-APPROVED for this work. **Merge to `main` is NOT approved.** Never
force-push. `C:/Programs/f1Brainz` and `C:/Programs/superCoolSpaceSim` are
read-only corpora. Do **not** `git add -A` in this worktree — the untracked
3,635-page `map/` tree is staged at `gs`, deliberately last; stage explicit paths.

_Updated: 2026-08-08T00:20:00Z_
